from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class PaginationParams:
    skip: int = 0
    limit: int | None = 20

@dataclass
class PaginatedResult(Generic[T]):
    items: list[T] = field(default_factory=list)
    total_count: int = 0
