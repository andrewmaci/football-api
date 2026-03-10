from datetime import date
from unittest.mock import MagicMock, call

import pytest

from domain.value_objects.pagination import PaginatedResult, PaginationParams
from infrastructure.database.models import League
from infrastructure.database.repositories.sqlalchemy_league_repository import (
    SqlAlchemyLeagueRepository,
)


def make_orm_league(
    league_id: int = 1,
    league_name: str = "Test League",
    scoring_type: str = "PPR",
    last_changed_date: date = date(2024, 1, 1),
) -> MagicMock:
    league = MagicMock(spec=League)
    league.league_id = league_id
    league.league_name = league_name
    league.scoring_type = scoring_type
    league.last_changed_date = last_changed_date
    league.teams = []
    return league


class TestGetById:
    def test_calls_session_scalar_for_get_by_id(self):
        session = MagicMock()
        session.scalar.return_value = make_orm_league()
        repo = SqlAlchemyLeagueRepository(session)

        repo.get_by_id(42)

        session.scalar.assert_called_once()

    def test_returns_entity_when_session_returns_row(self):
        session = MagicMock()
        session.scalar.return_value = make_orm_league(league_id=1, league_name="Fantasy")
        repo = SqlAlchemyLeagueRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.league_id == 1
        assert result.league_name == "Fantasy"

    def test_returns_none_when_session_returns_none(self):
        session = MagicMock()
        session.scalar.return_value = None
        repo = SqlAlchemyLeagueRepository(session)

        result = repo.get_by_id(99)

        assert result is None


class TestGetAll:
    def test_returns_paginated_result_with_items(self):
        session = MagicMock()
        orm_leagues = [make_orm_league(league_id=i) for i in range(3)]
        session.scalar.return_value = 3
        session.execute.return_value.scalars.return_value.all.return_value = orm_leagues
        repo = SqlAlchemyLeagueRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 3
        assert len(result.items) == 3

    def test_handles_zero_total_count(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.all.return_value = []
        repo = SqlAlchemyLeagueRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []


class TestGetLeagueCount:
    def test_returns_scalar_result(self):
        session = MagicMock()
        session.scalar.return_value = 7
        repo = SqlAlchemyLeagueRepository(session)

        assert repo.get_league_count() == 7

    def test_returns_zero_when_scalar_is_none(self):
        session = MagicMock()
        session.scalar.return_value = None
        repo = SqlAlchemyLeagueRepository(session)

        assert repo.get_league_count() == 0
