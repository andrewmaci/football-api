from fastapi import Depends
from sqlalchemy.orm import Session

from domain.interfaces.league_repository import LeagueRepository
from domain.interfaces.performance_repository import PerformanceRepository
from domain.interfaces.player_repository import PlayerRepository
from domain.interfaces.team_repository import TeamRepository
from infrastructure.database.repositories.sqlalchemy_league_repository import SqlAlchemyLeagueRepository
from infrastructure.database.repositories.sqlalchemy_performance_repository import SqlAlchemyPerformanceRepository
from infrastructure.database.repositories.sqlalchemy_player_repository import SqlAlchemyPlayerRepository
from infrastructure.database.repositories.sqlalchemy_team_repository import SqlAlchemyTeamRepository
from infrastructure.database.session import get_session


def get_player_repo(session: Session = Depends(get_session)) -> PlayerRepository:
    return SqlAlchemyPlayerRepository(session)


def get_performance_repo(session: Session = Depends(get_session)) -> PerformanceRepository:
    return SqlAlchemyPerformanceRepository(session)


def get_league_repo(session: Session = Depends(get_session)) -> LeagueRepository:
    return SqlAlchemyLeagueRepository(session)


def get_team_repo(session: Session = Depends(get_session)) -> TeamRepository:
    return SqlAlchemyTeamRepository(session)
