from .base import BaseEntity

class TeamEntity(BaseEntity):
    team_id: int
    league_id: int
    team_name: str
