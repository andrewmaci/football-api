from .base import BaseEntity

class LeagueEntity(BaseEntity):
    league_id: int
    league_name: str
    scoring_type: str
