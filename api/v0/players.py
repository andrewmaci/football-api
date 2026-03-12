from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_player_repo
from api.schemas import Player, PlayerBase
from domain.interfaces.player_repository import PlayerRepository
from domain.value_objects.pagination import PaginationParams

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerBase], summary="List players")
def get_players(
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    changed_since: Optional[date] = None,
    skip: int = 0,
    limit: Optional[int] = 20,
) -> list[PlayerBase]:
    result = repo.search(
        first_name=first_name,
        last_name=last_name,
        changed_since=changed_since,
        pagination=PaginationParams(skip=skip, limit=limit),
    )
    return [PlayerBase.model_validate(p.model_dump()) for p in result.items]


@router.get("/{player_id}", response_model=Player, summary="Get player by ID")
def get_player(
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
    player_id: int,
) -> Player:
    player = repo.get_by_id(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return Player.model_validate(player.model_dump())
