from fastapi import APIRouter, Query, status

from app.deps import CurrentUser, DbSession
from app.schemas.pets import PetCreate, PetRead, PetUpdate
from app.services import pets as service

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("", response_model=list[PetRead])
def list_pets(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return service.get_all_pet(db, current_user, limit=limit, offset=offset)


@router.get("/{pet_id}", response_model=PetRead)
def get_pet(pet_id: int, current_user: CurrentUser, db: DbSession):
    return service.get_pet(db, pet_id, current_user)


@router.post("", response_model=PetRead, status_code=status.HTTP_201_CREATED)
def create_pet(data: PetCreate, current_user: CurrentUser, db: DbSession):
    return service.create_pet(db, data, current_user)


@router.patch("/{pet_id}", response_model=PetRead)
def update_pet(pet_id: int, data: PetUpdate, current_user: CurrentUser, db: DbSession):
    pet = service.get_pet(db, pet_id, current_user)
    return service.update_pet(db, pet, data)
