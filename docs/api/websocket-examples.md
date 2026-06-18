# WebSocket 使用示例

快速上手指南，演示如何在前端和后端集成 Jules WebSocket API。

---

## 快速开始

### 1. 获取 JWT Token

首先通过 Sprint 1 认证 API 获取 JWT token：

```typescript
// 登录获取 token
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password',
  }),
})

const { access_token, user_id } = await response.json()
```

### 2. 建立 WebSocket 连接

```typescript
import { useWebSocket } from '@/hooks/useWebSocket'

function App() {
  const { state, error, on } = useWebSocket({
    url: `ws://localhost:8000/api/v1/ws/${user_id}`,
    token: access_token,
  })

  return (
    <div>
      <p>Status: {state}</p>
      {error && <p>Error: {error.message}</p>}
    </div>
  )
}
```

---

## 常见场景

### 场景 1: 实时显示 Agent 执行状态

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { useEffect, useState } from 'react'

function AgentStatusPanel({ runId }: { runId: string }) {
  const { on, subscribe } = useWebSocketContext()
  const [status, setStatus] = useState('pending')

  useEffect(() => {
    // 订阅该执行的进度
    subscribe(`progress:${runId}`)

    // 监听状态变更
    const cleanup = on('agent.status', (message) => {
      if (message.data.run_id === runId) {
        setStatus(message.data.current_status)
      }
    })

    return cleanup
  }, [on, subscribe, runId])

  return (
    <div className="agent-status">
      <h3>Agent Status</h3>
      <p>{status}</p>
    </div>
  )
}
```

### 场景 2: 流式显示代码生成

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { useEffect, useState } from 'react'

function CodeStreamViewer({ runId }: { runId: string }) {
  const { on, subscribe } = useWebSocketContext()
  const [code, setCode] = useState('')

  useEffect(() => {
    subscribe(`progress:${runId}`)

    const cleanup = on('code.chunk', (message) => {
      if (message.data.run_id === runId) {
        setCode((prev) => prev + message.data.content)
      }
    })

    return cleanup
  }, [on, subscribe, runId])

  return (
    <pre className="code-viewer">
      <code>{code}</code>
    </pre>
  )
}
```

### 场景 3: 任务通知提醒

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { useEffect } from 'react'
import { toast } from 'react-toastify'

function TaskNotifications({ userId }: { userId: string }) {
  const { on, subscribe } = useWebSocketContext()

  useEffect(() => {
    subscribe(`task:${userId}`)

    const cleanupCreated = on('task.created', (message) => {
      toast.info(`New task: ${message.data.title}`)
    })

    const cleanupCompleted = on('task.completed', (message) => {
      toast.success(`Task completed: ${message.data.result_summary}`)
    })

    return () => {
      cleanupCreated()
      cleanupCompleted()
    }
  }, [on, subscribe, userId])

  return null
}
```

### 场景 4: 进度条显示（Sprint 3 集成）

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { useEffect, useState } from 'react'

