from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_league_repo
from api.schemas import League
from domain.interfaces.league_repository import LeagueRepository
from domain.value_objects.pagination import PaginationParams

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("", response_model=list[League], summary="List leagues")
def get_leagues(
    repo: Annotated[LeagueRepository, Depends(get_league_repo)],
    league_name: Optional[str] = None,
    changed_since: Optional[date] = None,
    skip: int = 0,
    limit: Optional[int] = 20,
) -> list[League]:
    result = repo.search(
        league_name=league_name,
        changed_since=changed_since,
        pagination=PaginationParams(skip=skip, limit=limit),
    )
    return [League.model_validate(l.model_dump()) for l in result.items]


@router.get("/{league_id}", response_model=League, summary="Get league by ID")
def get_league(
    repo: Annotated[LeagueRepository, Depends(get_league_repo)],
    league_id: int,
) -> League:
    league = repo.get_by_id(league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return League.model_validate(league.model_dump())
