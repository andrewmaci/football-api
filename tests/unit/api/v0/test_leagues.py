from datetime import date

from domain.value_objects.pagination import PaginatedResult

from .conftest import make_league_entity, make_team_entity, mock_league_repo


class TestGetLeagues:
    def test_returns_200_with_empty_list(self, client):
        mock_league_repo(PaginatedResult(items=[], total_count=0))

        response = client.get("/v0/leagues")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_200_with_leagues(self, client):
        leagues = [
            make_league_entity(league_id=1, league_name="Alpha League"),
            make_league_entity(league_id=2, league_name="Beta League"),
        ]
        mock_league_repo(PaginatedResult(items=leagues, total_count=2))

        response = client.get("/v0/leagues")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["league_id"] == 1
        assert data[0]["league_name"] == "Alpha League"
        assert data[1]["league_id"] == 2

    def test_returns_league_fields(self, client):
        league = make_league_entity(
            league_id=3,
            league_name="PPR League",
            scoring_type="PPR",
            last_changed_date=date(2025, 1, 15),
        )
        mock_league_repo(PaginatedResult(items=[league], total_count=1))

        response = client.get("/v0/leagues")

        data = response.json()[0]
        assert data["league_id"] == 3
        assert data["league_name"] == "PPR League"
        assert data["scoring_type"] == "PPR"
        assert data["last_changed_date"] == "2025-01-15"

    def test_includes_teams_in_response(self, client):
        team = make_team_entity(team_id=1, league_id=1, team_name="Red Dragons")
        league = make_league_entity(league_id=1, teams=[team])
        mock_league_repo(PaginatedResult(items=[league], total_count=1))

        response = client.get("/v0/leagues")

        data = response.json()[0]
        assert "teams" in data
        assert len(data["teams"]) == 1
        assert data["teams"][0]["team_id"] == 1
        assert data["teams"][0]["team_name"] == "Red Dragons"

    def test_passes_league_name_filter_to_repo(self, client):
        repo = mock_league_repo()

        client.get("/v0/leagues?league_name=Fantasy")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["league_name"] == "Fantasy"

    def test_passes_changed_since_filter_to_repo(self, client):
        repo = mock_league_repo()

        client.get("/v0/leagues?changed_since=2024-03-01")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["changed_since"] == date(2024, 3, 1)

    def test_passes_pagination_to_repo(self, client):
        repo = mock_league_repo()

        client.get("/v0/leagues?skip=2&limit=5")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["pagination"].skip == 2
        assert call_kwargs["pagination"].limit == 5

    def test_no_filters_calls_repo_with_none_values(self, client):
        repo = mock_league_repo()

        client.get("/v0/leagues")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["league_name"] is None
        assert call_kwargs["changed_since"] is None


class TestGetLeagueById:
    def test_returns_200_when_found(self, client):
        league = make_league_entity(league_id=1, league_name="Test League")
        mock_league_repo(get_by_id_result=league)

        response = client.get("/v0/leagues/1")

        assert response.status_code == 200
        data = response.json()
        assert data["league_id"] == 1
        assert data["league_name"] == "Test League"

    def test_returns_404_when_not_found(self, client):
        mock_league_repo(get_by_id_result=None)

        response = client.get("/v0/leagues/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "League not found"

    def test_includes_teams_in_response(self, client):
        team = make_team_entity(team_id=5, league_id=1, team_name="Blue Hawks")
        league = make_league_entity(league_id=1, teams=[team])
        mock_league_repo(get_by_id_result=league)

        response = client.get("/v0/leagues/1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["teams"]) == 1
        assert data["teams"][0]["team_id"] == 5
        assert data["teams"][0]["team_name"] == "Blue Hawks"

    def test_calls_repo_with_correct_id(self, client):
        repo = mock_league_repo(get_by_id_result=make_league_entity(league_id=7))

        client.get("/v0/leagues/7")

        repo.get_by_id.assert_called_once_with(7)

    def test_empty_teams_list_when_none(self, client):
        league = make_league_entity(league_id=1, teams=[])
        mock_league_repo(get_by_id_result=league)

        response = client.get("/v0/leagues/1")

        assert response.status_code == 200
        assert response.json()["teams"] == []
