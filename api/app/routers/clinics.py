from fastapi import APIRouter, Query

from app.deps import CurrentUser, DbSession
from app.schemas.appointments import AppointmentRead
from app.services import appointments as service

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
