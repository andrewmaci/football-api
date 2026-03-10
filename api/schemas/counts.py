from pydantic import BaseModel


class Counts(BaseModel):
    league_count: int
    team_count: int
    player_count: int
