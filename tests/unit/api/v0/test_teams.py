from datetime import date

from domain.value_objects.pagination import PaginatedResult

from .conftest import make_player_entity, make_team_entity, mock_team_repo


class TestGetTeams:
    def test_returns_200_with_empty_list(self, client):
        mock_team_repo(PaginatedResult(items=[], total_count=0))

        response = client.get("/v0/teams")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_200_with_teams(self, client):
        teams = [
            make_team_entity(team_id=1, team_name="Red Dragons"),
            make_team_entity(team_id=2, team_name="Blue Hawks"),
        ]
        mock_team_repo(PaginatedResult(items=teams, total_count=2))

        response = client.get("/v0/teams")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["team_id"] == 1
        assert data[0]["team_name"] == "Red Dragons"
        assert data[1]["team_id"] == 2

    def test_returns_team_fields(self, client):
        team = make_team_entity(
            team_id=4,
            league_id=2,
            team_name="Green Giants",
            last_changed_date=date(2025, 4, 20),
        )
        mock_team_repo(PaginatedResult(items=[team], total_count=1))

        response = client.get("/v0/teams")

        data = response.json()[0]
        assert data["team_id"] == 4
        assert data["league_id"] == 2
        assert data["team_name"] == "Green Giants"
        assert data["last_changed_date"] == "2025-04-20"

    def test_includes_players_in_response(self, client):
        player = make_player_entity(player_id=1, first_name="John", last_name="Doe")
        team = make_team_entity(team_id=1, players=[player])
        mock_team_repo(PaginatedResult(items=[team], total_count=1))

        response = client.get("/v0/teams")

        data = response.json()[0]
        assert "players" in data
        assert len(data["players"]) == 1
        assert data["players"][0]["player_id"] == 1
        assert data["players"][0]["first_name"] == "John"

    def test_passes_team_name_filter_to_repo(self, client):
        repo = mock_team_repo()

        client.get("/v0/teams?team_name=Dragons")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["team_name"] == "Dragons"

    def test_passes_changed_since_filter_to_repo(self, client):
        repo = mock_team_repo()

        client.get("/v0/teams?changed_since=2024-05-01")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["changed_since"] == date(2024, 5, 1)

    def test_passes_pagination_to_repo(self, client):
        repo = mock_team_repo()

        client.get("/v0/teams?skip=3&limit=7")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["pagination"].skip == 3
        assert call_kwargs["pagination"].limit == 7

    def test_no_filters_calls_repo_with_none_values(self, client):
        repo = mock_team_repo()

        client.get("/v0/teams")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["team_name"] is None
        assert call_kwargs["changed_since"] is None

    def test_empty_players_list_when_none(self, client):
        team = make_team_entity(team_id=1, players=[])
        mock_team_repo(PaginatedResult(items=[team], total_count=1))

        response = client.get("/v0/teams")

        assert response.json()[0]["players"] == []
