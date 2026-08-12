from fastapi import APIRouter, Query, status

from app.deps import CurrentUser, DbSession
from app.schemas.appointments import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatusUpdate,
    AppointmentUpdate,
)
from app.services import appointments as service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return service.get_all_appointment(db, current_user, limit=limit, offset=offset)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: int, current_user: CurrentUser, db: DbSession):
    return service.get_appointment(db, appointment_id, current_user)


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreate, current_user: CurrentUser, db: DbSession
):
    return service.create_appointment(db, data, current_user)


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    appointment = service.get_appointment(db, appointment_id, current_user)
    return service.update_appointment(db, appointment, data)


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def change_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    appointment = service.get_appointment(db, appointment_id, current_user)
    return service.change_appointment_status(db, appointment, data.status)
