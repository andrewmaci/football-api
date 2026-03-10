from datetime import date

from pydantic import BaseModel


class Performance(BaseModel):
    performance_id: int
    player_id: int
    week_number: str
    fantasy_points: float
    last_changed_date: date
