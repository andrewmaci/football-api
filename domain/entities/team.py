from .base import BaseEntity
from .player import PlayerEntity

class TeamEntity(BaseEntity):
    team_id: int
    league_id: int
    team_name: str
    players: list[PlayerEntity] = []
