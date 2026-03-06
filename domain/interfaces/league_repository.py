from domain.entities.league import LeagueEntity
from abc import ABC, abstractmethod
from typing import Optional
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from datetime import date

class LeagueRepository(ABC):
    @abstractmethod
    def get_by_id(self, league_id: int) -> Optional[LeagueEntity]: ...

    @abstractmethod
    def get_all(self, pagination: PaginationParams = PaginationParams()) -> PaginatedResult[LeagueEntity]: ...

    @abstractmethod
    def search(
        self,
        league_name: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[LeagueEntity]: ...

    @abstractmethod
    def get_league_count(self) -> int: ...
