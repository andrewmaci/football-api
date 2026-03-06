from datetime import date

import pytest

from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import Player
from infrastructure.database.repositories.sqlalchemy_player_repository import (
    SqlAlchemyPlayerRepository,
)


def make_player(
    session,
    player_id: int = 1,
    gsis_id: str | None = "ABC123",
    first_name: str = "John",
    last_name: str = "Doe",
    position: str = "QB",
    last_changed: date = date(2024, 1, 1),
) -> Player:
    player = Player(
        player_id=player_id,
        gsis_id=gsis_id,
        first_name=first_name,
        last_name=last_name,
        position=position,
        last_changed_date=last_changed,
    )
    session.add(player)
    session.commit()
    return player


class TestGetById:
    def test_returns_entity_when_found(self, db_session):
        make_player(db_session, player_id=1, first_name="John", last_name="Doe")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.player_id == 1
        assert result.first_name == "John"
        assert result.last_name == "Doe"

    def test_returns_none_when_not_found(self, db_session):
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_by_id(999)

        assert result is None

    def test_returns_correct_position(self, db_session):
        make_player(db_session, player_id=1, position="WR")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.position == "WR"

    def test_returns_entity_with_null_gsis_id(self, db_session):
        make_player(db_session, player_id=1, gsis_id=None)
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.gsis_id is None


class TestGetAll:
    def test_returns_all_players(self, db_session):
        make_player(db_session, player_id=1, first_name="Alice")
        make_player(db_session, player_id=2, first_name="Bob")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 2
        assert len(result.items) == 2

    def test_returns_empty_when_no_players(self, db_session):
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []

    def test_pagination_limits_results(self, db_session):
        for i in range(5):
            make_player(db_session, player_id=i + 1, first_name=f"Player{i}")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all(PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_pagination_skip_offsets_results(self, db_session):
        for i in range(5):
            make_player(db_session, player_id=i + 1, first_name=f"Player{i}")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all(PaginationParams(skip=3, limit=10))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_returns_all_without_limit(self, db_session):
        for i in range(25):
            make_player(db_session, player_id=i + 1, first_name=f"Player{i}")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all(PaginationParams(limit=None))

        assert result.total_count == 25
        assert len(result.items) == 25

    def test_returns_all_with_default_pagination(self, db_session):
        make_player(db_session, player_id=1, first_name="Alice")
        make_player(db_session, player_id=2, first_name="Bob")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.get_all()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestSearch:
    def test_returns_all_when_no_filters(self, db_session):
        make_player(db_session, player_id=1, first_name="Alice")
        make_player(db_session, player_id=2, first_name="Bob")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search()

        assert result.total_count == 2

    def test_filters_by_first_name_exact_match(self, db_session):
        make_player(db_session, player_id=1, first_name="John", last_name="Doe")
        make_player(db_session, player_id=2, first_name="Jane", last_name="Smith")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="John")

        assert result.total_count == 1
        assert result.items[0].first_name == "John"

    def test_filters_by_first_name_partial_match(self, db_session):
        make_player(db_session, player_id=1, first_name="Jonathan")
        make_player(db_session, player_id=2, first_name="John")
        make_player(db_session, player_id=3, first_name="Alice")
        make_player(db_session, player_id=4, first_name="Jonas")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="Jon")

        assert result.total_count == 2
        first_names = {p.first_name for p in result.items}
        assert "Jonathan" in first_names
        assert "Jonas" in first_names

    def test_filters_by_first_name_case_insensitive(self, db_session):
        make_player(db_session, player_id=1, first_name="John")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="john")

        assert result.total_count == 1

    def test_filters_by_last_name_exact_match(self, db_session):
        make_player(db_session, player_id=1, first_name="John", last_name="Doe")
        make_player(db_session, player_id=2, first_name="Jane", last_name="Smith")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(last_name="Doe")

        assert result.total_count == 1
        assert result.items[0].last_name == "Doe"

    def test_filters_by_last_name_partial_match(self, db_session):
        make_player(db_session, player_id=1, last_name="Doering")
        make_player(db_session, player_id=2, last_name="Doe")
        make_player(db_session, player_id=3, last_name="Smith")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(last_name="Doe")

        assert result.total_count == 2

    def test_filters_by_last_name_case_insensitive(self, db_session):
        make_player(db_session, player_id=1, last_name="Smith")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(last_name="smith")

        assert result.total_count == 1

    def test_filters_by_changed_since(self, db_session):
        make_player(db_session, player_id=1, first_name="Old", last_changed=date(2023, 1, 1))
        make_player(db_session, player_id=2, first_name="New", last_changed=date(2025, 6, 1))
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].first_name == "New"

    def test_filters_by_first_name_and_last_name_combined(self, db_session):
        make_player(db_session, player_id=1, first_name="John", last_name="Doe")
        make_player(db_session, player_id=2, first_name="John", last_name="Smith")
        make_player(db_session, player_id=3, first_name="Jane", last_name="Doe")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="John", last_name="Doe")

        assert result.total_count == 1
        assert result.items[0].first_name == "John"
        assert result.items[0].last_name == "Doe"

    def test_filters_by_first_name_and_changed_since_combined(self, db_session):
        make_player(db_session, player_id=1, first_name="John", last_changed=date(2022, 1, 1))
        make_player(db_session, player_id=2, first_name="John", last_changed=date(2025, 1, 1))
        make_player(db_session, player_id=3, first_name="Jane", last_changed=date(2025, 1, 1))
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="John", changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].first_name == "John"

    def test_returns_empty_when_no_match(self, db_session):
        make_player(db_session, player_id=1, first_name="John")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="Nobody")

        assert result.total_count == 0
        assert result.items == []

    def test_search_respects_pagination(self, db_session):
        for i in range(5):
            make_player(db_session, player_id=i + 1, first_name="John", last_name=f"Player{i}")
        repo = SqlAlchemyPlayerRepository(db_session)

        result = repo.search(first_name="John", pagination=PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2


class TestGetPlayerCount:
    def test_returns_zero_when_empty(self, db_session):
        repo = SqlAlchemyPlayerRepository(db_session)

        assert repo.get_player_count() == 0

    def test_returns_correct_count(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2, first_name="Jane")
        repo = SqlAlchemyPlayerRepository(db_session)

        assert repo.get_player_count() == 2
