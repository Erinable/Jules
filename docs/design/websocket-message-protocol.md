# WebSocket 消息协议规范

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #05de8d26 (Sprint 2)
**依赖**: 无（独立规范）

---

## 1. 概述

定义 WebSocket 消息的 JSON Schema、事件类型、序列化格式、Ack 机制。本文档为 Sprint 2 前后端共同遵循的协议契约。

### 设计原则

- **统一信封**: 所有消息使用一致结构
- **类型安全**: Pydantic/TypeScript 双端 schema 同源
- **可扩展**: 新增事件类型不破坏现有客户端
- **向后兼容**: 字段只增不减，枚举可扩展

---

## 2. 消息信封（Envelope）

### 2.1 基础结构

所有 WebSocket 消息遵循统一信封：

```json
{
  "type": "<event_type>",
  "data": { /* 类型相关 payload */ },
  "timestamp": "2026-06-17T10:30:00.123Z",
  "id": "msg_uuid",
  "ack_required": false
}
```

### 2.2 字段说明

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `type` | string | ✅ | 事件类型（见第 3 节） |
| `data` | object | ✅ | 事件 payload，结构由 type 决定 |
| `timestamp` | ISO8601 | ✅ | 消息生成时间（UTC） |
| `id` | UUID | ✅ | 消息唯一标识，用于 Ack 和去重 |
| `ack_required` | bool | ❌ | 是否需要客户端确认（默认 false） |

### 2.3 Pydantic Schema

```python
# app/schemas/websocket.py
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class MessageType(str, Enum):
    """所有 WebSocket 消息类型"""
    # 服务端 → 客户端
    AGENT_STATUS = "agent.status"
    CODE_CHUNK = "code.chunk"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    SYSTEM_ERROR = "system.error"
    PONG = "pong"
    ACK = "ack"
    WELCOME = "welcome"

    # 客户端 → 服务端
    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ACK_RESPONSE = "ack.response"

    # 进度追踪（Sprint 3 集成）
    PROGRESS_STEP_STARTED = "progress.step.started"
    PROGRESS_STEP_COMPLETED = "progress.step.completed"
    PROGRESS_STEP_FAILED = "progress.step.failed"
    PROGRESS_UPDATED = "progress.updated"
    PROGRESS_LOG_APPENDED = "progress.log.appended"


class WSMessage(BaseModel):
    """WebSocket 消息信封（不可变）"""

    type: MessageType
    data: dict = Field(default_factory=dict)
    timestamp: datetime
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ack_required: bool = False

    class Config:
        frozen = True
        use_enum_values = True
```

### 2.4 TypeScript Schema

```typescript
// src/types/websocket.ts
export type MessageType =
  // 服务端 → 客户端
  | "agent.status"
  | "code.chunk"
  | "task.created"
  | "task.completed"
  | "system.error"
  | "pong"
  | "ack"
  | "welcome"
  // 客户端 → 服务端
  | "ping"
  | "subscribe"
  | "unsubscribe"
  | "ack.response"
  // Sprint 3 集成
  | "progress.step.started"
  | "progress.step.completed"
  | "progress.step.failed"
  | "progress.updated"
  | "progress.log.appended";

export interface WSMessage<T = unknown> {
  type: MessageType;
  data: T;
  timestamp: string;  // ISO 8601
  id: string;         // UUID
  ack_required?: boolean;
}
```

---

## 3. 事件类型详细规范

### 3.1 `agent.status` - Agent 执行状态变更

**触发**: Agent 状态机转换（pending → running → completed/failed）

```json
{
  "type": "agent.status",
  "data": {
    "agent_id": "agent-uuid",
    "run_id": "run-uuid",
    "previous_status": "running",
    "current_status": "completed",
    "duration_ms": 30000,
    "metadata": {
      "model": "gpt-4o",
      "tokens_used": 1500
    }
  },
  "timestamp": "2026-06-17T10:25:30.123Z",
  "id": "msg-uuid"
}
```

**data 字段**:
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `agent_id` | UUID | ✅ | Agent 实例 ID |
| `run_id` | UUID | ✅ | 执行运行 ID |
| `previous_status` | string | ❌ | 前置状态 |
| `current_status` | string | ✅ | 当前状态 |
| `duration_ms` | int | ❌ | 状态持续时间 |
| `metadata` | object | ❌ | 附加信息 |

