"""WebSocket endpoint for real-time notifications (Sprint 2).

Implements WebSocket protocol based on docs/design/websocket-message-protocol.md.
Authentication via Sec-WebSocket-Protocol header (Sprint 1 JWT integration).
"""

import asyncio
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.connection_manager import InMemoryConnectionManager
from app.core.jwt_handler import TokenExpiredError, TokenInvalidError, decode_token
from app.dependencies.auth import is_token_blacklisted, is_user_token_revoked
from app.dependencies.database import get_db
from app.repositories.progress_repository import ProgressRepository
from app.schemas.websocket import MessageType, WSMessage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Global ConnectionManager instance (singleton)
connection_manager = InMemoryConnectionManager(heartbeat_timeout_seconds=90)


@router.on_event("startup")
async def startup_websocket() -> None:
    """Start ConnectionManager heartbeat loop on app startup."""
    await connection_manager.start_heartbeat_loop()
    logger.info("WebSocket ConnectionManager started")


@router.on_event("shutdown")
async def shutdown_websocket() -> None:
    """Stop ConnectionManager heartbeat loop on app shutdown."""
    await connection_manager.stop_heartbeat_loop()
    logger.info("WebSocket ConnectionManager stopped")


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    sec_websocket_protocol: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> None:
    """WebSocket endpoint with JWT authentication via Sec-WebSocket-Protocol.

    Authentication flow (Q2-b decision):
    1. Client sends `Sec-WebSocket-Protocol: bearer.<jwt_token>`
    2. Server extracts token after "bearer." prefix
    3. Server validates JWT using Sprint 1's decode_token()
    4. Server verifies token's user_id matches path parameter
    5. Server accepts connection with subprotocol echo
    6. Server sends welcome message

    Args:
        websocket: FastAPI WebSocket connection
        user_id: User ID from path parameter
        sec_websocket_protocol: WebSocket subprotocol header (contains JWT)

    Close codes:
        4401: AUTH_FAILED (no protocol header or invalid token)
        4403: FORBIDDEN (user_id mismatch)
        1000: Normal closure
    """
    connection = None

    try:
        # Step 1: Extract and validate Sec-WebSocket-Protocol header
        if not sec_websocket_protocol or not sec_websocket_protocol.startswith("bearer."):
            await websocket.close(code=4401, reason="AUTH_FAILED")
            logger.warning(
                f"WebSocket auth failed for {user_id}: missing or invalid protocol header"
            )
            return

        token = sec_websocket_protocol[len("bearer.") :]
        if is_token_blacklisted(token):
            await websocket.close(code=4401, reason="AUTH_FAILED")
            logger.warning(f"WebSocket auth failed for {user_id}: token revoked")
            return

        # Step 2: Validate JWT using Sprint 1
        try:
            payload = decode_token(token, expected_type="access")
            token_user_id = payload.get("sub")
            token_role = payload.get("role", "viewer")
        except (TokenExpiredError, TokenInvalidError) as e:
            await websocket.close(code=4401, reason="AUTH_FAILED")
            logger.warning(f"WebSocket auth failed for {user_id}: {e}")
            return

        token_issued_at = payload.get("issued_at", payload.get("iat"))
        if not token_user_id or is_user_token_revoked(token_user_id, token_issued_at):
            await websocket.close(code=4401, reason="AUTH_FAILED")
            logger.warning(f"WebSocket auth failed for {user_id}: token revoked")
            return

        # Step 3: Verify user_id matches token (prevent privilege escalation)
        if token_user_id != user_id:
            await websocket.close(code=4403, reason="FORBIDDEN")
            logger.warning(
                f"WebSocket auth failed: user_id mismatch (path={user_id}, token={token_user_id})"
            )
            return

        # Step 4: Accept connection with subprotocol echo
        await websocket.accept(subprotocol=sec_websocket_protocol)

        # Step 5: Register connection in ConnectionManager
        connection = await connection_manager.connect(websocket, user_id, accept=False)

        # Step 6: Send welcome message
        welcome_msg = WSMessage(
            type=MessageType.WELCOME,
            data={
                "connection_id": connection.connection_id,
                "user_id": user_id,
                "heartbeat_interval_seconds": 30,
                "server_time": connection.connected_at.isoformat(),
                "protocol_version": "1.0",
            },
        )
        await websocket.send_text(welcome_msg.model_dump_json())
        logger.info(f"WebSocket connection established for user {user_id}")

        # Step 7: Enter message handling loop
        await _handle_messages(connection.connection_id, websocket, user_id, token_role, db)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
    finally:
        if connection:
            await connection_manager.disconnect(connection.connection_id)


