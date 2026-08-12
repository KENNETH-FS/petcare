from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.clinics import Clinic
    from app.models.pets import Pet

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (Index("ix_appointments_clinic_start", "clinic_id", "start_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="CASCADE"), index=True
    )
    clinic_id: Mapped[int] = mapped_column(
        ForeignKey("clinics.id", ondelete="RESTRICT"),
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), server_default="scheduled")
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    clinic: Mapped["Clinic"] = relationship(back_populates="appointments")
    pet: Mapped["Pet"] = relationship(back_populates="appointments")
