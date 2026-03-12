from .conftest import mock_league_repo, mock_player_repo, mock_team_repo


class TestGetCounts:
    def test_returns_200(self, client):
        mock_league_repo(league_count=0)
        mock_team_repo(team_count=0)
        mock_player_repo(player_count=0)

        response = client.get("/v0/count")

        assert response.status_code == 200

    def test_returns_correct_counts(self, client):
        mock_league_repo(league_count=3)
        mock_team_repo(team_count=12)
        mock_player_repo(player_count=45)

        response = client.get("/v0/count")

        assert response.status_code == 200
        data = response.json()
        assert data["league_count"] == 3
        assert data["team_count"] == 12
        assert data["player_count"] == 45

    def test_returns_zero_counts_when_empty(self, client):
        mock_league_repo(league_count=0)
        mock_team_repo(team_count=0)
        mock_player_repo(player_count=0)

        response = client.get("/v0/count")

        data = response.json()
        assert data["league_count"] == 0
        assert data["team_count"] == 0
        assert data["player_count"] == 0

    def test_response_has_all_count_fields(self, client):
        mock_league_repo(league_count=1)
        mock_team_repo(team_count=1)
        mock_player_repo(player_count=1)

        response = client.get("/v0/count")

        data = response.json()
        assert "league_count" in data
        assert "team_count" in data
        assert "player_count" in data

    def test_each_repo_count_method_is_called(self, client):
        league_repo = mock_league_repo(league_count=2)
        team_repo = mock_team_repo(team_count=8)
        player_repo = mock_player_repo(player_count=20)

        client.get("/v0/count")

        league_repo.get_league_count.assert_called_once()
        team_repo.get_team_count.assert_called_once()
        player_repo.get_player_count.assert_called_once()
