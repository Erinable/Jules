"""Unit tests for WebSocket message protocol (Sprint 2).

Tests are based on the message protocol documented in
docs/design/websocket-message-protocol.md.

Run: pytest tests/unit/websocket/test_message_protocol.py -v
"""

import json
from datetime import UTC, datetime

import pytest

from app.schemas.websocket import MessageType, WSMessage

pytestmark = pytest.mark.asyncio


class TestMessageEnvelope:
    """Tests for WSMessage envelope structure."""

    def test_message_has_required_fields(self):
        """Test: WSMessage 包含 type/data/timestamp/id 字段"""
        msg = WSMessage(
            type=MessageType.AGENT_STATUS,
            data={"agent_id": "123"},
        )
        assert msg.type == "agent.status"
        assert msg.data == {"agent_id": "123"}
        assert msg.id  # auto-generated UUID
        assert msg.timestamp  # auto-generated

    def test_message_default_ack_required_is_false(self):
        """Test: ack_required 默认 false"""
        msg = WSMessage(type=MessageType.PING, data={})
        assert msg.ack_required is False

    def test_message_id_is_auto_generated_uuid(self):
        """Test: 未指定 id 时自动生成 UUID"""
        msg1 = WSMessage(type=MessageType.PING, data={})
        msg2 = WSMessage(type=MessageType.PING, data={})
        assert msg1.id != msg2.id
        assert len(msg1.id) == 36  # UUID format

    def test_message_is_immutable(self):
        """Test: WSMessage 不可变（Pydantic frozen）"""
        from pydantic import ValidationError

        msg = WSMessage(type=MessageType.PING, data={})
        with pytest.raises(ValidationError):
            msg.type = MessageType.PONG  # type: ignore