async def _handle_messages(
    connection_id: str,
    websocket: WebSocket,
    user_id: str,
    user_role: str,
    db: Session,
) -> None:
    """Handle incoming WebSocket messages (ping, subscribe, unsubscribe, ack).

    Args:
        connection_id: Connection identifier
        websocket: WebSocket connection
        user_id: User identifier
    """
    while True:
        try:
            # Receive message with 120s timeout
            data = await asyncio.wait_for(websocket.receive_text(), timeout=120.0)

            # Parse message
            try:
                import json

                msg_dict = json.loads(data)
                message = WSMessage(**msg_dict)
            except Exception as e:
                logger.warning(f"Invalid message format from {user_id}: {e}")
                error_msg = WSMessage(
                    type=MessageType.SYSTEM_ERROR,
                    data={
                        "code": "INVALID_MESSAGE",
                        "message": f"Invalid message format: {e}",
                        "recoverable": True,
                    },
                )
                await websocket.send_text(error_msg.model_dump_json())
                continue

            # Handle message by type
            if message.type == MessageType.PING:
                await _handle_ping(connection_id, websocket)
            elif message.type == MessageType.SUBSCRIBE:
                await _handle_subscribe(connection_id, websocket, message, user_id, user_role, db)
            elif message.type == MessageType.UNSUBSCRIBE:
                await _handle_unsubscribe(connection_id, websocket, message)
            elif message.type == MessageType.ACK_RESPONSE:
                # ACK tracking not implemented in v1.0 (future enhancement)
                logger.debug(f"Received ACK from {user_id}: {message.data.get('message_id')}")
            else:
                logger.warning(f"Unsupported message type from {user_id}: {message.type}")

        except TimeoutError:
            logger.warning(f"WebSocket timeout for user {user_id} (120s no message)")
            break
        except WebSocketDisconnect:
            break


async def _handle_ping(connection_id: str, websocket: WebSocket) -> None:
    """Handle ping message: update last_ping_at and send pong."""
    await connection_manager.update_ping(connection_id)

    pong_msg = WSMessage(
        type=MessageType.PONG,
        data={"server_time": datetime.now(UTC).isoformat()},
    )
    await websocket.send_text(pong_msg.model_dump_json())


async def _handle_subscribe(
    connection_id: str,
    websocket: WebSocket,
    message: WSMessage,
    user_id: str,
    user_role: str,
    db: Session,
) -> None:
    """Handle subscribe message: add connection to channel."""
    channel = message.data.get("channel")
    if not channel:
        await _send_ws_error(
            websocket,
            code="INVALID_MESSAGE",
            message="Missing 'channel' field in subscribe message",
            recoverable=True,
        )
        return

    if not _is_channel_authorized(channel, user_id, user_role, db):
        await _send_ws_error(
            websocket,
            code="FORBIDDEN",
            message=f"Not authorized to subscribe to channel: {channel}",
            recoverable=True,
        )
        logger.warning(f"User {user_id} denied subscription to {channel}")
        return

    success = await connection_manager.subscribe(connection_id, channel)
    if success:
        logger.debug(f"Connection {connection_id} subscribed to {channel}")
    else:
        logger.warning(f"Failed to subscribe connection {connection_id} to {channel}")


def _is_channel_authorized(
    channel: str,
    user_id: str,
    user_role: str,
    db: Session,
) -> bool:
    """Authorize channel subscriptions for the authenticated WebSocket user."""
    if channel.startswith("progress:"):
        run_id = channel.removeprefix("progress:")
        progress = ProgressRepository(db).get_progress(run_id)
        if not progress:
            return False
        return user_role == "admin" or progress.user_id == user_id

    if channel.startswith("task:"):
        channel_user_id = channel.removeprefix("task:")
        return user_role == "admin" or channel_user_id == user_id

    if channel == "system:broadcast":
        return user_role == "admin"

    return False


async def _send_ws_error(
    websocket: WebSocket,
    code: str,
    message: str,
    recoverable: bool,
) -> None:
    error_msg = WSMessage(
        type=MessageType.SYSTEM_ERROR,
        data={
            "code": code,
            "message": message,
            "recoverable": recoverable,
        },
    )
    await websocket.send_text(error_msg.model_dump_json())


async def _handle_unsubscribe(connection_id: str, websocket: WebSocket, message: WSMessage) -> None:
    """Handle unsubscribe message: remove connection from channel."""
    channel = message.data.get("channel")
    if not channel:
        error_msg = WSMessage(
            type=MessageType.SYSTEM_ERROR,
            data={
                "code": "INVALID_MESSAGE",
                "message": "Missing 'channel' field in unsubscribe message",
                "recoverable": True,
            },
        )
        await websocket.send_text(error_msg.model_dump_json())
        return

    success = await connection_manager.unsubscribe(connection_id, channel)
    if success:
        logger.debug(f"Connection {connection_id} unsubscribed from {channel}")
    else:
        logger.warning(f"Failed to unsubscribe connection {connection_id} from {channel}")


# Utility function for other modules to send messages
async def send_to_user(user_id: str, message: WSMessage) -> int:
    """Send message to all connections of a user.

    Args:
        user_id: Target user ID
        message: WSMessage to send

    Returns:
        Number of connections that received the message
    """
    return await connection_manager.send_to_user(user_id, message)


async def send_to_channel(channel: str, message: WSMessage) -> int:
    """Broadcast message to all subscribers of a channel.

    Args:
        channel: Channel name (e.g., "progress:run_123")
        message: WSMessage to send

    Returns:
        Number of connections that received the message
    """
    return await connection_manager.send_to_channel(channel, message)
