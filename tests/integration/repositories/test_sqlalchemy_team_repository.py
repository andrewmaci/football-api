from datetime import date


from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import League, Team
from infrastructure.database.repositories.sqlalchemy_team_repository import (
    SqlAlchemyTeamRepository,
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


def make_team(
    session,
    team_id: int = 1,
    league_id: int = 1,
    team_name: str = "Test Team",
    last_changed: date = date(2024, 1, 1),
) -> Team:
    team = Team(
        team_id=team_id,
        league_id=league_id,
        team_name=team_name,
        last_changed_date=last_changed,
    )
    session.add(team)
    session.commit()
    return team


class TestGetById:
    def test_returns_entity_when_found(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Dragons")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.team_id == 1
        assert result.team_name == "Red Dragons"

    def test_returns_none_when_not_found(self, db_session):
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_by_id(999)

        assert result is None

    def test_returns_correct_league_id(self, db_session):
        make_league(db_session, league_id=7)
        make_team(db_session, team_id=1, league_id=7)
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.league_id == 7


class TestGetAll:
    def test_returns_all_teams(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Team A")
        make_team(db_session, team_id=2, league_id=1, team_name="Team B")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 2
        assert len(result.items) == 2

    def test_returns_empty_when_no_teams(self, db_session):
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []

    def test_pagination_limits_results(self, db_session):
        make_league(db_session, league_id=1)
        for i in range(5):
            make_team(db_session, team_id=i + 1, league_id=1, team_name=f"Team {i}")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all(PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_pagination_skip_offsets_results(self, db_session):
        make_league(db_session, league_id=1)
        for i in range(5):
            make_team(db_session, team_id=i + 1, league_id=1, team_name=f"Team {i}")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all(PaginationParams(skip=3, limit=10))

        assert result.total_count == 5
        assert len(result.items) == 2

    def test_returns_all_without_limit(self, db_session):
        make_league(db_session, league_id=1)
        for i in range(25):
            make_team(db_session, team_id=i + 1, league_id=1, team_name=f"Team {i}")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all(PaginationParams(limit=None))

        assert result.total_count == 25
        assert len(result.items) == 25

    def test_returns_all_with_default_pagination(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Team A")
        make_team(db_session, team_id=2, league_id=1, team_name="Team B")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.get_all()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestSearch:
    def test_returns_all_when_no_filters(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Alpha")
        make_team(db_session, team_id=2, league_id=1, team_name="Beta")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search()

        assert result.total_count == 2

    def test_filters_by_name_exact_match(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Dragons")
        make_team(db_session, team_id=2, league_id=1, team_name="Blue Eagles")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="Red Dragons")

        assert result.total_count == 1
        assert result.items[0].team_name == "Red Dragons"

    def test_filters_by_name_partial_match(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Dragons")
        make_team(db_session, team_id=2, league_id=1, team_name="Red Hawks")
        make_team(db_session, team_id=3, league_id=1, team_name="Blue Eagles")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="Red")

        assert result.total_count == 2
        team_names = {t.team_name for t in result.items}
        assert "Red Dragons" in team_names
        assert "Red Hawks" in team_names

    def test_filters_by_name_case_insensitive(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Dragons")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="red dragons")

        assert result.total_count == 1

    def test_filters_by_changed_since(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Old Team", last_changed=date(2023, 1, 1))
        make_team(db_session, team_id=2, league_id=1, team_name="New Team", last_changed=date(2025, 6, 1))
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].team_name == "New Team"

    def test_filters_by_name_and_changed_since_combined(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Old", last_changed=date(2022, 1, 1))
        make_team(db_session, team_id=2, league_id=1, team_name="Red New", last_changed=date(2025, 1, 1))
        make_team(db_session, team_id=3, league_id=1, team_name="Blue New", last_changed=date(2025, 1, 1))
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="Red", changed_since=date(2024, 1, 1))

        assert result.total_count == 1
        assert result.items[0].team_name == "Red New"

    def test_returns_empty_when_no_match(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Red Dragons")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="Nonexistent")

        assert result.total_count == 0
        assert result.items == []

    def test_search_respects_pagination(self, db_session):
        make_league(db_session, league_id=1)
        for i in range(5):
            make_team(db_session, team_id=i + 1, league_id=1, team_name=f"Red Team {i}")
        repo = SqlAlchemyTeamRepository(db_session)

        result = repo.search(team_name="Red", pagination=PaginationParams(skip=0, limit=2))

        assert result.total_count == 5
        assert len(result.items) == 2


class TestGetTeamCount:
    def test_returns_zero_when_empty(self, db_session):
        repo = SqlAlchemyTeamRepository(db_session)

        assert repo.get_team_count() == 0

    def test_returns_correct_count(self, db_session):
        make_league(db_session, league_id=1)
        make_team(db_session, team_id=1, league_id=1, team_name="Team A")
        make_team(db_session, team_id=2, league_id=1, team_name="Team B")
        repo = SqlAlchemyTeamRepository(db_session)

        assert repo.get_team_count() == 2
