from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.player import PlayerEntity
from datetime import date
from domain.value_objects.pagination import PaginationParams, PaginatedResult

class PlayerRepository(ABC):

    @abstractmethod
    def get_by_id(self, player_id: int) -> Optional[PlayerEntity]: ...

    @abstractmethod
    def get_all(self, pagination: PaginationParams = PaginationParams()) -> PaginatedResult[PlayerEntity]: ...

    @abstractmethod
    def search(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[PlayerEntity]: ...

    @abstractmethod
    def get_player_count(self) -> int: ...
