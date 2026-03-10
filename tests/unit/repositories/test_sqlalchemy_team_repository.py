from datetime import date
from unittest.mock import MagicMock


from domain.value_objects.pagination import PaginationParams
from infrastructure.database.models import Team
from infrastructure.database.repositories.sqlalchemy_team_repository import (
    SqlAlchemyTeamRepository,
)


def make_orm_team(
    team_id: int = 1,
    league_id: int = 10,
    team_name: str = "Test Team",
    last_changed_date: date = date(2024, 1, 1),
) -> MagicMock:
    team = MagicMock(spec=Team)
    team.team_id = team_id
    team.league_id = league_id
    team.team_name = team_name
    team.last_changed_date = last_changed_date
    team.players = []
    return team


class TestGetById:
    def test_calls_session_scalar_for_get_by_id(self):
        session = MagicMock()
        session.scalar.return_value = make_orm_team()
        repo = SqlAlchemyTeamRepository(session)

        repo.get_by_id(42)

        session.scalar.assert_called_once()

    def test_returns_entity_when_session_returns_row(self):
        session = MagicMock()
        session.scalar.return_value = make_orm_team(team_id=1, team_name="Red Dragons")
        repo = SqlAlchemyTeamRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.team_id == 1
        assert result.team_name == "Red Dragons"

    def test_returns_none_when_session_returns_none(self):
        session = MagicMock()
        session.scalar.return_value = None
        repo = SqlAlchemyTeamRepository(session)

        result = repo.get_by_id(99)

        assert result is None

    def test_returns_entity_with_correct_league_id(self):
        session = MagicMock()
        session.scalar.return_value = make_orm_team(team_id=1, league_id=5)
        repo = SqlAlchemyTeamRepository(session)

        result = repo.get_by_id(1)

        assert result is not None
        assert result.league_id == 5


class TestGetAll:
    def test_returns_paginated_result_with_items(self):
        session = MagicMock()
        orm_teams = [make_orm_team(team_id=i) for i in range(3)]
        session.scalar.return_value = 3
        session.execute.return_value.scalars.return_value.all.return_value = orm_teams
        repo = SqlAlchemyTeamRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 3
        assert len(result.items) == 3

    def test_handles_zero_total_count(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.all.return_value = []
        repo = SqlAlchemyTeamRepository(session)

        result = repo.get_all(PaginationParams())

        assert result.total_count == 0
        assert result.items == []


class TestSearch:
    def test_returns_paginated_result(self):
        session = MagicMock()
        orm_teams = [make_orm_team(team_id=1)]
        session.scalar.return_value = 1
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = orm_teams
        repo = SqlAlchemyTeamRepository(session)

        result = repo.search(team_name="Test")

        assert result.total_count == 1
        assert len(result.items) == 1

    def test_returns_empty_when_no_match(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = []
        repo = SqlAlchemyTeamRepository(session)

        result = repo.search(team_name="Nobody")

        assert result.total_count == 0
        assert result.items == []

    def test_returns_all_when_no_filters(self):
        session = MagicMock()
        orm_teams = [make_orm_team(team_id=i) for i in range(2)]
        session.scalar.return_value = 2
        session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = orm_teams
        repo = SqlAlchemyTeamRepository(session)

        result = repo.search()

        assert result.total_count == 2
        assert len(result.items) == 2


class TestGetTeamCount:
    def test_returns_scalar_result(self):
        session = MagicMock()
        session.scalar.return_value = 5
        repo = SqlAlchemyTeamRepository(session)

        assert repo.get_team_count() == 5

    def test_returns_zero_when_scalar_is_none(self):
        session = MagicMock()
        session.scalar.return_value = None
        repo = SqlAlchemyTeamRepository(session)

        assert repo.get_team_count() == 0
