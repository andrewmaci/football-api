
from sqlalchemy import ReturnsRows, func, select
from typing import Optional

from domain.interfaces.player_repository import PlayerRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from domain.entities.player import PlayerEntity
from infrastructure.database.models import Performance, Player

from sqlalchemy.orm import Session, joinedload

from datetime import date

class SqlAlchemyPlayerRepository(PlayerRepository):
   def __init__(self, session: Session):
       self.session = session

   def get_by_id(self, player_id: int) -> Optional[PlayerEntity]:
       player = self.session.get(Player,player_id)
       if player is None:
           return None
       return PlayerEntity.model_validate(player)

   def get_all(self, pagination: PaginationParams) -> PaginatedResult[PlayerEntity]:
       total = self.get_player_count()
      
       rows = (
           self.session.execute(
           select(Player).offset(pagination.skip).limit(pagination.limit)
           )
           .scalars()
           .all()  
       )  
      
       return PaginatedResult(
           items=[PlayerEntity.model_validate(player) for player in rows],
           total_count=total
       )


   def get_player_count(self) -> int:
       return self.session.scalar(select(func.count()).select_from(Player)) or 0

   def search(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        changed_since: date | None = None,
        pagination: PaginationParams = PaginationParams()) -> PaginatedResult[PlayerEntity]:

       count_query = select(func.count()).select_from(Player)

       query = select(Player)

       if first_name:
           name_filter = Player.first_name.ilike(f"%{first_name}%")
           query = query.where(name_filter)
           count_query = count_query.where(name_filter)

       if last_name:
           last_name_filter = Player.last_name.ilike(f"%{last_name}%")
           query = query.where(last_name_filter)
           count_query = count_query.where(last_name_filter)

       if changed_since is not None:
           date_filter = Player.last_changed_date >= changed_since
           query = query.where(date_filter)
           count_query = count_query.where(date_filter)

       total = self.session.scalar(count_query) or 0

       rows = (
           self.session.execute(
               query.options(
                joinedload(Player.teams),
                joinedload(Player.performances)
                )
               .offset(pagination.skip)
               .limit(pagination.limit)
           )
           .scalars()
           .unique()
           .all()
       )

       return PaginatedResult(
           items = [PlayerEntity.model_validate(player) for player in rows],
           total_count = total
       )
