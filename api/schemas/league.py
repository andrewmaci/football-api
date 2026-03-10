from datetime import date

from pydantic import BaseModel

from .team import TeamBase


class League(BaseModel):
    league_id: int
    league_name: str
    scoring_type: str
    last_changed_date: date
    teams: list[TeamBase] = []
