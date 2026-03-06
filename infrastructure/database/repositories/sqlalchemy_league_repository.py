from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from domain.entities.league import LeagueEntity
from domain.interfaces.league_repository import LeagueRepository
from domain.value_objects.pagination import PaginatedResult, PaginationParams
from infrastructure.database.models import League


class SqlAlchemyLeagueRepository(LeagueRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, league_id: int) -> Optional[LeagueEntity]:
        league = self.session.get(League, league_id)
        if league is None:
            return None
        return LeagueEntity.model_validate(league)

    def get_all(self, pagination: PaginationParams) -> PaginatedResult[LeagueEntity]:
        total = self.session.scalar(select(func.count()).select_from(League))

        rows = (
            self.session.execute(
                select(League).offset(pagination.skip).limit(pagination.limit)
            )
            .scalars()
            .all()
        )

        return PaginatedResult(
            items=[LeagueEntity.model_validate(r) for r in rows],
            total_count=total or 0,
        )

    def search(
        self,
        league_name: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResult[LeagueEntity]:
        query = select(League)
        count_query = select(func.count()).select_from(League)

        if league_name is not None:
            name_filter = League.league_name.ilike(f"%{league_name}%")
            query = query.where(name_filter)
            count_query = count_query.where(name_filter)

        if changed_since is not None:
            date_filter = League.last_changed_date >= changed_since
            query = query.where(date_filter)
            count_query = count_query.where(date_filter)

        total = self.session.scalar(count_query)

        rows = (
            self.session.execute(
                query.options(joinedload(League.teams)).offset(pagination.skip).limit(pagination.limit)
            )
            .scalars()
            .unique()
            .all()
        )

        return PaginatedResult(
            items=[LeagueEntity.model_validate(r) for r in rows],
            total_count=total or 0,
        )

    def get_league_count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(League)) or 0
