from datetime import date


from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import Performance, Player
from infrastructure.database.repositories.sqlalchemy_performance_repository import (
    SqlAlchemyPerformanceRepository,
)


def make_player(
    session,
    player_id: int = 1,
    first_name: str = "John",
    last_name: str = "Doe",
    position: str = "QB",
    last_changed: date = date(2024, 1, 1),
) -> Player:
    player = Player(
        player_id=player_id,
        first_name=first_name,
        last_name=last_name,
        position=position,
        last_changed_date=last_changed,
    )
    session.add(player)
    session.commit()
    return player


def make_performance(
    session,
    performance_id: int = 1,
    player_id: int = 1,
    week_number: str = "1",
    fantasy_points: float = 10.0,
    last_changed: date = date(2024, 1, 1),
) -> Performance:
    performance = Performance(
        performance_id=performance_id,
        player_id=player_id,
        week_number=week_number,
        fantasy_points=fantasy_points,
        last_changed_date=last_changed,
    )
    session.add(performance)
    session.commit()
    return performance


class TestGetById:
    def test_returns_entity_when_found(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="3", fantasy_points=25.5)
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.performance_id == 1
        assert result.week_number == "3"
        assert result.fantasy_points == 25.5

    def test_returns_none_when_not_found(self, db_session):
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_by_id(999)

        assert result is None

    def test_returns_correct_player_id(self, db_session):
        make_player(db_session, player_id=7)
        make_performance(db_session, performance_id=1, player_id=7)
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.player_id == 7

    def test_returns_correct_fantasy_points(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, fantasy_points=42.75)
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.fantasy_points == 42.75


class TestGetAll:
    def test_returns_all_performances(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=1, week_number="2")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 2
        assert len(result.items) == 2

    def test_returns_empty_when_no_performances(self, db_session):
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []

    def test_pagination_limits_results(self, db_session):
        make_player(db_session, player_id=1)
        for i in range(5):
            make_performance(db_session, performance_id=i + 1, player_id=1, week_number=str(i + 1))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all(PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_pagination_skip_offsets_results(self, db_session):
        make_player(db_session, player_id=1)
        for i in range(5):
            make_performance(db_session, performance_id=i + 1, player_id=1, week_number=str(i + 1))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all(PaginationParams(skip=3, limit=10))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_returns_all_without_limit(self, db_session):
        make_player(db_session, player_id=1)
        for i in range(25):
            make_performance(db_session, performance_id=i + 1, player_id=1, week_number=str(i + 1))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all(PaginationParams(limit=None))

        assert result.total_count == 25
        assert len(result.items) == 25

    def test_returns_all_with_default_pagination(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=1, week_number="2")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.get_all()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestSearch:
    def test_returns_all_when_no_filters(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=1, week_number="2")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search()

        assert result.total_count == 2

    def test_filters_by_player_id(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=2, week_number="1")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(playerid=1)

        assert result.total_count == 1
        assert result.items[0].player_id == 1

    def test_filters_by_player_id_returns_all_weeks(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=1, week_number="2")
        make_performance(db_session, performance_id=3, player_id=2, week_number="1")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(playerid=1)

        assert result.total_count == 2

    def test_filters_by_week_number(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="5")
        make_performance(db_session, performance_id=2, player_id=1, week_number="6")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(week_number="5")

        assert result.total_count == 1
        assert result.items[0].week_number == "5"

    def test_filters_by_week_number_across_players(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2)
        make_performance(db_session, performance_id=1, player_id=1, week_number="3")
        make_performance(db_session, performance_id=2, player_id=2, week_number="3")
        make_performance(db_session, performance_id=3, player_id=1, week_number="4")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(week_number="3")

        assert result.total_count == 2

    def test_filters_by_changed_since(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1", last_changed=date(2023, 1, 1))
        make_performance(db_session, performance_id=2, player_id=1, week_number="2", last_changed=date(2025, 6, 1))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].week_number == "2"

    def test_filters_by_player_id_and_week_number_combined(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        make_performance(db_session, performance_id=2, player_id=1, week_number="2")
        make_performance(db_session, performance_id=3, player_id=2, week_number="1")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(playerid=1, week_number="1")

        assert result.total_count == 1
        assert result.items[0].player_id == 1
        assert result.items[0].week_number == "1"

    def test_filters_by_player_id_and_changed_since_combined(self, db_session):
        make_player(db_session, player_id=1)
        make_player(db_session, player_id=2)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1", last_changed=date(2022, 1, 1))
        make_performance(db_session, performance_id=2, player_id=1, week_number="2", last_changed=date(2025, 1, 1))
        make_performance(db_session, performance_id=3, player_id=2, week_number="1", last_changed=date(2025, 1, 1))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(playerid=1, changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].player_id == 1
        assert result.items[0].week_number == "2"

    def test_returns_empty_when_no_match(self, db_session):
        make_player(db_session, player_id=1)
        make_performance(db_session, performance_id=1, player_id=1, week_number="1")
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(week_number="99")

        assert result.total_count == 0
        assert result.items == []

    def test_search_respects_pagination(self, db_session):
        make_player(db_session, player_id=1)
        for i in range(5):
            make_performance(db_session, performance_id=i + 1, player_id=1, week_number="1", fantasy_points=float(i))
        repo = SqlAlchemyPerformanceRepository(db_session)

        result = repo.search(week_number="1", pagination=PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2
