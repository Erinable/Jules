# WebSocket 测试计划

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #05de8d26 (Sprint 2)
**依赖**: Sprint 2 实施完成

---

## 1. 概述

定义 WebSocket 系统的完整测试策略，覆盖单元、集成、压力、E2E 四层。本文档与 `docs/design/websocket-connection-manager.md` 和 `docs/design/websocket-message-protocol.md` 配套。

### 测试目标

- **覆盖率**: ≥ 85%（与项目标准一致）
- **关键路径**: 100%（连接生命周期、消息路由、心跳）
- **性能**: 100 并发连接、消息延迟 < 100ms
- **健壮性**: 异常场景全部覆盖

---

## 2. 测试分层

```
┌─────────────────────────────────────────┐
│  E2E Tests (Playwright)                 │  最少，最贵
│  - 真实用户流程                          │
├─────────────────────────────────────────┤
│  Load Tests (Locust)                     │  性能基准
│  - 100 并发连接                          │
├─────────────────────────────────────────┤
│  Integration Tests (pytest + httpx)      │  端到端流程
│  - FastAPI WebSocket + DB               │
├─────────────────────────────────────────┤
│  Unit Tests (pytest)                     │  最多，最快
│  - 纯逻辑、Mock 依赖                     │
└─────────────────────────────────────────┘
```

---

## 3. 单元测试

### 3.1 ConnectionManager 测试

**文件**: `backend/tests/unit/websocket/test_connection_manager.py`

**测试类**:

| 类名 | 测试数量 | 覆盖场景 |
|------|---------|---------|
| `TestConnectionLifecycle` | 4 | 连接/断开/重复断开/websocket.close |
| `TestUserRouting` | 4 | 单连接/多连接/不存在用户/用户隔离 |
| `TestChannelSubscription` | 4 | 订阅/退订/广播过滤/断开自动退订 |
| `TestHeartbeat` | 3 | 超时清理/活跃保留/ping 更新 |
| `TestErrorHandling` | 3 | 死连接清理/超时/失败隔离 |
| `TestConcurrency` | 3 | 100 连接/广播/并发安全 |
| `TestStats` | 2 | 计数准确/top users 排序 |

**共计**: 23 个测试用例

### 3.2 消息协议测试

**文件**: `backend/tests/unit/websocket/test_message_protocol.py`

**测试类**:

| 类名 | 测试数量 | 覆盖场景 |
|------|---------|---------|
| `TestMessageEnvelope` | 4 | 必填字段/默认值/UUID 自动生成/不可变性 |
| `TestSerialization` | 4 | 往返序列化/ISO 8601/UTC/未知 type |
| `TestAgentStatusMessage` | 2 | data 结构/可选字段 |
| `TestCodeChunkMessage` | 3 | 必填字段/32KB/超限拒绝 |
| `TestTaskMessages` | 2 | created/completed |
| `TestSystemError` | 2 + 6 参数化 | 结构/错误码 recoverable |
| `TestControlMessages` | 4 | ping/pong/subscribe/channel 命名 |
| `TestAckMechanism` | 3 | flag/响应消息/status 值 |
| `TestMessageSizeLimit` | 3 | 入站/出站限制 |
| `TestProtocolVersioning` | 2 | welcome 版本/不兼容错误 |

**共计**: 33+ 个测试用例

### 3.3 测试执行

```bash
# 运行所有 WebSocket 单元测试
cd backend
poetry run pytest tests/unit/websocket/ -v --cov=app --cov-report=term-missing

# 仅运行 ConnectionManager 测试
poetry run pytest tests/unit/websocket/test_connection_manager.py -v

# 仅运行消息协议测试
poetry run pytest tests/unit/websocket/test_message_protocol.py -v
```

---

## 4. 集成测试

### 4.1 测试范围

**文件**: `backend/tests/integration/test_websocket_integration.py`（待 Sprint 2 创建）

