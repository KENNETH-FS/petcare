from fastapi import APIRouter

from app.deps import CurrentUser
from app.services import slots as slots_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/cache-stats")
def cache_stats(current_user: CurrentUser) -> dict[str, int | float]:
    """Hit/miss counters for the available-slots cache, this process only."""
    return slots_service.get_cache_stats()
