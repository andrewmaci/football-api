from typing import Optional
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func, select

from domain.entities.performance import PerformanceEntity
from domain.interfaces.performance_repository import PerformanceRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from infrastructure.database.models import Performance


class SqlAlchemyPerformanceRepository(PerformanceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, performance_id: int) -> Optional[PerformanceEntity]:
        performance = self.session.get(Performance, performance_id)
        if performance is None:
            return None
        return PerformanceEntity.model_validate(performance)

    def get_all(self, pagination: PaginationParams = PaginationParams()) -> PaginatedResult[PerformanceEntity]:
        total = self.session.scalar(select(func.count()).select_from(Performance)) or 0

        rows = (
            self.session.execute(
                select(Performance).offset(pagination.skip).limit(pagination.limit)
            )
            .scalars()
            .all()
        )

        return PaginatedResult(
            items=[PerformanceEntity.model_validate(p) for p in rows],
            total_count=total,
        )

    def search(
        self,
        playerid: int | None = None,
        week_number: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[PerformanceEntity]:
        count_query = select(func.count()).select_from(Performance)
        query = select(Performance)

        if playerid is not None:
            player_filter = Performance.player_id == playerid
            query = query.where(player_filter)
            count_query = count_query.where(player_filter)

        if week_number is not None:
            week_filter = Performance.week_number == week_number
            query = query.where(week_filter)
            count_query = count_query.where(week_filter)

        if changed_since is not None:
            date_filter = Performance.last_changed_date >= changed_since
            query = query.where(date_filter)
            count_query = count_query.where(date_filter)

        total = self.session.scalar(count_query) or 0

        rows = (
            self.session.execute(
                query.offset(pagination.skip).limit(pagination.limit)
            )
            .scalars()
            .all()
        )

        return PaginatedResult(
            items=[PerformanceEntity.model_validate(p) for p in rows],
            total_count=total,
        )
