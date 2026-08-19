from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.models import Appointment, Clinic, Pet, User
from app.schemas.appointments import (
    AppointmentCreate,
    AppointmentStatus,
    AppointmentUpdate,
)
from app.services.slots import invalidate_slots

# Legal status transitions. Anything not listed here is rejected.
_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    AppointmentStatus.SCHEDULED.value: {
        AppointmentStatus.COMPLETED.value,
        AppointmentStatus.CANCELLED.value,
    },
    AppointmentStatus.COMPLETED.value: set(),
    AppointmentStatus.CANCELLED.value: set(),
}


def _has_overlap(
    db: Session,
    pet_id: int,
    start_time: datetime,
    end_time: datetime | None,
    exclude_appointment_id: int | None = None,
) -> bool:
    """Return True if the pet already has a scheduled appointment in this window.

    IMPORTANT: this is a check-then-act and is therefore racy. Two simultaneous
    requests can both pass this check and both insert, producing a double
    booking. Closing the race requires a database-level exclusion constraint
    (btree_gist on (pet_id, tsrange(start_time, end_time))). Until that exists,
    treat this as best-effort.
    """
    effective_end = end_time or start_time

    stmt = select(Appointment.id).where(
        Appointment.pet_id == pet_id,
        Appointment.status == AppointmentStatus.SCHEDULED.value,
        Appointment.start_time <= effective_end,
        func.coalesce(Appointment.end_time, Appointment.start_time) >= start_time,
    )
    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)

    return db.scalar(stmt) is not None


def get_appointment(
    db: Session, appointment_id: int, current_user: User
) -> Appointment:
    """Return the appointment if the current user owns its pet, else raise."""
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise NotFoundError("Appointment not found.", code="APPOINTMENT_NOT_FOUND")
    if appointment.pet.owner_id != current_user.id:
        raise ForbiddenError(
            "You do not have access to this appointment.",
            code="NOT_APPOINTMENT_OWNER",
        )
    return appointment


def get_all_appointment(
    db: Session, current_user: User, limit: int = 50, offset: int = 0
) -> list[Appointment]:
    """Return the current user's appointments, newest scheduled first."""
    stmt = (
        select(Appointment)
        .join(Pet)
        .where(Pet.owner_id == current_user.id)
        .order_by(Appointment.start_time)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


def get_all_clinic_appointment(
    db: Session,
    clinic_id: int,
    current_user: User,
    limit: int = 50,
    offset: int = 0,
) -> list[Appointment]:
    """Return upcoming scheduled appointments at a clinic the caller owns.

    IMPORTANT: this raises 403 rather than 404 when the caller is not the owner.
    That is the opposite of get_appointment above, and it is deliberate: clinics
    are publicly readable, so their existence is already known and a 403 leaks
    nothing. Appointments are private, so not-yours must be indistinguishable
    from not-found.
    """
    clinic = db.get(Clinic, clinic_id)
    if clinic is None:
        raise NotFoundError("Clinic not found.", code="CLINIC_NOT_FOUND")

    if clinic.owner_id != current_user.id:
        raise ForbiddenError(
            "Only the clinic owner can view this schedule.",
            code="NOT_CLINIC_OWNER",
        )

    stmt = (
        select(Appointment)
        .where(
            Appointment.clinic_id == clinic_id,
            Appointment.start_time >= func.now(),
            Appointment.status == AppointmentStatus.SCHEDULED.value,
        )
        .order_by(Appointment.start_time)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


def create_appointment(
    db: Session, data: AppointmentCreate, current_user: User
) -> Appointment:
    """Book an appointment for one of the current user's pets."""
    pet = db.get(Pet, data.pet_id)
    # 404 for missing, 403 for not-yours, per the ownership spec for booking.
    # Trade-off: 403 confirms the pet exists (existence disclosure) in exchange
    # for an explicit, testable authorization signal.
    if pet is None:
        raise NotFoundError("Pet not found.", code="PET_NOT_FOUND")
    if pet.owner_id != current_user.id:
        raise ForbiddenError("You do not own this pet.", code="NOT_PET_OWNER")

    clinic = db.get(Clinic, data.clinic_id)
    if clinic is None:
        raise NotFoundError("Clinic not found.", code="CLINIC_NOT_FOUND")

    if _has_overlap(db, data.pet_id, data.start_time, data.end_time):
        raise ConflictError(
            "This pet already has an appointment in that time window.",
            code="APPOINTMENT_OVERLAP",
        )

    appointment = Appointment(
        pet_id=data.pet_id,
        clinic_id=data.clinic_id,
        start_time=data.start_time,
        end_time=data.end_time,
        status=AppointmentStatus.SCHEDULED.value,
        notes=data.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # Booking removes a slot from that clinic's available list for that day.
    invalidate_slots(appointment.clinic_id, appointment.start_time.date())

    return appointment


def update_appointment(
    db: Session, appointment: Appointment, data: AppointmentUpdate
) -> Appointment:
    """Apply a partial update to a scheduled, future appointment."""
    if appointment.status != AppointmentStatus.SCHEDULED.value:
        raise ConflictError(
            "Only scheduled appointments can be edited.",
            code="APPOINTMENT_NOT_EDITABLE",
        )

    if appointment.start_time <= datetime.now(timezone.utc):
        raise ConflictError(
            "Past appointments cannot be edited.",
            code="APPOINTMENT_IN_PAST",
        )

    changes = data.model_dump(exclude_unset=True)

    new_start = changes.get("start_time", appointment.start_time)
    new_end = changes.get("end_time", appointment.end_time)

    if new_end is not None and new_end <= new_start:
        raise ConflictError(
            "end_time must be after start_time.",
            code="INVALID_TIME_RANGE",
        )

    if "start_time" in changes or "end_time" in changes:
        if _has_overlap(
            db,
            appointment.pet_id,
            new_start,
            new_end,
            exclude_appointment_id=appointment.id,
        ):
            raise ConflictError(
                "This pet already has an appointment in that time window.",
                code="APPOINTMENT_OVERLAP",
            )

    # Snapshot the pre-update date BEFORE mutating start_time below — this is
    # the only chance to know which day's cache also needs invalidating if
    # the appointment moved to a different day.
    old_date = appointment.start_time.date()
    clinic_id = appointment.clinic_id

    for field, value in changes.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    new_date = appointment.start_time.date()
    invalidate_slots(clinic_id, new_date)
    if new_date != old_date:
        invalidate_slots(clinic_id, old_date)

    return appointment


def change_appointment_status(
    db: Session, appointment: Appointment, new_status: AppointmentStatus
) -> Appointment:
    """Move an appointment to a new status, if the transition is legal."""
    current = appointment.status
    target = new_status.value

    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise ConflictError(
            f"Cannot change status from {current} to {target}.",
            code="INVALID_STATUS_TRANSITION",
        )

    appointment.status = target
    db.commit()
    db.refresh(appointment)

    # Cancelling frees the slot; completing doesn't change availability, but
    # invalidating on every status change is simpler to reason about and
    # verify than special-casing which transitions matter.
    invalidate_slots(appointment.clinic_id, appointment.start_time.date())

    return appointment
