from datetime import date
from unittest.mock import MagicMock

from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import Performance
from infrastructure.database.repositories.sqlalchemy_performance_repository import (
    SqlAlchemyPerformanceRepository,
)


def make_orm_performance(
    performance_id: int = 1,
    player_id: int = 1,
    week_number: str = "1",
    fantasy_points: float = 10.0,
    last_changed_date: date = date(2024, 1, 1),
) -> MagicMock:
    performance = MagicMock(spec=Performance)
    performance.performance_id = performance_id
    performance.player_id = player_id
    performance.week_number = week_number
    performance.fantasy_points = fantasy_points
    performance.last_changed_date = last_changed_date
    return performance


class TestGetById:
    def test_calls_session_get_with_correct_args(self):
        session = MagicMock()
        session.get.return_value = make_orm_performance()
        repo = SqlAlchemyPerformanceRepository(session)

        repo.get_by_id(42)

        session.get.assert_called_once_with(Performance, 42)

    def test_returns_entity_when_session_returns_row(self):
        session = MagicMock()
        session.get.return_value = make_orm_performance(performance_id=5, week_number="7", fantasy_points=33.5)
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.get_by_id(5)

        assert result is not None
        assert result.performance_id == 5
        assert result.week_number == "7"
        assert result.fantasy_points == 33.5

    def test_returns_none_when_session_returns_none(self):
        session = MagicMock()
        session.get.return_value = None
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.get_by_id(99)

        assert result is None

    def test_returns_entity_with_correct_player_id(self):
        session = MagicMock()
        session.get.return_value = make_orm_performance(player_id=7)
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.player_id == 7


class TestGetAll:
    def test_returns_paginated_result_with_items(self):
        session = MagicMock()
        orm_performances = [make_orm_performance(performance_id=i) for i in range(3)]
        session.scalar.return_value = 3
        session.execute.return_value.scalars.return_value.all.return_value = orm_performances
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 3
        assert len(result.items) == 3

    def test_handles_zero_total_count(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.all.return_value = []
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []


class TestSearch:
    def test_returns_paginated_result(self):
        session = MagicMock()
        orm_performances = [make_orm_performance(performance_id=1)]
        session.scalar.return_value = 1
        session.execute.return_value.scalars.return_value.all.return_value = orm_performances
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.search(week_number="1")

        assert result.total_count == 1
        assert len(result.items) == 1

    def test_returns_empty_when_no_match(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.all.return_value = []
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.search(week_number="99")

        assert result.total_count == 0
        assert result.items == []

    def test_returns_all_when_no_filters(self):
        session = MagicMock()
        orm_performances = [make_orm_performance(performance_id=i) for i in range(2)]
        session.scalar.return_value = 2
        session.execute.return_value.scalars.return_value.all.return_value = orm_performances
        repo = SqlAlchemyPerformanceRepository(session)

        result = repo.search()

        assert result.total_count == 2
        assert len(result.items) == 2
