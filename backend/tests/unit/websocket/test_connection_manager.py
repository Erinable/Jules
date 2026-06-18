"""Unit tests for WebSocket ConnectionManager (Sprint 2).

Tests are based on the ConnectionManager design documented in
docs/design/websocket-connection-manager.md.

Run: pytest tests/unit/websocket/test_connection_manager.py -v
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.connection_manager import Connection, InMemoryConnectionManager
from app.schemas.websocket import MessageType, WSMessage

pytestmark = pytest.mark.asyncio


class TestConnectionLifecycle:
    """Tests for connection connect/disconnect lifecycle."""

    async def test_connect_adds_to_pool(self):
        """Test: WebSocket 连接成功后加入连接池"""
        # Arrange
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()

        # Act
        conn = await manager.connect(mock_ws, user_id="user-123")

        # Assert
        assert conn.user_id == "user-123"
        assert conn.connection_id in manager._connections
        assert "user-123" in manager._user_connections
        mock_ws.accept.assert_called_once()

    async def test_disconnect_removes_from_pool(self):
        """Test: 断开连接后从池中移除"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.close = AsyncMock()
        conn = await manager.connect(mock_ws, user_id="user-1")

        await manager.disconnect(conn.connection_id)

        assert conn.connection_id not in manager._connections
        assert conn.connection_id not in manager._user_connections.get("user-1", set())

    async def test_disconnect_already_disconnected_is_noop(self):
        """Test: 重复断开已不存在的连接应静默"""
        manager = InMemoryConnectionManager()
        # Should not raise exception
        await manager.disconnect("nonexistent-id")

    async def test_disconnect_closes_websocket(self):
        """Test: 断开时调用 websocket.close()"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.close = AsyncMock()
        conn = await manager.connect(mock_ws, user_id="user-1")

        await manager.disconnect(conn.connection_id)

        mock_ws.close.assert_called_once()


class TestUserRouting:
    """Tests for user_id-based message routing."""

    async def test_send_to_user_single_connection(self):
        """Test: 向单连接用户推送消息"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        await manager.connect(mock_ws, "user-1")

        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("user-1", msg)

        assert count == 1
        mock_ws.send_text.assert_called_once()

    async def test_send_to_user_multiple_connections(self):
        """Test: 同一用户多设备连接，全部收到消息"""
        manager = InMemoryConnectionManager()
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        await manager.connect(ws1, "user-1")
        await manager.connect(ws2, "user-1")

        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("user-1", msg)

        assert count == 2
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    async def test_send_to_nonexistent_user_returns_zero(self):
        """Test: 向不存在用户推送返回 0"""
        manager = InMemoryConnectionManager()
        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("nonexistent-user", msg)
        assert count == 0

    async def test_multi_user_isolation(self):
        """Test: 用户 A 不收到用户 B 的消息"""
        manager = InMemoryConnectionManager()
        ws_a = MagicMock()
        ws_a.accept = AsyncMock()
        ws_a.send_text = AsyncMock()
        ws_b = MagicMock()
        ws_b.accept = AsyncMock()
        ws_b.send_text = AsyncMock()
        await manager.connect(ws_a, "user-a")
        await manager.connect(ws_b, "user-b")

        msg = WSMessage(type=MessageType.PING, data={})
        await manager.send_to_user("user-a", msg)

        ws_a.send_text.assert_called_once()
        ws_b.send_text.assert_not_called()


