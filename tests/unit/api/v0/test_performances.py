from datetime import date

from domain.value_objects.pagination import PaginatedResult

from .conftest import make_performance_entity, mock_performance_repo


class TestGetPerformances:
    def test_returns_200_with_empty_list(self, client):
        mock_performance_repo(PaginatedResult(items=[], total_count=0))

        response = client.get("/v0/performances")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_200_with_performances(self, client):
        performances = [
            make_performance_entity(performance_id=1, week_number="1", fantasy_points=15.0),
            make_performance_entity(performance_id=2, week_number="2", fantasy_points=22.5),
        ]
        mock_performance_repo(PaginatedResult(items=performances, total_count=2))

        response = client.get("/v0/performances")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["performance_id"] == 1
        assert data[0]["week_number"] == "1"
        assert data[1]["performance_id"] == 2
        assert data[1]["fantasy_points"] == 22.5

    def test_returns_performance_fields(self, client):
        performance = make_performance_entity(
            performance_id=5,
            player_id=3,
            week_number="7",
            fantasy_points=31.25,
            last_changed_date=date(2025, 2, 10),
        )
        mock_performance_repo(PaginatedResult(items=[performance], total_count=1))

        response = client.get("/v0/performances")

        data = response.json()[0]
        assert data["performance_id"] == 5
        assert data["player_id"] == 3
        assert data["week_number"] == "7"
        assert data["fantasy_points"] == 31.25
        assert data["last_changed_date"] == "2025-02-10"

    def test_passes_player_id_filter_to_repo(self, client):
        repo = mock_performance_repo()

        client.get("/v0/performances?player_id=42")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["playerid"] == 42

    def test_passes_week_number_filter_to_repo(self, client):
        repo = mock_performance_repo()

        client.get("/v0/performances?week_number=5")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["week_number"] == "5"

    def test_passes_changed_since_filter_to_repo(self, client):
        repo = mock_performance_repo()

        client.get("/v0/performances?changed_since=2024-09-01")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["changed_since"] == date(2024, 9, 1)

    def test_passes_pagination_to_repo(self, client):
        repo = mock_performance_repo()

        client.get("/v0/performances?skip=10&limit=5")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["pagination"].skip == 10
        assert call_kwargs["pagination"].limit == 5

    def test_no_filters_calls_repo_with_none_values(self, client):
        repo = mock_performance_repo()

        client.get("/v0/performances")

        repo.search.assert_called_once()
        call_kwargs = repo.search.call_args.kwargs
        assert call_kwargs["playerid"] is None
        assert call_kwargs["week_number"] is None
        assert call_kwargs["changed_since"] is None
