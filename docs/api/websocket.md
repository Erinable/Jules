# WebSocket API 文档

**版本**: v1.0
**Sprint**: Sprint 2
**状态**: 已实施

---

## 概述

Jules WebSocket API 提供实时双向通信，用于 Agent 执行状态更新、代码流式输出、任务通知和进度追踪。

### 特性

- ✅ JWT 认证（Sec-WebSocket-Protocol）
- ✅ 自动重连（客户端）
- ✅ 心跳保活（30s ping）
- ✅ Channel 订阅机制
- ✅ 17 种消息类型
- ✅ 类型安全（Pydantic + TypeScript）

---

## 连接建立

### 端点

```
ws://localhost:8000/api/v1/ws/{user_id}
wss://api.jules-ai.dev/api/v1/ws/{user_id}
```

### 认证

使用 `Sec-WebSocket-Protocol` HTTP 头携带 JWT Token：

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/${userId}`,
  [`bearer.${jwtToken}`]
)
```

### 握手流程

1. 客户端发起连接，携带 `Sec-WebSocket-Protocol: bearer.<jwt>`
2. 服务端验证 JWT（使用 Sprint 1 `decode_token`）
3. 服务端验证 `user_id` 与 token 中的 `sub` 一致
4. 服务端接受连接，echo 原 protocol 头
5. 服务端发送 `welcome` 消息

### 关闭码

| Code | Reason | 描述 |
|------|--------|------|
| 1000 | Normal | 正常关闭 |
| 4401 | AUTH_FAILED | 无 protocol 头 / token 无效 |
| 4403 | FORBIDDEN | user_id 与 token 不匹配 |
| 4404 | PROTOCOL_VERSION_MISMATCH | 协议版本不兼容 |
| 4409 | CONFLICT | 同名连接冲突 |
| 4429 | RATE_LIMITED | 连接频率超限 |

---

## 消息格式

### 消息信封

所有消息遵循统一结构：

```typescript
interface WSMessage<T> {
  type: MessageType
  data: T
  timestamp: string  // ISO 8601 UTC
  id: string         // UUID
  ack_required?: boolean
}
```

### 消息类型

#### 服务端 → 客户端

| Type | 描述 | 触发时机 |
|------|------|---------|
| `welcome` | 欢迎消息 | 连接建立后 |
| `pong` | 心跳响应 | 收到 ping 后 |
| `agent.status` | Agent 状态变更 | Agent 状态机转换 |
| `code.chunk` | 代码流式输出 | LLM 生成代码 |
| `task.created` | 任务创建通知 | 用户创建任务 |
| `task.completed` | 任务完成通知 | 任务执行完成 |
| `system.error` | 系统错误 | 错误发生 |
| `progress.step.started` | 步骤开始（Sprint 3） | 进度追踪 |
| `progress.step.completed` | 步骤完成（Sprint 3） | 进度追踪 |
| `progress.step.failed` | 步骤失败（Sprint 3） | 进度追踪 |
| `progress.updated` | 进度更新（Sprint 3） | 进度追踪 |
| `progress.log.appended` | 日志追加（Sprint 3） | 进度追踪 |

#### 客户端 → 服务端

| Type | 描述 | 何时发送 |
|------|------|---------|
| `ping` | 心跳请求 | 每 30s |
| `subscribe` | 订阅 channel | 需要接收特定 channel 消息 |
| `unsubscribe` | 退订 channel | 不再需要特定 channel 消息 |
| `ack.response` | 消息确认 | 收到需要 Ack 的消息 |

---

## 消息示例

### welcome

```json
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
```

### ping / pong

```json
// 客户端 → 服务端
{
  "type": "ping",
  "data": {},
  "timestamp": "2026-06-17T10:00:30.000Z",
  "id": "ping-uuid"
}

// 服务端 → 客户端
{
  "type": "pong",
  "data": {
    "server_time": "2026-06-17T10:00:30.005Z"
  },
  "timestamp": "2026-06-17T10:00:30.005Z",
  "id": "pong-uuid"
}
```

### agent.status

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

### code.chunk

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

### system.error

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
    "recoverable": true
  },
  "timestamp": "2026-06-17T10:05:00.123Z",
  "id": "msg-uuid"
}
```

### subscribe / unsubscribe

```json
// 订阅 channel
{
  "type": "subscribe",
  "data": {
    "channel": "progress:run_550e8400"
  },
  "timestamp": "2026-06-17T10:00:00.000Z",
  "id": "sub-uuid"
}

