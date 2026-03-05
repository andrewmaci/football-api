from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.team import TeamEntity
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from datetime import datetime

class TeamRepository(ABC):
    @abstractmethod
    def get_by_id(self, team_id: int) -> Optional[TeamEntity]: ...

    @abstractmethod
    def get_all(self, pagination: PaginationParams) -> PaginatedResult[TeamEntity]: ...

    @abstractmethod
    def search(
        self,
        team_name: str | None = None,
        changed_since: datetime | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[TeamEntity]: ...

    @abstractmethod
    def get_team_count(self) -> int: ...