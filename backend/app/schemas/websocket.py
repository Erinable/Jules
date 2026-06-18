"""WebSocket message schemas (Sprint 2).

Defines the message envelope and types for WebSocket communication.
Based on docs/design/websocket-message-protocol.md.

All models are immutable (frozen=True) per project coding standards.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MessageType(str, Enum):
    """All WebSocket message types."""

    # Server → Client
    AGENT_STATUS = "agent.status"
    CODE_CHUNK = "code.chunk"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    SYSTEM_ERROR = "system.error"
    PONG = "pong"
    ACK = "ack"
    WELCOME = "welcome"

    # Client → Server
    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ACK_RESPONSE = "ack.response"

    # Sprint 3 integration (progress tracking)
    PROGRESS_STEP_STARTED = "progress.step.started"
    PROGRESS_STEP_COMPLETED = "progress.step.completed"
    PROGRESS_STEP_FAILED = "progress.step.failed"
    PROGRESS_UPDATED = "progress.updated"
    PROGRESS_LOG_APPENDED = "progress.log.appended"


class WSMessage(BaseModel):
    """WebSocket message envelope (immutable).

    All WebSocket messages follow this unified structure:
    - type: event type (see MessageType enum)
    - data: event payload (structure depends on type)
    - timestamp: message creation time (UTC)
    - id: unique message identifier (UUID)
    - ack_required: whether client acknowledgment is required (default false)
    """

    model_config = ConfigDict(frozen=True, use_enum_values=True)

    type: MessageType
    data: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ack_required: bool = False