// 退订 channel
{
  "type": "unsubscribe",
  "data": {
    "channel": "progress:run_550e8400"
  },
  "timestamp": "2026-06-17T10:05:00.000Z",
  "id": "unsub-uuid"
}
```

---

## Channel 命名规则

| Pattern | 描述 | 示例 |
|---------|------|------|
| `progress:{run_id}` | 特定执行的进度 | `progress:run_550e8400` |
| `agent:{agent_id}` | 特定 Agent 的状态 | `agent:agent_123` |
| `task:{user_id}` | 用户的任务通知 | `task:user_456` |
| `system:broadcast` | 系统广播（所有人） | `system:broadcast` |

---

## 前端集成

### React Hook 使用

```typescript
import { useWebSocket } from '@/hooks/useWebSocket'
import { useEffect } from 'react'

function MyComponent() {
  const { state, error, on, subscribe } = useWebSocket({
    url: `ws://localhost:8000/api/v1/ws/${userId}`,
    token: jwtToken,
  })

  useEffect(() => {
    // 订阅进度 channel
    subscribe(`progress:run_${runId}`)

    // 注册消息处理器
    const cleanup = on('progress.updated', (message) => {
      console.log('Progress:', message.data.overall_percentage)
    })

    return cleanup
  }, [on, subscribe, runId])

  return (
    <div>
      <p>Connection: {state}</p>
      {error && <p>Error: {error.message}</p>}
    </div>
  )
}
```

### Context Provider 使用

```typescript
import { WebSocketProvider } from '@/contexts/WebSocketContext'

function App() {
  return (
    <WebSocketProvider
      config={{
        url: `ws://localhost:8000/api/v1/ws/${userId}`,
        token: jwtToken,
      }}
    >
      <YourApp />
    </WebSocketProvider>
  )
}
```

### 批量注册消息处理器

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { registerMessageHandlers } from '@/utils/websocketHandlers'
import { useEffect } from 'react'

function Dashboard() {
  const { on } = useWebSocketContext()

  useEffect(() => {
    const cleanups = registerMessageHandlers(on, {
      onAgentStatus: (status, agentId, runId) => {
        console.log(`Agent ${agentId} status: ${status}`)
      },
      onCodeChunk: (chunk, index, isFinal) => {
        // Display code chunk in UI
      },
      onTaskCompleted: (taskId, status, summary) => {
        // Show notification
      },
      onSystemError: (code, message, recoverable) => {
        // Display error toast
      },
    })

    return () => cleanups.forEach((cleanup) => cleanup())
  }, [on])

  return <div>Dashboard</div>
}
```

---

## 错误处理

### 标准错误码

| Code | 描述 | recoverable |
|------|------|-------------|
| `AUTH_FAILED` | JWT 验证失败 | false |
| `RATE_LIMITED` | 频率超限 | true |
| `AGENT_TIMEOUT` | Agent 超时 | true |
| `LLM_ERROR` | LLM Provider 错误 | true |
| `INTERNAL_ERROR` | 内部错误 | false |
| `INVALID_MESSAGE` | 消息格式错误 | true |

### 错误恢复策略

- **AUTH_FAILED / FORBIDDEN**: 不重连，提示用户重新登录
- **RATE_LIMITED**: 指数退避重连（1s / 2s / 4s）
- **CONNECTION_TIMEOUT**: 自动重连（最多 3 次）
- **INVALID_MESSAGE**: 忽略该消息，继续连接

---

## 性能特性

- **并发连接**: 支持 100 并发（v1.0），可通过 Redis 扩展到多实例
- **消息延迟**: < 100ms (p99 < 200ms)
- **心跳间隔**: 30s ping / 60s 检查 / 90s 超时
- **消息大小限制**: 64KB 入站 / 256KB 出站 / 32KB 单 chunk
- **重连策略**: 1s / 2s / 4s 指数退避，最多 3 次

---

## 安全考虑

- ✅ JWT 在 Sec-WebSocket-Protocol 头中传输（不在 URL）
- ✅ Token 不出现在 access_log / Referer 日志
- ✅ 严格 user_id 验证（防越权）
- ✅ 连接频率限制（防 DDoS）
- ✅ 消息大小限制（防恶意大消息）

---

## 版本兼容

- **当前版本**: v1.0
- **协议版本**: 在 `welcome` 消息中声明
- **不兼容处理**: 返回 close code 4404 后断开
- **向后兼容**: 字段只增不减，枚举可扩展

---

## 参考文档

- [WebSocket 消息协议规范](../design/websocket-message-protocol.md)
- [ConnectionManager 设计](../design/websocket-connection-manager.md)
- [WebSocket 测试计划](../design/websocket-test-plan.md)
- [Sprint 2 任务](../../README.md#sprint-2)
