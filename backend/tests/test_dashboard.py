"""Tests for dashboard API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


def test_dashboard_health(client):
    response = client.get("/api/dashboard/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "dashboard"
    assert "timestamp" in data


def test_dashboard_active_requires_auth(client):
    response = client.get("/api/dashboard/active")
    assert response.status_code == 422


def test_dashboard_metrics_requires_auth(client):
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 422


def test_dashboard_timeline_requires_auth(client):
    response = client.get("/api/dashboard/timeline")
    assert response.status_code == 422


def test_dashboard_active(auth_client):
    with patch("app.services.heartbeat.supabase") as mock_db:
        mock_result = MagicMock()
        mock_result.data = []
        mock_db.table.return_value.select.return_value.in_.return_value.order.return_value.execute.return_value = mock_result

        response = auth_client.get(
            "/api/dashboard/active",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200
        assert response.json() == []


def test_dashboard_metrics(auth_client):
    with patch("app.services.heartbeat.supabase") as mock_db:
        mock_active = MagicMock()
        mock_active.count = 2
        mock_active.data = []
        mock_today = MagicMock()
        mock_today.count = 5
        mock_today.data = [{"tokens_used": 100, "cost_estimate": 0.01}]
        mock_agents = MagicMock()
        mock_agents.count = 3
        mock_agents.data = []

        def table_side_effect(name):
            mock_table = MagicMock()
            if name == "agent_heartbeats":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_active
                mock_table.select.return_value.gte.return_value.execute.return_value = mock_today
            elif name == "agents":
                mock_table.select.return_value.execute.return_value = mock_agents
            return mock_table

        mock_db.table.side_effect = table_side_effect

        response = auth_client.get(
            "/api/dashboard/metrics",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "active_runs" in data
        assert "total_agents" in data
        assert "tokens_today" in data
        assert "cost_today" in data


def test_dashboard_timeline(auth_client):
    with patch("app.routers.dashboard.supabase") as mock_db:
        mock_result = MagicMock()
        mock_result.data = []
        mock_db.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_result

        response = auth_client.get(
            "/api/dashboard/timeline",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200
        assert response.json() == []