---

### 3.2 `code.chunk` - 代码生成流式输出

**触发**: LLM 生成代码时每行/每 chunk 推送

```json
{
  "type": "code.chunk",
  "data": {
    "run_id": "run-uuid",
    "step": "coder",
    "file_path": "src/main.py",
    "chunk_index": 0,
    "content": "def hello():\n    print('Hello')\n",
    "is_final": false
  },
  "timestamp": "2026-06-17T10:26:18.500Z",
  "id": "msg-uuid"
}
```

**data 字段**:
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `run_id` | UUID | ✅ | 执行 ID |
| `step` | string | ✅ | 当前步骤 |
| `file_path` | string | ❌ | 目标文件 |
| `chunk_index` | int | ✅ | chunk 序号（0-based） |
| `content` | string | ✅ | 代码片段 |
| `is_final` | bool | ✅ | 是否最后一个 chunk |

**推送频率**（默认）: 每 1 行或 100ms 批处理，可配置。

---

### 3.3 `task.created` - 任务创建通知

**触发**: 用户创建新任务时

```json
{
  "type": "task.created",
  "data": {
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "title": "Refactor auth module",
    "priority": "high",
    "created_at": "2026-06-17T10:00:00Z"
  },
  "timestamp": "2026-06-17T10:00:00.123Z",
  "id": "msg-uuid"
}
```

---

### 3.4 `task.completed` - 任务完成通知

```json
{
  "type": "task.completed",
  "data": {
    "task_id": "task-uuid",
    "status": "completed",  // completed | failed | cancelled
    "result_summary": "Successfully refactored 3 files",
    "artifacts": [
      {"type": "code_file", "path": "src/auth/jwt.py"}
    ],
    "total_duration_ms": 180000
  },
  "timestamp": "2026-06-17T10:03:00.123Z",
  "id": "msg-uuid"
}
```

---

### 3.5 `system.error` - 系统错误

```json
{
  "type": "system.error",
  "data": {
    "code": "AGENT_TIMEOUT",
    "message": "Agent execution exceeded 300s timeout",
    "details": {
      "agent_id": "agent-uuid",
      "timeout_ms": 300000
    },
    "recoverable": false
  },
  "timestamp": "2026-06-17T10:05:00.123Z",
  "id": "msg-uuid"
}
```

**标准错误码**:
| Code | 描述 | recoverable |
|------|------|-------------|
| `AUTH_FAILED` | JWT 验证失败 | false |
| `RATE_LIMITED` | 频率超限 | true |
| `AGENT_TIMEOUT` | Agent 超时 | true |
| `LLM_ERROR` | LLM Provider 错误 | true |
| `INTERNAL_ERROR` | 内部错误 | false |
| `INVALID_MESSAGE` | 消息格式错误 | true |

---

### 3.6 Sprint 3 集成事件

```typescript
// progress.step.started
{
  "type": "progress.step.started",
  "data": {
    "run_id": "run-uuid",
    "step": "coder",
    "started_at": "2026-06-17T10:26:15Z"
  }
}

// progress.step.completed
{
  "type": "progress.step.completed",
  "data": {
    "run_id": "run-uuid",
    "step": "coder",
    "duration_ms": 135000,
    "retry_count": 0
  }
}

// progress.updated (整体进度变更)
{
  "type": "progress.updated",
  "data": {
    "run_id": "run-uuid",
    "overall_percentage": 45.5,
    "eta_seconds": 150,
    "current_step": "coder"
  }
}

// progress.log.appended
{
  "type": "progress.log.appended",
  "data": {
    "run_id": "run-uuid",
    "step": "planner",
    "level": "info",
    "message": "生成架构方案 v1",
    "sequence_num": 42
  }
}
```

---

## 4. 控制消息（客户端 → 服务端）

### 4.1 `ping` / `pong` 心跳

```json
// 客户端 → 服务端
{ "type": "ping", "data": {}, "timestamp": "...", "id": "..." }

// 服务端 → 客户端
{ "type": "pong", "data": {"server_time": "..."}, "timestamp": "...", "id": "..." }
```

**频率**: 客户端每 30s 发送一次 ping。

---

### 4.2 `subscribe` / `unsubscribe` 订阅管理

```json
{
  "type": "subscribe",
  "data": {
    "channel": "progress:run_550e8400"
  },
  "timestamp": "...",
  "id": "..."
}
```

