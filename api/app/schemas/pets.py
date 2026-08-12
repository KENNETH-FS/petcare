from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    species: str
    breed: str | None = None
    date_of_birth: date | None = None


class PetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    species: str | None = None
    breed: str | None = None
    date_of_birth: date | None = None


class PetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    species: str
    breed: str | None
    date_of_birth: date | None
    created_at: datetime
