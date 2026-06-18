"""WebSocket ConnectionManager (Sprint 2).

Manages WebSocket connections, user routing, and channel subscriptions.
Based on docs/design/websocket-connection-manager.md.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi import WebSocket

from app.schemas.websocket import WSMessage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Connection:
    """Immutable WebSocket connection record."""

    connection_id: str
    user_id: str
    websocket: WebSocket
    connected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_ping_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ConnectionManager(ABC):
    """Abstract base class for WebSocket connection management."""

    @abstractmethod
    async def connect(self, websocket: WebSocket, user_id: str, accept: bool = True) -> Connection:
        """Accept and register a new WebSocket connection."""

    @abstractmethod
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect and cleanup a connection."""

    @abstractmethod
    async def send_to_user(self, user_id: str, message: WSMessage) -> int:
        """Send message to all connections of a user. Returns connection count."""

    @abstractmethod
    async def send_to_channel(self, channel: str, message: WSMessage) -> int:
        """Broadcast message to all subscribers of a channel. Returns connection count."""

    @abstractmethod
    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Subscribe a connection to a channel. Returns success status."""

    @abstractmethod
    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe a connection from a channel. Returns success status."""

    @abstractmethod
    async def update_ping(self, connection_id: str) -> bool:
        """Update last_ping_at timestamp. Returns success status."""

    @abstractmethod
    def get_stats(self) -> dict:
        """Get connection statistics."""


class InMemoryConnectionManager(ConnectionManager):
    """In-memory WebSocket connection manager.

    Manages up to 100 concurrent connections using three indexes:
    - _connections: connection_id → Connection
    - _user_connections: user_id → set[connection_id]
    - _channel_subscriptions: channel → set[connection_id]

    Heartbeat: ping every 30s, check every 60s, timeout at 90s.
    """

    def __init__(self, heartbeat_timeout_seconds: int = 90):
        self._connections: dict[str, Connection] = {}
        self._user_connections: dict[str, set[str]] = {}
        self._channel_subscriptions: dict[str, set[str]] = {}
        self._lock = asyncio.Lock()
        self._heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self._heartbeat_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket, user_id: str, accept: bool = True) -> Connection:
        """Accept and register a new WebSocket connection."""
        if accept:
            await websocket.accept()

        import uuid

        connection_id = str(uuid.uuid4())
        connection = Connection(
            connection_id=connection_id,
            user_id=user_id,
            websocket=websocket,
        )

        async with self._lock:
            self._connections[connection_id] = connection
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(connection_id)

        logger.info(f"Connection {connection_id} established for user {user_id}")
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect and cleanup a connection."""
        async with self._lock:
            connection = self._connections.pop(connection_id, None)
            if not connection:
                return

            # Remove from user_connections index
            user_conns = self._user_connections.get(connection.user_id, set())
            user_conns.discard(connection_id)
            if not user_conns:
                self._user_connections.pop(connection.user_id, None)

            # Remove from all channel subscriptions
            for channel, subscribers in list(self._channel_subscriptions.items()):
                subscribers.discard(connection_id)
                if not subscribers:
                    self._channel_subscriptions.pop(channel, None)

        # Close WebSocket outside lock
        try:
            await connection.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing websocket {connection_id}: {e}")

        logger.info(f"Connection {connection_id} disconnected")

    async def send_to_user(self, user_id: str, message: WSMessage) -> int:
        """Send message to all connections of a user."""
        async with self._lock:
            connection_ids = self._user_connections.get(user_id, set()).copy()

        if not connection_ids:
            return 0

        tasks = [self._send_message(conn_id, message) for conn_id in connection_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        return success_count

    async def send_to_channel(self, channel: str, message: WSMessage) -> int:
        """Broadcast message to all subscribers of a channel."""
        async with self._lock:
            connection_ids = self._channel_subscriptions.get(channel, set()).copy()

        if not connection_ids:
            return 0

        tasks = [self._send_message(conn_id, message) for conn_id in connection_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        return success_count

    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Subscribe a connection to a channel."""
        async with self._lock:
            if connection_id not in self._connections:
                return False

            if channel not in self._channel_subscriptions:
                self._channel_subscriptions[channel] = set()
            self._channel_subscriptions[channel].add(connection_id)

        logger.debug(f"Connection {connection_id} subscribed to channel {channel}")
        return True

    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe a connection from a channel."""
        async with self._lock:
            if channel not in self._channel_subscriptions:
                return False

            self._channel_subscriptions[channel].discard(connection_id)
            if not self._channel_subscriptions[channel]:
                self._channel_subscriptions.pop(channel, None)

        logger.debug(f"Connection {connection_id} unsubscribed from channel {channel}")
        return True

    async def update_ping(self, connection_id: str) -> bool:
        """Update last_ping_at timestamp."""
        async with self._lock:
            connection = self._connections.get(connection_id)
            if not connection:
                return False

            # Replace with new Connection (immutable)
            updated = Connection(
                connection_id=connection.connection_id,
                user_id=connection.user_id,
                websocket=connection.websocket,
                connected_at=connection.connected_at,
                last_ping_at=datetime.now(UTC),
            )
            self._connections[connection_id] = updated

        return True

    def get_stats(self) -> dict:
        """Get connection statistics."""
        total_connections = len(self._connections)
        unique_users = len(self._user_connections)
        channels_count = len(self._channel_subscriptions)

        # Top users by connection count
        top_users = sorted(self._user_connections.items(), key=lambda x: len(x[1]), reverse=True)[
            :10
        ]

        return {
            "total_connections": total_connections,
            "unique_users": unique_users,
            "channels_count": channels_count,
            "top_users": [
                {"user_id": user_id, "connections": len(conn_ids)}
                for user_id, conn_ids in top_users
            ],
        }

    async def _send_message(self, connection_id: str, message: WSMessage) -> bool:
        """Send message to a single connection. Returns success status."""
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        try:
            json_str = message.model_dump_json()
            await asyncio.wait_for(connection.websocket.send_text(json_str), timeout=5.0)
            return True
        except TimeoutError:
            logger.warning(f"Timeout sending to connection {connection_id}")
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False

    async def start_heartbeat_loop(self) -> None:
        """Start background heartbeat cleanup loop."""
        if self._heartbeat_task:
            return

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Heartbeat loop started")

    async def stop_heartbeat_loop(self) -> None:
        """Stop background heartbeat cleanup loop."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            logger.info("Heartbeat loop stopped")

    async def _heartbeat_loop(self) -> None:
        """Background loop to cleanup stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every 60s
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

    async def _cleanup_stale_connections(self) -> None:
        """Remove connections that haven't pinged within timeout."""
        now = datetime.now(UTC)
        stale_ids = []

        async with self._lock:
            for conn_id, conn in self._connections.items():
                elapsed = (now - conn.last_ping_at).total_seconds()
                if elapsed > self._heartbeat_timeout_seconds:
                    stale_ids.append(conn_id)

        for conn_id in stale_ids:
            logger.info(f"Cleaning up stale connection {conn_id}")
            await self.disconnect(conn_id)
