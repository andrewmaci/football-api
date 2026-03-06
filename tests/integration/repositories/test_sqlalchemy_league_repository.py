from datetime import date

import pytest

from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import League
from infrastructure.database.repositories.sqlalchemy_league_repository import (
    SqlAlchemyLeagueRepository,
)


def make_league(
    session,
    league_id: int = 1,
    name: str = "Test League",
    scoring: str = "PPR",
    last_changed: date = date(2024, 1, 1),
) -> League:
    league = League(
        league_id=league_id,
        league_name=name,
        scoring_type=scoring,
        last_changed_date=last_changed,
    )
    session.add(league)
    session.commit()
    return league


class TestGetById:
    def test_returns_entity_when_found(self, db_session):
        make_league(db_session, league_id=1, name="Fantasy Football")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.league_id == 1
        assert result.league_name == "Fantasy Football"

    def test_returns_none_when_not_found(self, db_session):
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_by_id(999)

        assert result is None

    def test_returns_correct_scoring_type(self, db_session):
        make_league(db_session, league_id=1, scoring="Standard")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.scoring_type == "Standard"


class TestGetAll:
    def test_returns_all_leagues(self, db_session):
        make_league(db_session, league_id=1, name="League A")
        make_league(db_session, league_id=2, name="League B")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 2
        assert len(result.items) == 2

    def test_returns_empty_when_no_leagues(self, db_session):
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []

    def test_pagination_limits_results(self, db_session):
        for i in range(5):
            make_league(db_session, league_id=i + 1, name=f"League {i}")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all(PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_pagination_skip_offsets_results(self, db_session):
        for i in range(5):
            make_league(db_session, league_id=i + 1, name=f"League {i}")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all(PaginationParams(skip=3, limit=10))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_returns_all_without_limit(self, db_session):
        for i in range(25):
            make_league(db_session, league_id=i + 1, name=f"League {i}")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all(PaginationParams(limit=None))

        assert result.total_count == 25
        assert len(result.items) == 25

    def test_returns_all_with_default_pagination(self, db_session):
        make_league(db_session, league_id=1, name="League A")
        make_league(db_session, league_id=2, name="League B")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.get_all()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestSearch:
    def test_returns_all_when_no_filters(self, db_session):
        make_league(db_session, league_id=1, name="Alpha")
        make_league(db_session, league_id=2, name="Beta")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search()

        assert result.total_count == 2

    def test_filters_by_name_exact_match(self, db_session):
        make_league(db_session, league_id=1, name="Fantasy Football")
        make_league(db_session, league_id=2, name="Basketball League")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="Fantasy Football")

        assert result.total_count == 1
        assert result.items[0].league_name == "Fantasy Football"

    def test_filters_by_name_partial_match(self, db_session):
        make_league(db_session, league_id=1, name="Fantasy Football")
        make_league(db_session, league_id=2, name="Fantasy Basketball")
        make_league(db_session, league_id=3, name="Soccer League")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="Fantasy")

        assert result.total_count == 2

    def test_filters_by_name_case_insensitive(self, db_session):
        make_league(db_session, league_id=1, name="Fantasy Football")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="fantasy")

        assert result.total_count == 1

    def test_filters_by_changed_since(self, db_session):
        make_league(db_session, league_id=1, name="Old League", last_changed=date(2023, 1, 1))
        make_league(db_session, league_id=2, name="New League", last_changed=date(2025, 6, 1))
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].league_name == "New League"

    def test_filters_by_name_and_changed_since_combined(self, db_session):
        make_league(db_session, league_id=1, name="Fantasy Old", last_changed=date(2022, 1, 1))
        make_league(db_session, league_id=2, name="Fantasy New", last_changed=date(2025, 1, 1))
        make_league(db_session, league_id=3, name="Other New", last_changed=date(2025, 1, 1))
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="Fantasy", changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].league_name == "Fantasy New"

    def test_returns_empty_when_no_match(self, db_session):
        make_league(db_session, league_id=1, name="Football")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="Basketball")

        assert result.total_count == 0
        assert result.items == []

    def test_search_respects_pagination(self, db_session):
        for i in range(5):
            make_league(db_session, league_id=i + 1, name=f"Fantasy {i}")
        repo = SqlAlchemyLeagueRepository(db_session)

        result = repo.search(league_name="Fantasy", pagination=PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2


class TestGetLeagueCount:
    def test_returns_zero_when_empty(self, db_session):
        repo = SqlAlchemyLeagueRepository(db_session)

        assert repo.get_league_count() == 0

    def test_returns_correct_count(self, db_session):
        make_league(db_session, league_id=1)
        make_league(db_session, league_id=2, name="Other")
        repo = SqlAlchemyLeagueRepository(db_session)

        assert repo.get_league_count() == 2