| 测试 | 描述 |
|------|------|
| `test_websocket_handshake_with_jwt` | JWT 验证后建立连接 |
| `test_websocket_rejects_invalid_token` | 无效 JWT 被拒（依赖 Sprint 1） |
| `test_subscribe_receive_messages` | 订阅后能收到 channel 消息 |
| `test_multiple_users_isolated` | 多用户消息互不干扰 |
| `test_reconnect_resubscribes_channels` | 断线重连后恢复订阅 |
| `test_offline_message_replay` | 重连后回放离线消息 |

### 4.2 测试工具

```python
from fastapi.testclient import TestClient
from app.main import app


def test_websocket_handshake_with_jwt():
    """通过 TestClient 测试 WebSocket"""
    client = TestClient(app)
    with client.websocket_connect(
        "/api/v1/ws/user-1?token=valid.jwt.token"
    ) as websocket:
        # 接收 welcome
        data = websocket.receive_json()
        assert data["type"] == "welcome"
        assert data["data"]["protocol_version"] == "1.0"

        # 发送 ping
        websocket.send_json({"type": "ping", "data": {}, "timestamp": "...", "id": "x"})

        # 接收 pong
        pong = websocket.receive_json()
        assert pong["type"] == "pong"
```

---

## 5. 压力测试

### 5.1 Locust 测试脚本

**文件**: `backend/tests/load/test_websocket_load.py`（待创建）

```python
from locust import User, task, between
import websocket
import json
import time


class WebSocketUser(User):
    wait_time = between(1, 3)

    def on_start(self):
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://localhost:8000/api/v1/ws/{self.user_id}?token={self.token}")
        # 验证 welcome
        welcome = json.loads(self.ws.recv())
        assert welcome["type"] == "welcome"

    @task
    def ping_pong(self):
        self.ws.send(json.dumps({
            "type": "ping",
            "data": {},
            "timestamp": time.time(),
            "id": str(uuid.uuid4()),
        }))
        pong = json.loads(self.ws.recv())
        assert pong["type"] == "pong"

    @task(3)
    def subscribe_progress(self):
        self.ws.send(json.dumps({
            "type": "subscribe",
            "data": {"channel": f"progress:run_{uuid.uuid4()}"},
            "timestamp": time.time(),
            "id": str(uuid.uuid4()),
        }))

    def on_stop(self):
        self.ws.close()
```

### 5.2 性能基准

```bash
# 启动 Locust
cd backend
locust -f tests/load/test_websocket_load.py --headless \
  --users 100 --spawn-rate 10 --host ws://localhost:8000

# 输出关键指标：
# - 100 并发连接建立时间 < 2s
# - ping-pong 平均延迟 < 50ms (p99 < 200ms)
# - 0 个连接错误
```

---

## 6. E2E 测试

### 6.1 Playwright 测试

**文件**: `frontend/e2e/websocket.spec.ts`（待 Sprint 2 创建）

```typescript
import { test, expect } from "@playwright/test";

test.describe("WebSocket real-time notifications", () => {
  test("user receives agent status updates", async ({ page }) => {
    await page.goto("/dashboard");

    // 触发 Agent 执行
    await page.click("[data-testid=start-agent]");

    // 验证实时 UI 更新
    await expect(page.locator("[data-testid=agent-status]")).toHaveText("running", {
      timeout: 5000,
    });

    // 等待完成
    await expect(page.locator("[data-testid=agent-status]")).toHaveText("completed", {
      timeout: 60000,
    });
  });

  test("auto-reconnect on network drop", async ({ page, context }) => {
    // 模拟网络断开
    await context.setOffline(true);
    await page.waitForTimeout(1000);
    await context.setOffline(false);

    // 验证自动重连
    await expect(page.locator("[data-testid=connection-status]")).toHaveText("connected", {
      timeout: 10000,
    });
  });
});
```

### 6.2 E2E 覆盖场景

| 场景 | 测试 |
|------|------|
| Agent 状态实时更新 | UI 自动刷新 |
| 代码流式输出 | 日志面板实时滚动 |
| 断线重连 | 自动恢复订阅 |
| 多用户隔离 | 用户 A 不见用户 B 数据 |
| 错误处理 | system.error 显示 toast |

---

## 7. Mock 策略

### 7.1 Sprint 1 JWT 验证 Mock

