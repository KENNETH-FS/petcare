import logging
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cache import cache_delete, cache_get_json, cache_set_json, get_redis
from app.errors import NotFoundError
from app.models import Appointment, Clinic

logger = logging.getLogger("app.slots")

CLINIC_OPEN_HOUR = 9
CLINIC_CLOSE_HOUR = 17
SLOT_MINUTES = 30
SLOTS_TTL_SECONDS = 60  # short TTL: slots change whenever anyone books

_HITS = 0
_MISSES = 0


def _cache_key(clinic_id: int, on_date: date) -> str:
    return f"slots:{clinic_id}:{on_date.isoformat()}"


def _generate_all_slots(on_date: date) -> list[datetime]:
    """All candidate slot start-times for a day, ignoring bookings."""
    start = datetime.combine(on_date, time(CLINIC_OPEN_HOUR), tzinfo=timezone.utc)
    end = datetime.combine(on_date, time(CLINIC_CLOSE_HOUR), tzinfo=timezone.utc)

    slots = []
    current = start
    while current < end:
        slots.append(current)
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


def _load_available_slots_from_db(
    db: Session, clinic_id: int, on_date: date
) -> list[str]:
    """The 'source of truth' load — what cache-aside calls on a miss."""
    clinic = db.get(Clinic, clinic_id)
    if clinic is None:
        raise NotFoundError("Clinic not found.", code="CLINIC_NOT_FOUND")

    all_slots = _generate_all_slots(on_date)

    day_start = datetime.combine(on_date, time.min, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    stmt = select(Appointment.start_time).where(
        Appointment.clinic_id == clinic_id,
        Appointment.status == "scheduled",
        Appointment.start_time >= day_start,
        Appointment.start_time < day_end,
    )
    booked_times = list(db.scalars(stmt).all())

    # IMPORTANT: booking creation does not currently enforce that
    # start_time lands exactly on a 30-minute grid mark. So instead of an
    # exact equality match, a slot is considered booked if any real
    # appointment starts anywhere inside that slot's window. This is more
    # forgiving and correct than exact-match, but it does mean an
    # off-grid booking can only ever "consume" one slot even if it runs
    # long — a real limitation, worth fixing when slot duration becomes
    # configurable per appointment type.
    def is_booked(slot: datetime) -> bool:
        slot_end = slot + timedelta(minutes=SLOT_MINUTES)
        return any(slot <= booked < slot_end for booked in booked_times)

    available = [slot for slot in all_slots if not is_booked(slot)]
    return [slot.isoformat() for slot in available]


def get_available_slots(db: Session, clinic_id: int, on_date: date) -> list[str]:
    """Cache-aside: check cache, on miss load from DB and populate cache."""
    global _HITS, _MISSES
    client = get_redis()
    key = _cache_key(clinic_id, on_date)

    cached = cache_get_json(client, key)
    if cached is not None:
        _HITS += 1
        logger.info(
            "slots_cache_hit",
            extra={"clinic_id": clinic_id, "date": on_date.isoformat()},
        )
        return cached

    _MISSES += 1
    logger.info(
        "slots_cache_miss",
        extra={"clinic_id": clinic_id, "date": on_date.isoformat()},
    )
    slots = _load_available_slots_from_db(db, clinic_id, on_date)
    cache_set_json(client, key, slots, ttl_seconds=SLOTS_TTL_SECONDS)
    return slots


def invalidate_slots(clinic_id: int, on_date: date) -> None:
    """Call this after any write that could change availability."""
    client = get_redis()
    cache_delete(client, _cache_key(clinic_id, on_date))
    logger.info(
        "slots_cache_invalidated",
        extra={"clinic_id": clinic_id, "date": on_date.isoformat()},
    )
