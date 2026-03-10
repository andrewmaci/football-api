from .base import BaseEntity
from .team import TeamEntity

class LeagueEntity(BaseEntity):
    league_id: int
    league_name: str
    scoring_type: str
    teams: list[TeamEntity] = []
