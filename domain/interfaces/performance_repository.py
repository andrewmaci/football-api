from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.performance import PerformanceEntity
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from datetime import date

class PerformanceRepository(ABC):
    @abstractmethod
    def get_by_id(self, performance_id: int) -> Optional[PerformanceEntity]: ...

    @abstractmethod
    def get_all(self, pagination: PaginationParams) -> PaginatedResult[PerformanceEntity]: ...

    @abstractmethod
    def search(
        self,
        playerid: int | None = None,
        week_number: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[PerformanceEntity]: ...