from datetime import date

from fastapi import APIRouter, Query

from app.deps import CurrentUser, DbSession
from app.schemas.appointments import AppointmentRead
from app.services import appointments as service
from app.services import slots as slots_service

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("/{clinic_id}/appointments", response_model=list[AppointmentRead])
def list_clinic_appointments(
    clinic_id: int,
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return service.get_all_clinic_appointment(
        db, clinic_id, current_user, limit=limit, offset=offset
    )


@router.get("/{clinic_id}/available-slots", response_model=list[str])
def get_available_slots(clinic_id: int, on_date: date, db: DbSession):
    """No CurrentUser required — available times aren't sensitive the way
    appointment details are, and a client needs to see slots before it can
    log in to book one. Consistent with clinics being publicly readable.
    """
    return slots_service.get_available_slots(db, clinic_id, on_date)
