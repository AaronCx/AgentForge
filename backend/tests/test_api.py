import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AgentForge API"
    assert data["status"] == "running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agents_requires_auth(client):
    response = client.get("/api/agents")
    assert response.status_code == 422  # Missing authorization header


def test_runs_requires_auth(client):
    response = client.get("/api/runs")
    assert response.status_code == 422


def test_keys_requires_auth(client):
    response = client.get("/api/keys")
    assert response.status_code == 422
