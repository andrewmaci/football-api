from select import select
from typing import Optional
from datetime import date
from domain.value_objects.pagination import *

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func,select
from domain.entities.team import TeamEntity
from domain.interfaces.team_repository import TeamRepository
from infrastructure.database.models import Team


class SqlAlchemyTeamRepository(TeamRepository):
    def __init__(self,session:Session) -> None:
        self.session = session

    def get_all(self, pagination: PaginationParams=PaginationParams(limit=None)) -> PaginatedResult[TeamEntity]:
        total = self.get_team_count()

        rows = (self.session.execute(
            select(Team).limit(pagination.limit).offset(pagination.skip)
            )
            .scalars()
            .all()
        )

        return PaginatedResult(
            items=[TeamEntity.model_validate(team) for team in rows],
            total_count = total
        )

    def search(
        self,
        team_name: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams()) -> PaginatedResult[TeamEntity]:
        
        count_query = select(func.count()).select_from(Team)
        query = select(Team)

        if team_name:
            name_filter = Team.team_name.ilike(f"%{team_name}%")
            query = query.where(name_filter)
            count_query = count_query.where(name_filter)
        
        if changed_since:
            date_filter = Team.last_changed_date >= changed_since
            query = query.where(date_filter)
            count_query = count_query.where(date_filter)

        total = self.session.scalar(count_query) or 0

        rows = (
           self.session.execute(
               query.options(
                joinedload(Team.players),
                joinedload(Team.league)
                )
               .offset(pagination.skip)
               .limit(pagination.limit)
           )
           .scalars()
           .unique()
           .all()
        )
        return PaginatedResult(
            items=[TeamEntity.model_validate(team) for team in rows],
            total_count=total
        )        


    def get_by_id(self, team_id: int) -> Optional[TeamEntity]:
        team = self.session.get(Team,team_id)

        if not team:
            return None
        return TeamEntity.model_validate(team)

    def get_team_count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(Team)) or 0       