from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends

from api.dependencies import get_team_repo
from api.schemas import Team
from domain.interfaces.team_repository import TeamRepository
from domain.value_objects.pagination import PaginationParams

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[Team], summary="List teams")
def get_teams(
    repo: Annotated[TeamRepository, Depends(get_team_repo)],
    team_name: Optional[str] = None,
    changed_since: Optional[date] = None,
    skip: int = 0,
    limit: Optional[int] = 20,
) -> list[Team]:
    result = repo.search(
        team_name=team_name,
        changed_since=changed_since,
        pagination=PaginationParams(skip=skip, limit=limit),
    )
    return [Team.model_validate(t.model_dump()) for t in result.items]