**channel 命名规则**:

- `progress:{run_id}` - 特定执行的进度
- `agent:{agent_id}` - 特定 Agent 的状态
- `task:{user_id}` - 用户的任务通知
- `system:broadcast` - 系统广播（所有人）

---

### 4.3 `ack.response` - 消息确认

```json
// 服务端发送需 Ack 的消息
{
  "type": "task.completed",
  "data": {...},
  "timestamp": "...",
  "id": "msg-123",
  "ack_required": true
}

// 客户端确认
{
  "type": "ack.response",
  "data": {
    "message_id": "msg-123",
    "status": "received"
  },
  "timestamp": "...",
  "id": "..."
}
```

---

## 5. 握手协议（连接建立）

### 5.1 认证方式：Sec-WebSocket-Protocol 握手（决策 Q2-b）

JWT Token 通过 `Sec-WebSocket-Protocol` HTTP 头携带，避免暴露在 URL 或 access log 中。

**客户端发起连接**:

```
GET /api/v1/ws/{user_id} HTTP/1.1
Host: api.jules-ai.dev
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: <random>
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: bearer.<jwt_token>
```

**服务端验证流程**（依赖 Sprint 1 `validate_jwt`）:

```python
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    sec_websocket_protocol: str | None = Header(default=None),
):
    # 1. 提取并验证 protocol 头
    if not sec_websocket_protocol or not sec_websocket_protocol.startswith("bearer."):
        await websocket.close(code=4401, reason="AUTH_FAILED")
        return

    token = sec_websocket_protocol[len("bearer."):]

    # 2. 调用 Sprint 1 JWT 验证
    try:
        token_user_id = await validate_jwt(token)  # Sprint 1 提供
    except InvalidTokenError:
        await websocket.close(code=4401, reason="AUTH_FAILED")
        return

    # 3. 验证 user_id 一致（防越权）
    if token_user_id != user_id:
        await websocket.close(code=4403, reason="FORBIDDEN")
        return

    # 4. 接受连接，必须 echo 原 protocol 头
    await websocket.accept(subprotocol=sec_websocket_protocol)

    # 5. 注册到 ConnectionManager
    connection = await connection_manager.connect(websocket, user_id)

    # 6. 发送 welcome 消息
    await send_welcome(websocket, connection)
```

**WebSocket 关闭码**（自定义 4xxx 范围）:
| Code | Reason | 描述 |
|------|--------|------|
| 4401 | AUTH_FAILED | 无 protocol 头 / token 无效 |
| 4403 | FORBIDDEN | user_id 与 token 不匹配 |
| 4404 | PROTOCOL_VERSION_MISMATCH | 协议版本不兼容 |
| 4409 | CONFLICT | 同名连接冲突 |
| 4429 | RATE_LIMITED | 连接频率超限 |

### 5.2 连接建立后流程

```
1. 客户端建立 WebSocket 连接（Sec-WebSocket-Protocol: bearer.<jwt>）
2. 服务端验证 JWT（见 §5.1）
3. 服务端发送 welcome 消息:

{
  "type": "welcome",
  "data": {
    "connection_id": "conn-uuid",
    "user_id": "user-uuid",
    "heartbeat_interval_seconds": 30,
    "server_time": "2026-06-17T10:00:00Z",
    "protocol_version": "1.0"
  },
  "timestamp": "2026-06-17T10:00:00.123Z",
  "id": "msg-uuid"
}

4. 客户端开始订阅 channel
5. 进入正常消息流
```

**安全优势（Q2-b 决策理由）**:

- ✅ Token 不出现在 URL（避免 access_log / Referer 泄漏）
- ✅ 不在 query string（避免代理/CDN 日志记录）
- ✅ 浏览器原生支持，无需自定义 header
- ✅ 与 Sprint 1 `validate_jwt` 函数直接复用
- ✅ 业界标准做法（RFC 6455）

### 5.3 协议版本兼容

- 客户端在 `Sec-WebSocket-Protocol` 头中声明版本：`bearer.<token>, v1.0`
- 服务端支持 v1.0，未来版本可在 `welcome` 中协商
- 不兼容版本返回 close code 4404 后断开

---

## 6. Ack 机制

### 6.1 何时需要 Ack