class TestChannelSubscription:
    """Tests for channel-based pub/sub."""

    async def test_subscribe_to_channel(self):
        """Test: 订阅 channel 后能收到该 channel 消息"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        await manager.subscribe(conn.connection_id, "progress:run_123")
        msg = WSMessage(type=MessageType.PROGRESS_UPDATED, data={})
        count = await manager.send_to_channel("progress:run_123", msg)

        assert count == 1
        mock_ws.send_text.assert_called_once()

    async def test_unsubscribe_from_channel(self):
        """Test: 退订后不再收到 channel 消息"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        await manager.subscribe(conn.connection_id, "progress:run_123")
        await manager.unsubscribe(conn.connection_id, "progress:run_123")
        msg = WSMessage(type=MessageType.PROGRESS_UPDATED, data={})
        count = await manager.send_to_channel("progress:run_123", msg)

        assert count == 0
        mock_ws.send_text.assert_not_called()

    async def test_broadcast_to_channel_only(self):
        """Test: 广播仅送达订阅该 channel 的连接"""
        manager = InMemoryConnectionManager()
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        conn1 = await manager.connect(ws1, "user-1")
        conn2 = await manager.connect(ws2, "user-2")

        await manager.subscribe(conn1.connection_id, "progress:run_123")
        # conn2 not subscribed

        msg = WSMessage(type=MessageType.PROGRESS_UPDATED, data={})
        count = await manager.send_to_channel("progress:run_123", msg)

        assert count == 1
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_not_called()

    async def test_disconnect_auto_unsubscribes_all_channels(self):
        """Test: 断开时自动从所有 channel 移除"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.close = AsyncMock()
        mock_ws.send_text = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        await manager.subscribe(conn.connection_id, "channel-1")
        await manager.subscribe(conn.connection_id, "channel-2")
        await manager.disconnect(conn.connection_id)

        msg = WSMessage(type=MessageType.PING, data={})
        count1 = await manager.send_to_channel("channel-1", msg)
        count2 = await manager.send_to_channel("channel-2", msg)

        assert count1 == 0
        assert count2 == 0


class TestHeartbeat:
    """Tests for heartbeat/ping-pong mechanism."""

    async def test_heartbeat_timeout_disconnects(self):
        """Test: 心跳超时的连接应被清理"""
        manager = InMemoryConnectionManager(heartbeat_timeout_seconds=90)
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.close = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        # Simulate stale connection (91s old ping)

        stale_conn = Connection(
            connection_id=conn.connection_id,
            user_id=conn.user_id,
            websocket=conn.websocket,
            connected_at=conn.connected_at,
            last_ping_at=datetime.now(UTC) - timedelta(seconds=91),
        )
        manager._connections[conn.connection_id] = stale_conn

        await manager._cleanup_stale_connections()

        assert conn.connection_id not in manager._connections

    async def test_alive_connection_not_cleaned(self):
        """Test: 活跃连接不被心跳清理"""
        manager = InMemoryConnectionManager(heartbeat_timeout_seconds=90)
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        await manager._cleanup_stale_connections()

        assert conn.connection_id in manager._connections

    async def test_ping_updates_last_ping_at(self):
        """Test: 收到 ping 后更新 last_ping_at"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        conn = await manager.connect(mock_ws, "user-1")

        original_ping_at = manager._connections[conn.connection_id].last_ping_at

        import asyncio

        await asyncio.sleep(0.01)  # Small delay
        await manager.update_ping(conn.connection_id)

        updated_ping_at = manager._connections[conn.connection_id].last_ping_at
        assert updated_ping_at > original_ping_at


