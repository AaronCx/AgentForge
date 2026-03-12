"""Tests for message API endpoints."""

from unittest.mock import MagicMock

from tests.conftest import _mock_supabase_client


class TestMessageRoutes:
    """Test message API endpoints."""

    def _mock_group_exists(self):
        """Mock a successful group lookup."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "g1"}
        )

    def _mock_group_not_found(self):
        """Mock a failed group lookup."""
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )

    def test_send_message(self, auth_client):
        """POST /api/messages sends a message."""
        self._mock_group_exists()
        _mock_supabase_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "m1",
                "group_id": "g1",
                "sender_index": 0,
                "receiver_index": 1,
                "message_type": "info",
                "content": "Hello agent 2",
            }]
        )
        r = auth_client.post("/api/messages", json={
            "group_id": "g1",
            "sender_index": 0,
            "receiver_index": 1,
            "content": "Hello agent 2",
        })
        assert r.status_code == 200
        assert r.json()["content"] == "Hello agent 2"

    def test_send_message_group_not_found(self, auth_client):
        """POST /api/messages returns 404 for unknown group."""
        self._mock_group_not_found()
        r = auth_client.post("/api/messages", json={
            "group_id": "nonexistent",
            "sender_index": 0,
            "content": "Hello",
        })
        assert r.status_code == 404

    def test_get_messages(self, auth_client):
        """GET /api/messages/{group_id} returns messages."""
        self._mock_group_exists()
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "m1", "sender_index": 0, "content": "msg1", "message_type": "info"},
                {"id": "m2", "sender_index": 1, "content": "msg2", "message_type": "response"},
            ]
        )
        r = auth_client.get("/api/messages/g1")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2

    def test_get_messages_group_not_found(self, auth_client):
        """GET /api/messages/{group_id} returns 404 for unknown group."""
        self._mock_group_not_found()
        r = auth_client.get("/api/messages/nonexistent")
        assert r.status_code == 404

    def test_get_conversation(self, auth_client):
        """GET /api/messages/{group_id}/conversation returns bilateral messages."""
        self._mock_group_exists()
        _mock_supabase_client.table.return_value.select.return_value.eq.return_value.or_.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "m1", "sender_index": 0, "receiver_index": 1, "content": "hello"},
                {"id": "m2", "sender_index": 1, "receiver_index": 0, "content": "hi back"},
            ]
        )
        r = auth_client.get("/api/messages/g1/conversation?agent_a=0&agent_b=1")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2

    def test_get_conversation_group_not_found(self, auth_client):
        """GET /api/messages/{group_id}/conversation returns 404 for unknown group."""
        self._mock_group_not_found()
        r = auth_client.get("/api/messages/nonexistent/conversation?agent_a=0&agent_b=1")
        assert r.status_code == 404