function ProgressBar({ runId }: { runId: string }) {
  const { on, subscribe } = useWebSocketContext()
  const [progress, setProgress] = useState(0)
  const [eta, setEta] = useState<number | null>(null)

  useEffect(() => {
    subscribe(`progress:${runId}`)

    const cleanup = on('progress.updated', (message) => {
      if (message.data.run_id === runId) {
        setProgress(message.data.overall_percentage)
        setEta(message.data.eta_seconds)
      }
    })

    return cleanup
  }, [on, subscribe, runId])

  return (
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${progress}%` }}>
        {progress.toFixed(1)}%
      </div>
      {eta !== null && <p>ETA: {eta}s</p>}
    </div>
  )
}
```

### 场景 5: 系统错误处理

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { useEffect } from 'react'
import { toast } from 'react-toastify'

function ErrorHandler() {
  const { on, error: connectionError } = useWebSocketContext()

  useEffect(() => {
    // 处理连接错误
    if (connectionError) {
      if (connectionError.recoverable) {
        toast.warning(`Connection error: ${connectionError.message}`)
      } else {
        toast.error(`Fatal error: ${connectionError.message}`)
      }
    }

    // 处理系统消息错误
    const cleanup = on('system.error', (message) => {
      const { code, message: msg, recoverable } = message.data
      if (recoverable) {
        toast.warning(`${code}: ${msg}`)
      } else {
        toast.error(`${code}: ${msg}`)
      }
    })

    return cleanup
  }, [on, connectionError])

  return null
}
```

---

## 完整应用示例

### App.tsx

```typescript
import { WebSocketProvider } from '@/contexts/WebSocketContext'
import { useAuth } from '@/hooks/useAuth'
import AgentStatusPanel from '@/components/AgentStatusPanel'
import ErrorHandler from '@/components/ErrorHandler'
import TaskNotifications from '@/components/TaskNotifications'

function App() {
  const { userId, accessToken } = useAuth()

  if (!userId || !accessToken) {
    return <Login />
  }

  return (
    <WebSocketProvider
      config={{
        url: `ws://localhost:8000/api/v1/ws/${userId}`,
        token: accessToken,
        heartbeatInterval: 30000,
        reconnectDelays: [1000, 2000, 4000],
        maxReconnectAttempts: 3,
      }}
    >
      <ErrorHandler />
      <TaskNotifications userId={userId} />
      <Dashboard />
    </WebSocketProvider>
  )
}

export default App
```

### Dashboard.tsx

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import { registerMessageHandlers } from '@/utils/websocketHandlers'
import { useEffect, useState } from 'react'

function Dashboard() {
  const { on, state } = useWebSocketContext()
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    const cleanups = registerMessageHandlers(on, {
      onAgentStatus: (status, agentId, runId) => {
        setLogs((prev) => [...prev, `[${agentId}] ${status}`])
      },
      onProgressUpdate: (runId, percentage, eta) => {
        setLogs((prev) => [...prev, `Progress: ${percentage}% (ETA: ${eta}s)`])
      },
      onSystemError: (code, message, recoverable) => {
        setLogs((prev) => [...prev, `ERROR [${code}]: ${message}`])
      },
    })

    return () => cleanups.forEach((cleanup) => cleanup())
  }, [on])

  return (
    <div>
      <h1>Dashboard</h1>
      <p>WebSocket: {state}</p>
      <div className="logs">
        {logs.map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </div>
  )
}
```

---

## 后端主动推送

### 从 API 端点推送消息

```python
from fastapi import APIRouter
from app.api.v1.websocket import send_to_user, send_to_channel
from app.schemas.websocket import MessageType, WSMessage

router = APIRouter()

@router.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str, user_id: str):
    # 执行 Agent 启动逻辑...

    # 推送状态更新到用户
    message = WSMessage(
        type=MessageType.AGENT_STATUS,
        data={
            "agent_id": agent_id,
            "run_id": run_id,
            "current_status": "running",
        },
    )
    await send_to_user(user_id, message)

    return {"status": "started"}

@router.post("/progress/{run_id}/update")
async def update_progress(run_id: str, percentage: float):
    # 更新进度...

    # 广播到订阅该 run 的所有客户端
    message = WSMessage(
        type=MessageType.PROGRESS_UPDATED,
        data={
            "run_id": run_id,
            "overall_percentage": percentage,
            "eta_seconds": 120,
            "current_step": "coder",
        },
    )
    await send_to_channel(f"progress:{run_id}", message)

    return {"status": "updated"}
```

---

## 测试

### 单元测试（Mock WebSocket）

```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { useWebSocket } from '@/hooks/useWebSocket'

describe('useWebSocket', () => {
  it('should connect and receive welcome message', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/ws/test-user',
        token: 'valid-token',
      })
    )

    await waitFor(() => {
      expect(result.current.state).toBe('connected')
    })
  })

  it('should handle reconnection on error', async () => {
    // Mock WebSocket close
    // Verify reconnection attempts
  })
})
```

### 集成测试（FastAPI TestClient）

```python
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_handshake():
    client = TestClient(app)

    with client.websocket_connect(
        "/api/v1/ws/user-123",
        subprotocols=["bearer.valid-token"],
    ) as websocket:
        data = websocket.receive_json()
        assert data["type"] == "welcome"
        assert data["data"]["user_id"] == "user-123"
```

---

## 故障排查

### 常见问题

**Q: 连接立即关闭，错误码 4401**
A: JWT token 无效或过期。检查 token 生成和传递。

**Q: 连接立即关闭，错误码 4403**
A: URL 中的 user_id 与 token 中的 `sub` 不匹配。

**Q: 连接建立后无消息**
A: 检查是否订阅了正确的 channel。确认后端是否推送消息。

**Q: 频繁断线重连**
A: 检查心跳间隔配置。确认网络稳定性。

**Q: 前端收不到 welcome 消息**
A: 检查 `Sec-WebSocket-Protocol` 头格式：`bearer.<token>`（注意点号）。

---

## 最佳实践

1. **Token 管理**: 在 token 过期前主动断开并刷新 token
2. **订阅管理**: 组件卸载时自动退订 channel（useEffect cleanup）
3. **错误恢复**: 区分 recoverable/non-recoverable 错误
4. **消息去重**: 使用 `message.id` 去重（防重连后重复消息）
5. **性能优化**: 避免在消息处理器中进行昂贵计算
6. **日志记录**: 记录连接状态变更和错误（便于调试）

---

## 下一步

- 阅读 [WebSocket API 文档](./websocket.md)
- 查看 [消息协议规范](../design/websocket-message-protocol.md)
- 运行 [集成测试](../../backend/tests/integration/test_websocket_integration.py)
- 集成 [Sprint 3 进度追踪](../design/agent-progress-state-machine.md)