class TestSerialization:
    """Tests for JSON serialization round-trip."""

    def test_message_round_trip_serialization(self):
        """Test: 消息序列化/反序列化保持一致"""
        for sample in SAMPLE_MESSAGES:
            msg = WSMessage(**sample)
            json_str = msg.model_dump_json()
            parsed = json.loads(json_str)
            # Reconstruct and compare (timestamps might differ slightly)
            reconstructed = WSMessage(**parsed)
            assert reconstructed.type == msg.type
            assert reconstructed.data == msg.data
            assert reconstructed.id == msg.id

    def test_timestamp_serialized_as_iso8601(self):
        """Test: timestamp 序列化为 ISO 8601 字符串"""

        msg = WSMessage(
            type=MessageType.PING,
            data={},
            timestamp=datetime(2026, 6, 17, 10, 30, 0, tzinfo=UTC),
        )
        json_str = msg.model_dump_json()
        parsed = json.loads(json_str)
        assert "2026-06-17T10:30:00" in parsed["timestamp"]

    def test_timestamp_uses_utc(self):
        """Test: timestamp 统一使用 UTC"""
        msg = WSMessage(type=MessageType.PING, data={})
        # Default timestamp should be timezone-aware UTC
        assert msg.timestamp.tzinfo is not None

    def test_unknown_type_raises_validation_error(self):
        """Test: 未知的 type 值导致 ValidationError"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WSMessage(type="unknown.type", data={})  # type: ignore


class TestAgentStatusMessage:
    """Tests for agent.status event."""

    def test_agent_status_data_structure(self):
        """Test: agent.status 包含 agent_id/run_id/current_status"""
        # sample = {
        #     "type": "agent.status",
        #     "data": {
        #         "agent_id": "agent-uuid",
        #         "run_id": "run-uuid",
        #         "current_status": "completed",
        #     },
        #     "timestamp": "2026-06-17T10:00:00Z",
        #     "id": "msg-uuid",
        # }
        # msg = WSMessage(**sample)
        # assert msg.data["agent_id"] == "agent-uuid"
        pytest.skip("Sprint 2 implementation pending")

    def test_agent_status_optional_fields(self):
        """Test: previous_status/duration_ms/metadata 可选"""
        pytest.skip("Sprint 2 implementation pending")


class TestCodeChunkMessage:
    """Tests for code.chunk event."""

    def test_code_chunk_required_fields(self):
        """Test: code.chunk 必含 run_id/step/chunk_index/content/is_final"""
        pytest.skip("Sprint 2 implementation pending")

    def test_code_chunk_large_content_handled(self):
        """Test: 32KB 内容分片处理"""
        # large_content = "x" * 32768
        # 验证可正确序列化
        pytest.skip("Sprint 2 implementation pending")

    def test_code_chunk_exceeds_limit_rejected(self):
        """Test: 超过 32KB 的 chunk 被拒绝"""
        pytest.skip("Sprint 2 implementation pending")


class TestTaskMessages:
    """Tests for task.created/completed events."""

    def test_task_created_structure(self):
        """Test: task.created 包含 task_id/user_id/title"""
        pytest.skip("Sprint 2 implementation pending")

    def test_task_completed_with_artifacts(self):
        """Test: task.completed 包含 artifacts 列表"""
        pytest.skip("Sprint 2 implementation pending")


class TestSystemError:
    """Tests for system.error event."""

    def test_system_error_has_code_and_message(self):
        """Test: system.error 含 code/message/recoverable"""
        pytest.skip("Sprint 2 implementation pending")

    @pytest.mark.parametrize(
        "error_code,expected_recoverable",
        [
            ("AUTH_FAILED", False),
            ("RATE_LIMITED", True),
            ("AGENT_TIMEOUT", True),
            ("LLM_ERROR", True),
            ("INTERNAL_ERROR", False),
            ("INVALID_MESSAGE", True),
        ],
    )
    def test_error_code_recoverability(self, error_code, expected_recoverable):
        """Test: 每种错误码的 recoverable 值正确"""
        pytest.skip("Sprint 2 implementation pending")


class TestControlMessages:
    """Tests for ping/pong/subscribe/unsubscribe."""

    def test_ping_message_structure(self):
        """Test: ping 消息格式"""
        # {"type": "ping", "data": {}, "timestamp": "...", "id": "..."}
        pytest.skip("Sprint 2 implementation pending")

    def test_pong_includes_server_time(self):
        """Test: pong 包含 server_time"""
        pytest.skip("Sprint 2 implementation pending")

    def test_subscribe_has_channel_field(self):
        """Test: subscribe 消息含 channel 字段"""
        pytest.skip("Sprint 2 implementation pending")

    def test_channel_naming_convention(self):
        """Test: channel 命名遵循 progress:{id}/agent:{id}/task:{id}/system:broadcast"""
        # valid_channels = [
        #     "progress:run_123",
        #     "agent:agent_456",
        #     "task:user_789",
        #     "system:broadcast",
        # ]
        pytest.skip("Sprint 2 implementation pending")


class TestAckMechanism:
    """Tests for message acknowledgment."""

    def test_ack_required_flag_in_serialization(self):
        """Test: ack_required 字段在序列化时正确输出"""
        pytest.skip("Sprint 2 implementation pending")

    def test_ack_response_message(self):
        """Test: ack.response 包含 message_id/status"""
        pytest.skip("Sprint 2 implementation pending")

    def test_ack_response_status_values(self):
        """Test: ack status 只能是 received/processed/failed"""
        pytest.skip("Sprint 2 implementation pending")


class TestMessageSizeLimit:
    """Tests for message size enforcement."""

    def test_message_under_64kb_accepted(self):
        """Test: < 64KB 入站消息接受"""
        pytest.skip("Sprint 2 implementation pending")

    def test_message_over_64kb_rejected(self):
        """Test: > 64KB 入站消息拒绝"""
        pytest.skip("Sprint 2 implementation pending")

    def test_outbound_message_over_256kb_rejected(self):
        """Test: > 256KB 出站消息拒绝"""
        pytest.skip("Sprint 2 implementation pending")


class TestProtocolVersioning:
    """Tests for protocol version negotiation."""

    def test_welcome_message_includes_protocol_version(self):
        """Test: welcome 消息包含 protocol_version"""
        pytest.skip("Sprint 2 implementation pending")

    def test_incompatible_version_returns_error(self):
        """Test: 不兼容版本返回 system.error 后断开"""
        pytest.skip("Sprint 2 implementation pending")


# 共享测试 fixtures（前后端一致性测试可复用）
SAMPLE_MESSAGES = [
    {
        "type": "agent.status",
        "data": {
            "agent_id": "550e8400-e29b-41d4-a716-446655440000",
            "run_id": "660e8400-e29b-41d4-a716-446655440000",
            "previous_status": "running",
            "current_status": "completed",
            "duration_ms": 30000,
        },
        "timestamp": "2026-06-17T10:25:30.123Z",
        "id": "550e8400-e29b-41d4-a716-446655440000",
    },
    {
        "type": "code.chunk",
        "data": {
            "run_id": "660e8400-e29b-41d4-a716-446655440000",
            "step": "coder",
            "file_path": "src/main.py",
            "chunk_index": 0,
            "content": "def hello():\n    print('Hello')\n",
            "is_final": False,
        },
        "timestamp": "2026-06-17T10:26:18.500Z",
        "id": "770e8400-e29b-41d4-a716-446655440000",
    },
    {
        "type": "system.error",
        "data": {
            "code": "AGENT_TIMEOUT",
            "message": "Agent execution exceeded 300s timeout",
            "recoverable": True,
        },
        "timestamp": "2026-06-17T10:05:00.123Z",
        "id": "880e8400-e29b-41d4-a716-446655440000",
    },
    {
        "type": "ping",
        "data": {},
        "timestamp": "2026-06-17T10:00:00.000Z",
        "id": "990e8400-e29b-41d4-a716-446655440000",
    },
]
