from datetime import date

from pydantic import BaseModel

from .player import PlayerBase


class TeamBase(BaseModel):
    team_id: int
    league_id: int
    team_name: str
    last_changed_date: date


class Team(TeamBase):
    players: list[PlayerBase] = []
