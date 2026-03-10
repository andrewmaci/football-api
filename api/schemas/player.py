from datetime import date
from typing import Optional

from pydantic import BaseModel

from .performance import Performance


class PlayerBase(BaseModel):
    player_id: int
    gsis_id: Optional[str] = None
    first_name: str
    last_name: str
    position: str
    last_changed_date: date


class Player(PlayerBase):
    performances: list[Performance] = []
