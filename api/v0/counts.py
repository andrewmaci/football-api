from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_league_repo, get_player_repo, get_team_repo
from api.schemas import Counts
from domain.interfaces.league_repository import LeagueRepository
from domain.interfaces.player_repository import PlayerRepository
from domain.interfaces.team_repository import TeamRepository

router = APIRouter(tags=["counts"])


@router.get("/count", response_model=Counts, summary="Get record counts")
def get_counts(
    league_repo: Annotated[LeagueRepository, Depends(get_league_repo)],
    team_repo: Annotated[TeamRepository, Depends(get_team_repo)],
    player_repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Counts:
    return Counts(
        league_count=league_repo.get_league_count(),
        team_count=team_repo.get_team_count(),
        player_count=player_repo.get_player_count(),
    )
