from typing import Optional
from .base import BaseEntity
from .performance import PerformanceEntity

class PlayerEntity(BaseEntity):
    player_id: int
    gsis_id: Optional[str] = None
    first_name: str
    last_name: str
    position: str
    performances: list[PerformanceEntity] = []
