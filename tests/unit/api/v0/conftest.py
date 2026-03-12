from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.dependencies import (
    get_league_repo,
    get_performance_repo,
    get_player_repo,
    get_team_repo,
)
from domain.entities.league import LeagueEntity
from domain.entities.performance import PerformanceEntity
from domain.entities.player import PlayerEntity
from domain.entities.team import TeamEntity
from domain.value_objects.pagination import PaginatedResult


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_player_entity(
    player_id: int = 1,
    gsis_id: str | None = "ABC123",
    first_name: str = "John",
    last_name: str = "Doe",
    position: str = "QB",
    last_changed_date: date = date(2024, 1, 1),
    performances: list = [],
) -> PlayerEntity:
    return PlayerEntity(
        player_id=player_id,
        gsis_id=gsis_id,
        first_name=first_name,
        last_name=last_name,
        position=position,
        last_changed_date=last_changed_date,
        performances=performances,
    )


def make_performance_entity(
    performance_id: int = 1,
    player_id: int = 1,
    week_number: str = "1",
    fantasy_points: float = 10.0,
    last_changed_date: date = date(2024, 1, 1),
) -> PerformanceEntity:
    return PerformanceEntity(
        performance_id=performance_id,
        player_id=player_id,
        week_number=week_number,
        fantasy_points=fantasy_points,
        last_changed_date=last_changed_date,
    )


def make_team_entity(
    team_id: int = 1,
    league_id: int = 1,
    team_name: str = "Test Team",
    last_changed_date: date = date(2024, 1, 1),
    players: list = [],
) -> TeamEntity:
    return TeamEntity(
        team_id=team_id,
        league_id=league_id,
        team_name=team_name,
        last_changed_date=last_changed_date,
        players=players,
    )


def make_league_entity(
    league_id: int = 1,
    league_name: str = "Test League",
    scoring_type: str = "PPR",
    last_changed_date: date = date(2024, 1, 1),
    teams: list = [],
) -> LeagueEntity:
    return LeagueEntity(
        league_id=league_id,
        league_name=league_name,
        scoring_type=scoring_type,
        last_changed_date=last_changed_date,
        teams=teams,
    )


def mock_player_repo(search_result: PaginatedResult | None = None, get_by_id_result=None, player_count: int = 0):
    repo = MagicMock()
    repo.search.return_value = search_result or PaginatedResult(items=[], total_count=0)
    repo.get_by_id.return_value = get_by_id_result
    repo.get_player_count.return_value = player_count
    app.dependency_overrides[get_player_repo] = lambda: repo
    return repo


def mock_performance_repo(search_result: PaginatedResult | None = None):
    repo = MagicMock()
    repo.search.return_value = search_result or PaginatedResult(items=[], total_count=0)
    app.dependency_overrides[get_performance_repo] = lambda: repo
    return repo


def mock_team_repo(search_result: PaginatedResult | None = None, get_by_id_result=None, team_count: int = 0):
    repo = MagicMock()
    repo.search.return_value = search_result or PaginatedResult(items=[], total_count=0)
    repo.get_by_id.return_value = get_by_id_result
    repo.get_team_count.return_value = team_count
    app.dependency_overrides[get_team_repo] = lambda: repo
    return repo


def mock_league_repo(search_result: PaginatedResult | None = None, get_by_id_result=None, league_count: int = 0):
    repo = MagicMock()
    repo.search.return_value = search_result or PaginatedResult(items=[], total_count=0)
    repo.get_by_id.return_value = get_by_id_result
    repo.get_league_count.return_value = league_count
    app.dependency_overrides[get_league_repo] = lambda: repo
    return repo