class TestErrorHandling:
    """Tests for error scenarios."""

    async def test_send_to_dead_connection_triggers_cleanup(self):
        """Test: 推送到已断开的连接时清理资源"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock(side_effect=Exception("Connection closed"))
        conn = await manager.connect(mock_ws, "user-1")

        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("user-1", msg)

        assert count == 0
        assert conn.connection_id not in manager._connections

    async def test_send_with_timeout(self):
        """Test: 推送 5s 超时后清理"""
        manager = InMemoryConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()

        async def slow_send(text):
            import asyncio

            await asyncio.sleep(6)  # Exceeds 5s timeout

        mock_ws.send_text = AsyncMock(side_effect=slow_send)
        conn = await manager.connect(mock_ws, "user-1")

        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("user-1", msg)

        assert count == 0
        assert conn.connection_id not in manager._connections

    async def test_concurrent_send_failure_isolated(self):
        """Test: 单连接失败不影响其他连接"""
        manager = InMemoryConnectionManager()
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock(side_effect=Exception("Fail"))
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        ws3 = MagicMock()
        ws3.accept = AsyncMock()
        ws3.send_text = AsyncMock()

        conn1 = await manager.connect(ws1, "user-1")
        conn2 = await manager.connect(ws2, "user-1")
        conn3 = await manager.connect(ws3, "user-1")

        msg = WSMessage(type=MessageType.PING, data={})
        count = await manager.send_to_user("user-1", msg)

        # 2 out of 3 succeed
        assert count == 2
        # Failed connection removed
        assert conn1.connection_id not in manager._connections
        assert conn2.connection_id in manager._connections
        assert conn3.connection_id in manager._connections


class TestConcurrency:
    """Load tests for concurrent connections."""

    async def test_100_concurrent_connections(self):
        """Test: 100 并发连接建立 < 2s"""
        import time

        manager = InMemoryConnectionManager()
        start = time.time()

        tasks = []
        for i in range(100):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            tasks.append(manager.connect(mock_ws, f"user-{i}"))

        import asyncio

        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        assert len(manager._connections) == 100
        assert elapsed < 2.0

    async def test_broadcast_to_100_connections(self):
        """Test: 广播到 100 连接 < 500ms"""
        import time

        manager = InMemoryConnectionManager()

        # Create 100 connections
        for i in range(100):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_text = AsyncMock()
            conn = await manager.connect(mock_ws, f"user-{i}")
            await manager.subscribe(conn.connection_id, "broadcast")

        msg = WSMessage(type=MessageType.PING, data={})
        start = time.time()
        count = await manager.send_to_channel("broadcast", msg)
        elapsed = time.time() - start

        assert count == 100
        assert elapsed < 0.5

    async def test_concurrent_connect_disconnect_safe(self):
        """Test: 并发 connect/disconnect 无 race condition"""
        import asyncio

        manager = InMemoryConnectionManager()

        async def connect_task(i):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            return await manager.connect(mock_ws, f"user-{i}")

        async def disconnect_task(conn):
            await asyncio.sleep(0.001)  # Small delay
            await manager.disconnect(conn.connection_id)

        # 50 connect + 50 disconnect concurrently
        connect_tasks = [connect_task(i) for i in range(50)]
        connections = await asyncio.gather(*connect_tasks)
        disconnect_tasks = [disconnect_task(conn) for conn in connections[:25]]

        await asyncio.gather(*disconnect_tasks)

        # 25 connections remain
        assert len(manager._connections) == 25


class TestStats:
    """Tests for observability."""

    async def test_get_stats_returns_correct_counts(self):
        """Test: 统计数据准确"""
        manager = InMemoryConnectionManager()

        # 3 users, 5 connections
        for i in range(2):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            conn = await manager.connect(mock_ws, "user-1")
            await manager.subscribe(conn.connection_id, "channel-1")

        for i in range(2):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            conn = await manager.connect(mock_ws, "user-2")
            await manager.subscribe(conn.connection_id, "channel-2")

        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        await manager.connect(mock_ws, "user-3")

        stats = manager.get_stats()

        assert stats["total_connections"] == 5
        assert stats["unique_users"] == 3
        assert stats["channels_count"] == 2

    async def test_stats_top_users_by_connections(self):
        """Test: top users 排序正确"""
        manager = InMemoryConnectionManager()

        # user-1: 3 connections
        for i in range(3):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            await manager.connect(mock_ws, "user-1")

        # user-2: 2 connections
        for i in range(2):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            await manager.connect(mock_ws, "user-2")

        # user-3: 1 connection
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        await manager.connect(mock_ws, "user-3")

        stats = manager.get_stats()
        top_users = stats["top_users"]

        assert len(top_users) == 3
        assert top_users[0]["user_id"] == "user-1"
        assert top_users[0]["connections"] == 3
        assert top_users[1]["user_id"] == "user-2"
        assert top_users[1]["connections"] == 2
        assert top_users[2]["user_id"] == "user-3"
        assert top_users[2]["connections"] == 1
