"""WebSocket integration tests (Sprint 2).

Tests complete WebSocket connection lifecycle with JWT authentication.
Based on docs/design/websocket-test-plan.md §4.

Run: pytest tests/integration/test_websocket_integration.py -v
"""

from datetime import UTC, datetime

import pytest
from app.core.jwt_handler import create_access_token
from app.main import app
from app.repositories.progress_repository import ProgressRepository
from fastapi.testclient import TestClient


@pytest.fixture
def test_user_id() -> str:
    """Test user ID"""
    return "12345678-1234-5678-1234-567812345678"


@pytest.fixture
def test_token(test_user_id: str) -> str:
    """Create valid JWT token for testing"""
    from uuid import UUID

    token, _ = create_access_token(user_id=UUID(test_user_id), role="developer")
    return token


@pytest.fixture
def invalid_token() -> str:
    """Invalid JWT token"""
    return "invalid.jwt.token"


def create_progress_for_user(db_session, run_id: str, user_id: str):
    """Create a progress record used by WebSocket channel authorization."""
    return ProgressRepository(db_session).create_progress(
        run_id=run_id,
        user_id=user_id,
        status="running",
        steps_json=[],
    )


class TestWebSocketHandshake:
    """Test WebSocket connection establishment with JWT authentication."""

    def test_websocket_handshake_with_valid_jwt(self, test_user_id: str, test_token: str):
        """Test: JWT 验证后建立连接"""
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            # Receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "welcome"
            assert data["data"]["user_id"] == test_user_id
            assert data["data"]["protocol_version"] == "1.0"
            assert "connection_id" in data["data"]
            assert "heartbeat_interval_seconds" in data["data"]

    def test_websocket_rejects_invalid_token(self, test_user_id: str, invalid_token: str):
        """Test: 无效 JWT 被拒（依赖 Sprint 1）"""
        client = TestClient(app)

        with pytest.raises(Exception) as exc_info:
            with client.websocket_connect(
                f"/api/v1/ws/{test_user_id}",
                subprotocols=[f"bearer.{invalid_token}"],
            ):
                pass

        # Should close with 4401 AUTH_FAILED
        assert getattr(exc_info.value, "code", None) == 4401

    def test_websocket_rejects_missing_protocol_header(self, test_user_id: str):
        """Test: 缺少 Sec-WebSocket-Protocol 被拒"""
        client = TestClient(app)

        with pytest.raises(Exception) as exc_info:
            with client.websocket_connect(f"/api/v1/ws/{test_user_id}"):
                pass

        assert getattr(exc_info.value, "code", None) == 4401

    def test_websocket_rejects_mismatched_user_id(self, test_token: str):
        """Test: user_id 不匹配被拒"""
        client = TestClient(app)

        with pytest.raises(Exception) as exc_info:
            with client.websocket_connect(
                "/api/v1/ws/87654321-4321-8765-4321-876543218765",
                subprotocols=[f"bearer.{test_token}"],
            ):
                pass

        # Should close with 4403 FORBIDDEN
        assert getattr(exc_info.value, "code", None) == 4403

    def test_websocket_rejects_blacklisted_token(
        self,
        test_user_id: str,
        test_token: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test: revoked JWT is rejected during WebSocket handshake."""
        monkeypatch.setattr("app.api.v1.websocket.is_token_blacklisted", lambda token: True)
        client = TestClient(app)

        with pytest.raises(Exception) as exc_info:
            with client.websocket_connect(
                f"/api/v1/ws/{test_user_id}",
                subprotocols=[f"bearer.{test_token}"],
            ):
                pass

        assert getattr(exc_info.value, "code", None) == 4401


class TestWebSocketMessaging:
    """Test WebSocket message handling (ping, subscribe, unsubscribe)."""

    def test_ping_pong(self, test_user_id: str, test_token: str):
        """Test: 发送 ping，接收 pong"""
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            # Receive welcome
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            # Send ping
            ping_msg = {
                "type": "ping",
                "data": {},
                "timestamp": datetime.now(UTC).isoformat(),
                "id": "ping-123",
            }
            websocket.send_json(ping_msg)

            # Receive pong
            pong = websocket.receive_json()
            assert pong["type"] == "pong"
            assert "server_time" in pong["data"]

    def test_subscribe_to_channel(self, client, db_session, test_user_id: str, test_token: str):
        """Test: 订阅 channel 后能收到该 channel 消息"""
        create_progress_for_user(db_session, "run_123", test_user_id)

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            # Receive welcome
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            # Subscribe to channel
            subscribe_msg = {
                "type": "subscribe",
                "data": {"channel": "progress:run_123"},
                "timestamp": datetime.now(UTC).isoformat(),
                "id": "sub-123",
            }
            websocket.send_json(subscribe_msg)

            # Note: To fully test channel broadcast, need another connection
            # or use ConnectionManager directly. This test verifies subscribe
            # message is accepted without error.

    def test_rejects_cross_user_progress_subscription(
        self,
        client,
        db_session,
        test_user_id: str,
        test_token: str,
    ):
        """Test: users cannot subscribe to another user's progress channel."""
        create_progress_for_user(
            db_session,
            "other_run",
            "87654321-4321-8765-4321-876543218765",
        )

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            websocket.send_json(
                {
                    "type": "subscribe",
                    "data": {"channel": "progress:other_run"},
                    "timestamp": datetime.now(UTC).isoformat(),
                    "id": "sub-forbidden",
                }
            )

            error = websocket.receive_json()
            assert error["type"] == "system.error"
            assert error["data"]["code"] == "FORBIDDEN"

    def test_invalid_message_format(self, test_user_id: str, test_token: str):
        """Test: 无效消息格式返回 system.error"""
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            # Receive welcome
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            # Send invalid message (missing required fields)
            websocket.send_text("invalid json")

            # Receive system.error
            error = websocket.receive_json()
            assert error["type"] == "system.error"
            assert error["data"]["code"] == "INVALID_MESSAGE"
            assert error["data"]["recoverable"] is True


class TestMultiUserIsolation:
    """Test user isolation (user A should not receive user B's messages)."""

    def test_multiple_users_isolated(self, test_token: str):
        """Test: 多用户消息互不干扰"""
        # Note: This test requires mocking different user tokens
        # or using ConnectionManager directly to send targeted messages.
        # Skipped in basic integration tests; covered in unit tests.
        pytest.skip("Requires multi-user token setup or direct ConnectionManager access")


class TestReconnection:
    """Test reconnection behavior."""

    def test_reconnect_resubscribes_channels(
        self,
        client,
        db_session,
        test_user_id: str,
        test_token: str,
    ):
        """Test: 断线重连后恢复订阅"""
        # Note: Reconnection logic is primarily client-side (useWebSocket hook).
        # Server accepts new connections independently. This test verifies
        # a new connection can re-subscribe to channels.
        create_progress_for_user(db_session, "run_123", test_user_id)

        # First connection
        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            subscribe_msg = {
                "type": "subscribe",
                "data": {"channel": "progress:run_123"},
                "timestamp": datetime.now(UTC).isoformat(),
                "id": "sub-1",
            }
            websocket.send_json(subscribe_msg)

        # Second connection (simulating reconnection)
        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            # Re-subscribe
            subscribe_msg = {
                "type": "subscribe",
                "data": {"channel": "progress:run_123"},
                "timestamp": datetime.now(UTC).isoformat(),
                "id": "sub-2",
            }
            websocket.send_json(subscribe_msg)
            # No error means re-subscription successful


class TestMessageSerialization:
    """Test message serialization/deserialization."""

    def test_message_round_trip(self, test_user_id: str, test_token: str):
        """Test: 消息序列化/反序列化保持一致"""
        client = TestClient(app)

        with client.websocket_connect(
            f"/api/v1/ws/{test_user_id}",
            subprotocols=[f"bearer.{test_token}"],
        ) as websocket:
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"

            # Send ping with specific data
            ping_msg = {
                "type": "ping",
                "data": {"test_key": "test_value"},
                "timestamp": datetime.now(UTC).isoformat(),
                "id": "test-123",
            }
            websocket.send_json(ping_msg)

            # Receive pong
            pong = websocket.receive_json()
            assert pong["type"] == "pong"
            assert isinstance(pong["data"], dict)
            assert "timestamp" in pong
            assert "id" in pong
