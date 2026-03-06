from .base import BaseEntity

class PerformanceEntity(BaseEntity):
    performance_id: int
    player_id: int
    week_number: str
    fantasy_points: float