```python
# tests/unit/websocket/conftest.py
@pytest.fixture
def mock_jwt_validator(monkeypatch):
    """Mock Sprint 1 JWT 验证，使测试不依赖 Sprint 1"""
    async def mock_validate(token: str) -> str:
        if token == "valid.token":
            return "user-123"
        raise ValueError("Invalid token")

    monkeypatch.setattr("app.core.auth.validate_jwt", mock_validate)
```

### 7.2 WebSocket Mock

```python
@pytest.fixture
def mock_websocket():
    """Mock FastAPI WebSocket"""
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.close = AsyncMock()
    return ws
```

### 7.3 Redis Mock（未来扩展）

```python
@pytest.fixture
def mock_redis():
    """Mock Redis for v2.0 RedisBackedConnectionManager"""
    redis = AsyncMock()
    redis.publish = AsyncMock()
    redis.pubsub.return_value.listen = AsyncMock(return_value=iter([]))
    return redis
```

---

## 8. CI 集成

### 8.1 GitHub Actions 测试作业

```yaml
# .github/workflows/backend-ci.yml（已有，扩展）
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Poetry
        run: pip install poetry
      - name: Install deps
        run: poetry install
      - name: Run unit tests
        run: poetry run pytest tests/unit/ -v --cov=app --cov-fail-under=85
      - name: Run integration tests
        run: poetry run pytest tests/integration/ -v
```

### 8.2 性能测试定期运行

```yaml
# .github/workflows/websocket-load-test.yml
on:
  schedule:
    - cron: "0 2 * * 0"  # 每周日 02:00 UTC
  pull_request:
    paths:
      - "backend/app/core/connection_manager.py"
jobs:
  load:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Locust load test
        run: |
          docker-compose up -d backend redis postgres
          sleep 10
          cd backend && poetry run locust -f tests/load/test_websocket_load.py \
            --headless --users 100 --spawn-rate 10 --run-time 60s
```

---

## 9. 测试数据

### 9.1 Fixture 数据

```python
# tests/fixtures/websocket_messages.py
VALID_MESSAGES = [
    {"type": "ping", "data": {}, ...},
    {"type": "agent.status", "data": {...}, ...},
    # ... 17 种消息类型样本
]

INVALID_MESSAGES = [
    {"type": "unknown"},  # 缺必填字段
    {"data": {}},  # 缺 type
    {"type": "ping", "data": {}},  # 缺 timestamp/id
]
```

### 9.2 用户和 Token

```python
# tests/fixtures/users.py
TEST_USERS = {
    "admin": {"id": "admin-1", "token": "valid.jwt.admin", "role": "admin"},
    "developer": {"id": "dev-1", "token": "valid.jwt.dev", "role": "developer"},
    "viewer": {"id": "viewer-1", "token": "valid.jwt.viewer", "role": "viewer"},
}
```

---

## 10. 验收清单

### 10.1 单元测试验收

- [ ] 23 个 ConnectionManager 测试全部通过
- [ ] 33+ 个消息协议测试全部通过
- [ ] 覆盖率 ≥ 85%
- [ ] 测试执行 < 10s
- [ ] 无 flaky 测试

### 10.2 集成测试验收

- [ ] 6 个集成测试全部通过
- [ ] JWT 验证生效
- [ ] 多用户隔离验证
- [ ] 断线重连工作

### 10.3 压力测试验收

- [ ] 100 并发连接稳定
- [ ] ping-pong p99 < 200ms
- [ ] 内存占用 < 50MB
- [ ] 无连接泄漏

### 10.4 E2E 测试验收

- [ ] 5 个关键场景通过
- [ ] 实时 UI 更新正常
- [ ] 自动重连工作
- [ ] 跨浏览器兼容

---

## 11. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| WebSocket 测试不稳定 | 中 | 高 | Mock + 重试机制 |
| 100 并发压不过 | 低 | 中 | 优化锁粒度、asyncio.gather |
| JWT 集成问题 | 中 | 高 | Sprint 1 接口契约明确 |
| Locust 环境复杂 | 中 | 低 | Docker Compose 一键启动 |

---

**变更记录**:

- 2026-06-17: v1.0 初版设计（tom）
