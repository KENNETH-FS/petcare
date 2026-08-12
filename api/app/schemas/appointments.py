from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: int
    clinic_id: int
    start_time: datetime
    end_time: datetime | None = None
    notes: str | None = None

    @field_validator("start_time", "end_time")
    @classmethod
    def must_be_aware(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        if v.tzinfo is None:
            raise ValueError("must include a timezone offset")
        return v

    @field_validator("start_time")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(timezone.utc):
            raise ValueError("start_time must be in the future")
        return v

    @model_validator(mode="after")
    def end_after_start(self) -> "AppointmentCreate":
        if self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_time: datetime | None = None
    end_time: datetime | None = None
    notes: str | None = None


class AppointmentStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AppointmentStatus


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    clinic_id: int
    start_time: datetime
    end_time: datetime | None
    status: str
    notes: str | None
    created_at: datetime


class AppointmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime | None
    status: str
    pet_name: str
    owner_name: str
