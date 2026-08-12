from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models import Pet, User
from app.schemas.pets import PetCreate, PetUpdate


def get_pet(db: Session, pet_id: int, current_user: User) -> Pet:
    pet = db.scalar(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    if pet is None:
        raise NotFoundError("Pet not found.", code="PET_NOT_FOUND")
    return pet


def get_all_pet(
    db: Session, current_user: User, limit: int = 50, offset: int = 0
) -> list[Pet]:
    stmt = (
        select(Pet)
        .where(Pet.owner_id == current_user.id)
        .order_by(Pet.name)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


def create_pet(db: Session, data: PetCreate, current_user: User) -> Pet:
    pet = Pet(owner_id=current_user.id, **data.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def update_pet(db: Session, pet: Pet, data: PetUpdate) -> Pet:
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(pet, field, value)
    db.commit()
    db.refresh(pet)
    return pet
