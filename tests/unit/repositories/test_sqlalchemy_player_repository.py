from datetime import date
from unittest.mock import MagicMock

import pytest

from domain.value_objects.pagination import PaginatedResult, PaginationParams
from infrastructure.database.models import Player
from infrastructure.database.repositories.sqlalchemy_player_repository import (
    SqlAlchemyPlayerRepository,
)


def make_orm_player(
    player_id: int = 1,
    gsis_id: str | None = "ABC123",
    first_name: str = "John",
    last_name: str = "Doe",
    position: str = "QB",
    last_changed_date: date = date(2024, 1, 1),
) -> MagicMock:
    player = MagicMock(spec=Player)
    player.player_id = player_id
    player.gsis_id = gsis_id
    player.first_name = first_name
    player.last_name = last_name
    player.position = position
    player.last_changed_date = last_changed_date
    return player


class TestGetById:
    def test_calls_session_get_with_correct_args(self):
        session = MagicMock()
        session.get.return_value = make_orm_player()
        repo = SqlAlchemyPlayerRepository(session)

        repo.get_by_id(42)

        session.get.assert_called_once_with(Player, 42)

    def test_returns_entity_when_session_returns_row(self):
        session = MagicMock()
        session.get.return_value = make_orm_player(player_id=1, first_name="Jane", last_name="Smith")
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.player_id == 1
        assert result.first_name == "Jane"
        assert result.last_name == "Smith"

    def test_returns_none_when_session_returns_none(self):
        session = MagicMock()
        session.get.return_value = None
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.get_by_id(99)

        assert result is None

    def test_returns_entity_with_null_gsis_id(self):
        session = MagicMock()
        session.get.return_value = make_orm_player(gsis_id=None)
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.gsis_id is None


class TestGetAll:
    def test_returns_paginated_result_with_items(self):
        session = MagicMock()
        orm_players = [make_orm_player(player_id=i) for i in range(3)]
        session.scalar.return_value = 3
        session.execute.return_value.scalars.return_value.all.return_value = orm_players
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 3
        assert len(result.items) == 3

    def test_handles_zero_total_count(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.all.return_value = []
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []


class TestSearch:
    def test_returns_paginated_result(self):
        session = MagicMock()
        orm_players = [make_orm_player(player_id=1)]
        session.scalar.return_value = 1
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = orm_players
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.search(first_name="John")

        assert result.total_count == 1
        assert len(result.items) == 1

    def test_returns_empty_when_no_match(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = []
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.search(first_name="Nobody")

        assert result.total_count == 0
        assert result.items == []

    def test_returns_all_when_no_filters(self):
        session = MagicMock()
        orm_players = [make_orm_player(player_id=i) for i in range(2)]
        session.scalar.return_value = 2
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = orm_players
        repo = SqlAlchemyPlayerRepository(session)

        result = repo.search()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestGetPlayerCount:
    def test_returns_scalar_result(self):
        session = MagicMock()
        session.scalar.return_value = 5
        repo = SqlAlchemyPlayerRepository(session)

        assert repo.get_player_count() == 5

    def test_returns_zero_when_scalar_is_none(self):
        session = MagicMock()
        session.scalar.return_value = None
        repo = SqlAlchemyPlayerRepository(session)

        assert repo.get_player_count() == 0
