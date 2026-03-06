from typing import Optional
from .base import BaseEntity

class PlayerEntity(BaseEntity):
    player_id: int
    gsis_id: Optional[str] = None
    first_name: str
    last_name: str
    position: str