| 消息类型 | Ack Required | 原因 |
|---------|--------------|------|
| `task.completed` | ✅ | 关键通知，确保用户看到 |
| `system.error` | ✅ | 关键错误 |
| `code.chunk` | ❌ | 高频消息，丢失可容忍 |
| `agent.status` | ❌ | 状态变更会同步刷新 |
| `progress.updated` | ❌ | 频繁更新 |

### 6.2 重试策略

- 服务端等待 Ack 5s
- 未收到则重试 1 次
- 仍失败则记录日志，不再重试
- 客户端断线时跳过重试

### 6.3 实现要点

```python
class AckTracker:
    def __init__(self) -> None:
        self._pending: dict[str, asyncio.Future] = {}

    async def wait_for_ack(self, message_id: str, timeout: float = 5.0) -> bool:
        future = asyncio.Future()
        self._pending[message_id] = future
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return False
        finally:
            self._pending.pop(message_id, None)

    def resolve(self, message_id: str, status: str) -> None:
        if future := self._pending.get(message_id):
            if not future.done():
                future.set_result(status == "received")
```

---

## 7. 消息大小限制

| 类型 | 最大大小 | 备注 |
|------|---------|------|
| 单条消息（入站） | 64KB | 防恶意大消息 |
| 单条消息（出站） | 256KB | 含代码 chunk |
| code.chunk 单条 | 32KB | 大文件分片 |
| 单连接总流量 | 1MB/s | 速率限制 |

超过限制返回 `system.error` (code: `MESSAGE_TOO_LARGE`)。

---

## 8. 消息序列化

### 8.1 编码

- **格式**: JSON UTF-8
- **压缩**: 不在协议层压缩（WS 已支持 permessage-deflate）
- **二进制**: 不支持（如需传输二进制，base64 编码）

### 8.2 时间格式

- **统一使用 ISO 8601 + UTC**: `2026-06-17T10:30:00.123Z`
- **不使用本地时区**
- **毫秒精度**: 3 位小数

### 8.3 ID 生成

- **UUID v4**: 客户端和服务端各自生成
- **服务端权威**: 出现 ID 冲突时以服务端为准

---

## 9. 错误恢复

### 9.1 客户端断线重连

```
断线 → 等待 1s → 重连 → 等待 2s → 重连 → 等待 4s → 重连 → 放弃
```

**重连后**:

1. 重新发送订阅请求
2. 请求离线消息（lastEventId 之后）
3. 更新本地状态

### 9.2 离线消息（可选）

- Redis 缓存每个用户最近 100 条消息
- 客户端重连后通过 REST API 或握手消息拉取
- TTL: 1 小时

---

## 10. 测试 Schema 校验

### 10.1 JSON Schema（用于跨语言验证）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WSMessage",
  "type": "object",
  "required": ["type", "data", "timestamp", "id"],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "agent.status", "code.chunk", "task.created", "task.completed",
        "system.error", "pong", "ack", "welcome",
        "ping", "subscribe", "unsubscribe", "ack.response",
        "progress.step.started", "progress.step.completed",
        "progress.step.failed", "progress.updated", "progress.log.appended"
      ]
    },
    "data": { "type": "object" },
    "timestamp": { "type": "string", "format": "date-time" },
    "id": { "type": "string", "format": "uuid" },
    "ack_required": { "type": "boolean", "default": false }
  }
}
```

### 10.2 双端一致性测试

```python
# 共享 fixtures，前后端复用
@pytest.fixture
def sample_messages():
    return [
        {"type": "agent.status", "data": {...}},
        {"type": "code.chunk", "data": {...}},
        # ...
    ]

def test_message_round_trip():
    """验证消息序列化/反序列化一致"""
    for sample in sample_messages():
        msg = WSMessage(**sample)
        json_str = msg.model_dump_json()
        parsed = json.loads(json_str)
        assert WSMessage(**parsed) == msg
```

---

## 11. 待决问题

| # | 问题 | 默认建议 |
|---|------|---------|
| 1 | code.chunk 推送粒度？ | 每 100ms 批处理 |
| 2 | 是否支持二进制消息？ | v1.1 不支持 |
| 3 | 跨实例消息（Redis Pub/Sub）？ | v1.2 实现 |
| 4 | 消息压缩？ | 依赖 WS permessage-deflate |

---

**变更记录**:

- 2026-06-17: v1.0 初版设计（tom）
