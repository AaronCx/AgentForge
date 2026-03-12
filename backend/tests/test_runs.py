"""Tests for runs API endpoints."""

from unittest.mock import MagicMock

from tests.conftest import _mock_supabase_client


class TestRunRoutes:
    """Test run API endpoints."""

    def test_list_runs(self, auth_client):
        """GET /api/runs returns user runs."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "r1", "agent_id": "a1", "user_id": "test-user-id-123",
                    "status": "completed", "input_text": "hi", "output": "hello",
                    "tokens_used": 10, "duration_ms": 100, "step_logs": [],
                    "input_file_url": None, "created_at": "2026-03-12T00:00:00Z",
                },
            ]
        )
        r = auth_client.get("/api/runs")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id"] == "r1"

    def test_get_run(self, auth_client):
        """GET /api/runs/{id} returns a specific run."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "r1", "agent_id": "a1", "user_id": "test-user-id-123",
                "status": "completed", "input_text": "hi", "output": "hello",
                "tokens_used": 10, "duration_ms": 100, "step_logs": [],
                "input_file_url": None, "created_at": "2026-03-12T00:00:00Z",
            }
        )
        r = auth_client.get("/api/runs/r1")
        assert r.status_code == 200
        assert r.json()["id"] == "r1"

    def test_get_run_not_found(self, auth_client):
        """GET /api/runs/{id} returns 404 when not found."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )
        r = auth_client.get("/api/runs/nonexistent")
        assert r.status_code == 404

    def test_get_run_wrong_user(self, auth_client):
        """GET /api/runs/{id} returns 404 for another user's run."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "r1", "agent_id": "a1", "user_id": "different-user",
                "status": "completed", "input_text": "hi", "output": "hello",
                "tokens_used": 10, "duration_ms": 100, "step_logs": [],
                "created_at": "2026-03-12T00:00:00Z",
            }
        )
        r = auth_client.get("/api/runs/r1")
        assert r.status_code == 404

    def test_get_stats(self, auth_client):
        """GET /api/stats returns aggregate stats."""
        # Agents count
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            count=5, data=[{"tokens_used": 100}]
        )
        # Recent runs
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = MagicMock(
            count=2
        )
        r = auth_client.get("/api/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_agents" in data
        assert "total_runs" in data
        assert "runs_this_hour" in data
