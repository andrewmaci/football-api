from datetime import date

from domain.value_objects.pagination import PaginatedResult

from .conftest import make_performance_entity, make_player_entity, mock_player_repo


class TestGetPlayers:
    def test_returns_200_with_empty_list(self, client):
        mock_player_repo(PaginatedResult(items=[], total_count=0))

        response = client.get("/v0/players")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_200_with_players(self, client):
        players = [
            make_player_entity(player_id=1, first_name="John", last_name="Doe"),
            make_player_entity(player_id=2, first_name="Jane", last_name="Smith"),
        ]
        mock_player_repo(PaginatedResult(items=players, total_count=2))

        response = client.get("/v0/players")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["player_id"] == 1
        assert data[0]["first_name"] == "John"
        assert data[1]["player_id"] == 2
        assert data[1]["first_name"] == "Jane"

    def test_response_does_not_include_performances(self, client):
        player = make_player_entity(
            player_id=1,
            performances=[make_performance_entity()],
        )
        mock_player_repo(PaginatedResult(items=[player], total_count=1))

        response = client.get("/v0/players")

        assert response.status_code == 200
        data = response.json()
        assert "performances" not in data[0]

    def test_passes_first_name_filter_to_repo(self, client):
        repo = mock_player_repo()

        client.get("/v0/players?first_name=John")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["first_name"] == "John"

    def test_passes_last_name_filter_to_repo(self, client):
        repo = mock_player_repo()

        client.get("/v0/players?last_name=Doe")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["last_name"] == "Doe"

    def test_passes_changed_since_filter_to_repo(self, client):
        repo = mock_player_repo()

        client.get("/v0/players?changed_since=2024-06-01")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["changed_since"] == date(2024, 6, 1)

    def test_passes_pagination_to_repo(self, client):
        repo = mock_player_repo()

        client.get("/v0/players?skip=5&limit=10")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["pagination"].skip == 5
        assert call_kwargs["pagination"].limit == 10

    def test_returns_player_fields(self, client):
        player = make_player_entity(
            player_id=7,
            gsis_id="XYZ",
            first_name="Alice",
            last_name="Walker",
            position="WR",
            last_changed_date=date(2025, 3, 1),
        )
        mock_player_repo(PaginatedResult(items=[player], total_count=1))

        response = client.get("/v0/players")

        data = response.json()[0]
        assert data["player_id"] == 7
        assert data["gsis_id"] == "XYZ"
        assert data["first_name"] == "Alice"
        assert data["last_name"] == "Walker"
        assert data["position"] == "WR"
        assert data["last_changed_date"] == "2025-03-01"

    def test_null_gsis_id_serialized_correctly(self, client):
        player = make_player_entity(gsis_id=None)
        mock_player_repo(PaginatedResult(items=[player], total_count=1))

        response = client.get("/v0/players")

        assert response.json()[0]["gsis_id"] is None


class TestGetPlayerById:
    def test_returns_200_when_found(self, client):
        player = make_player_entity(player_id=1, first_name="John", last_name="Doe")
        mock_player_repo(get_by_id_result=player)

        response = client.get("/v0/players/1")

        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == 1
        assert data["first_name"] == "John"

    def test_returns_404_when_not_found(self, client):
        mock_player_repo(get_by_id_result=None)

        response = client.get("/v0/players/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Player not found"

    def test_includes_performances_in_response(self, client):
        performance = make_performance_entity(performance_id=1, week_number="5", fantasy_points=22.5)
        player = make_player_entity(player_id=1, performances=[performance])
        mock_player_repo(get_by_id_result=player)

        response = client.get("/v0/players/1")

        assert response.status_code == 200
        data = response.json()
        assert "performances" in data
        assert len(data["performances"]) == 1
        assert data["performances"][0]["performance_id"] == 1
        assert data["performances"][0]["week_number"] == "5"
        assert data["performances"][0]["fantasy_points"] == 22.5

    def test_calls_repo_with_correct_id(self, client):
        repo = mock_player_repo(get_by_id_result=make_player_entity(player_id=42))

        client.get("/v0/players/42")

        repo.get_by_id.assert_called_once_with(42)

    def test_empty_performances_list_when_none(self, client):
        player = make_player_entity(player_id=1, performances=[])
        mock_player_repo(get_by_id_result=player)

        response = client.get("/v0/players/1")

        assert response.status_code == 200
        assert response.json()["performances"] == []
