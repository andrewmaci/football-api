from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends

from api.dependencies import get_performance_repo
from api.schemas import Performance
from domain.interfaces.performance_repository import PerformanceRepository
from domain.value_objects.pagination import PaginationParams

router = APIRouter(prefix="/performances", tags=["performances"])


@router.get("", response_model=list[Performance], summary="List performances")
def get_performances(
    repo: Annotated[PerformanceRepository, Depends(get_performance_repo)],
    player_id: Optional[int] = None,
    week_number: Optional[str] = None,
    changed_since: Optional[date] = None,
    skip: int = 0,
    limit: Optional[int] = 20,
) -> list[Performance]:
    result = repo.search(
        playerid=player_id,
        week_number=week_number,
        changed_since=changed_since,
        pagination=PaginationParams(skip=skip, limit=limit),
    )
    return [Performance.model_validate(p.model_dump()) for p in result.items]
