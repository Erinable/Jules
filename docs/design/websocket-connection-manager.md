# WebSocket ConnectionManager 设计

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #05de8d26 (Sprint 2)
**依赖**: Sprint 1 (认证) - 仅运行时验证需要

---

## 1. 概述

定义 WebSocket 连接管理器（ConnectionManager）的设计，负责维护客户端连接池、消息路由、心跳检测、断线重连。本文档为 Sprint 2 核心组件，不依赖 Sprint 1 实现（仅 JWT 验证 hook 需要 Sprint 1）。

### 设计目标

- **高并发**: 支持 100+ 同时连接
- **可扩展**: 易于添加新事件类型
- **可观测**: 完善的指标和日志
- **健壮性**: 单连接异常不影响其他连接
- **低延迟**: 消息推送 < 100ms

---

## 2. 核心数据结构

### 2.1 Connection（单连接抽象）

```python
from dataclasses import dataclass, field
from datetime import datetime
from fastapi import WebSocket


@dataclass(frozen=True)
class Connection:
    """单个 WebSocket 连接的不可变表示"""

    connection_id: str           # UUID，唯一标识
    user_id: str                 # 用户 ID（来自 Sprint 1 JWT）
    websocket: WebSocket         # FastAPI WebSocket 实例
    connected_at: datetime
    last_ping_at: datetime
    subscriptions: frozenset[str] = field(default_factory=frozenset)
    # 订阅的 channel，如 {"progress:run_123", "agent:status"}

    @property
    def is_alive(self) -> bool:
        """连接是否活跃（基于心跳）"""
        elapsed = (datetime.utcnow() - self.last_ping_at).total_seconds()
        return elapsed < 60  # 60s 未收到 ping 视为断开
```

### 2.2 ConnectionManager（连接池管理）

```python
from abc import ABC, abstractmethod


class ConnectionManager(ABC):
    """连接管理器抽象接口"""

    @abstractmethod
    async def connect(self, websocket: WebSocket, user_id: str) -> Connection:
        """接受连接并加入池"""

    @abstractmethod
    async def disconnect(self, connection_id: str) -> None:
        """断开连接并从池中移除"""

    @abstractmethod
    async def send_to_user(self, user_id: str, message: WSMessage) -> int:
        """向指定用户的所有连接推送消息，返回成功送达数"""

    @abstractmethod
    async def broadcast(self, message: WSMessage, channel: str | None = None) -> int:
        """广播消息（可选 channel 过滤），返回送达数"""

    @abstractmethod
    async def subscribe(self, connection_id: str, channel: str) -> None:
        """订阅 channel"""

    @abstractmethod
    async def unsubscribe(self, connection_id: str, channel: str) -> None:
        """取消订阅 channel"""

    @abstractmethod
    def get_stats(self) -> ConnectionStats:
        """获取连接统计"""
```

### 2.3 ConnectionStats（统计）

```python
@dataclass(frozen=True)
class ConnectionStats:
    total_connections: int
    unique_users: int
    channels_count: int
    connections_per_user: dict[str, int]  # 仅前 10 个用户用于展示

    def to_dict(self) -> dict:
        return {
            "total_connections": self.total_connections,
            "unique_users": self.unique_users,
            "channels_count": self.channels_count,
            "top_users_by_connections": self.connections_per_user,
        }
```

---

## 3. 具体实现（InMemoryConnectionManager）

### 3.1 数据结构

```python
import asyncio
from collections import defaultdict


class InMemoryConnectionManager(ConnectionManager):
    """内存版连接管理器（单实例）"""

    def __init__(self) -> None:
        # 主索引：connection_id → Connection
        self._connections: dict[str, Connection] = {}

        # 反向索引：user_id → set[connection_id]
        self._user_connections: dict[str, set[str]] = defaultdict(set)

        # channel 索引：channel → set[connection_id]
        self._channel_subscribers: dict[str, set[str]] = defaultdict(set)

        # 锁（保证并发安全）
        self._lock = asyncio.Lock()

        # 后台任务
        self._heartbeat_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None
```

### 3.2 连接生命周期

```python
    async def connect(self, websocket: WebSocket, user_id: str) -> Connection:
        # 接受 WebSocket 握手
        await websocket.accept()

        async with self._lock:
            connection = Connection(
                connection_id=str(uuid.uuid4()),
                user_id=user_id,
                websocket=websocket,
                connected_at=datetime.utcnow(),
                last_ping_at=datetime.utcnow(),
            )
            # 不可变更新：写入新连接对象
            self._connections = {**self._connections, connection.connection_id: connection}
            self._user_connections[user_id] = self._user_connections[user_id] | {connection.connection_id}

        logger.info(f"Connection {connection.connection_id} accepted for user {user_id}")
        return connection

    async def disconnect(self, connection_id: str) -> None:
        async with self._lock:
            conn = self._connections.get(connection_id)
            if not conn:
                return

            # 不可变更新：从所有索引中移除
            self._connections = {k: v for k, v in self._connections.items() if k != connection_id}

            user_conns = self._user_connections.get(conn.user_id, set()) - {connection_id}
            if user_conns:
                self._user_connections[conn.user_id] = user_conns
            else:
                self._user_connections.pop(conn.user_id, None)

            for channel in list(self._channel_subscribers.keys()):
                subs = self._channel_subscribers[channel] - {connection_id}
                if subs:
                    self._channel_subscribers[channel] = subs
                else:
                    self._channel_subscribers.pop(channel, None)

            # 关闭 WebSocket
            try:
                await conn.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket {connection_id}: {e}")
```

### 3.3 消息推送

```python
    async def send_to_user(self, user_id: str, message: WSMessage) -> int:
        connection_ids = self._user_connections.get(user_id, set())
        if not connection_ids:
            return 0

        success_count = 0
        # 并发推送，单连接失败不影响其他
        tasks = [self._safe_send(cid, message) for cid in connection_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if r is True:
                success_count += 1
            elif isinstance(r, Exception):
                logger.warning(f"Send error: {r}")
        return success_count

    async def _safe_send(self, connection_id: str, message: WSMessage) -> bool:
        """安全推送，自动清理失败连接"""
        conn = self._connections.get(connection_id)
        if not conn or not conn.is_alive:
            await self.disconnect(connection_id)
            return False

        try:
            await conn.websocket.send_text(message.model_dump_json())
            return True
        except (WebSocketDisconnect, ConnectionClosedError):
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Unexpected send error to {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
```

---

## 4. 心跳检测

### 4.1 心跳协议

```
客户端每 30s 发送: {"type": "ping", "timestamp": "..."}
服务端立即响应:    {"type": "pong", "timestamp": "..."}
```

### 4.2 服务端心跳任务

```python
    async def _heartbeat_loop(self) -> None:
        """后台任务：每 60s 检查一次连接活跃度"""
        while True:
            await asyncio.sleep(60)
            now = datetime.utcnow()
            dead_connections = [
                cid for cid, conn in self._connections.items()
                if (now - conn.last_ping_at).total_seconds() > 90  # 3 个 ping 周期
            ]
            for cid in dead_connections:
                logger.info(f"Heartbeat timeout, disconnecting {cid}")
                await self.disconnect(cid)

    def start_heartbeat(self) -> None:
        if not self._heartbeat_task or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop_heartbeat(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
```

---

## 5. 并发处理策略

### 5.1 锁策略

- **粒度**: 全局 `asyncio.Lock`（v1.1 简单方案）
- **保护范围**: 仅修改索引时加锁
- **推送不加锁**: `send_to_user` 读取索引后释放锁

**v1.2 优化**（如性能不足）:

- 分片锁（按 user_id hash 分 16 个分片）
- 读写锁（读多写少场景）

### 5.2 异步并发

- `asyncio.gather` 并发推送同一用户的多个连接
- 失败隔离（`return_exceptions=True`）
- 超时控制（单连接推送 5s 超时）

```python
    async def _safe_send_with_timeout(self, conn: Connection, message: WSMessage) -> bool:
        try:
            await asyncio.wait_for(
                conn.websocket.send_text(message.model_dump_json()),
                timeout=5.0
            )
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Send timeout to {conn.connection_id}")
            await self.disconnect(conn.connection_id)
            return False
```

---

## 6. 容量规划（100 并发连接）

### 6.1 资源消耗估算

| 资源 | 单连接 | 100 连接 | 备注 |
|------|--------|----------|------|
| 内存 | ~50KB | ~5MB | Connection 对象 + 缓冲区 |
| CPU（空闲） | ~0% | ~1% | 心跳检测 |
| CPU（推送） | ~0.1ms | ~10ms | 并发发送 |
| 网络（空闲） | 100B/s | 10KB/s | 心跳流量 |
| 网络（推送） | 1KB/msg | 100KB/批次 | 实际消息 |

### 6.2 性能基准（目标）

| 指标 | 目标 | 测试方法 |
|------|------|---------|
| 100 连接建立 | < 2s | Locust |
| 单消息推送延迟 | < 100ms | p99 |
| 100 用户广播延迟 | < 500ms | p99 |
| 心跳检测周期 | 60s | 配置 |
| 内存占用 | < 50MB | psutil |

---

## 7. 多实例扩展（v2.0 规划）

当前设计为单实例内存版。多实例部署需 Redis Pub/Sub：

```python
class RedisBackedConnectionManager(InMemoryConnectionManager):
    """v2.0: 支持 horizontally scale"""

    def __init__(self, redis: Redis):
        super().__init__()
        self._redis = redis
        self._pubsub = redis.pubsub()

    async def send_to_user(self, user_id: str, message: WSMessage) -> int:
        # 1. 发布到 Redis channel
        await self._redis.publish(f"user:{user_id}", message.model_dump_json())
        # 2. 本地连接直接发送
        return await super().send_to_user(user_id, message)

    async def _subscribe_loop(self) -> None:
        """订阅 Redis，跨实例推送"""
        async for msg in self._pubsub.listen():
            # 解析 channel 提取 user_id
            # 调用 super().send_to_user 本地推送
            ...
```

---

## 8. 错误处理

### 8.1 错误分类

| 错误类型 | 处理策略 |
|---------|---------|
| WebSocketDisconnect | 清理连接，记录日志 |
| ConnectionClosedError | 清理连接，记录日志 |
| TimeoutError | 清理连接，告警 |
| JSONEncodeError | 丢弃消息，告警 |
| 未知异常 | 清理连接，记录堆栈 |

### 8.2 错误消息推送

```python
async def send_error(websocket: WebSocket, code: str, message: str) -> None:
    """向客户端推送错误消息"""
    error_msg = WSMessage(
        type="system.error",
        data={"code": code, "message": message},
        timestamp=datetime.utcnow(),
    )
    await websocket.send_text(error_msg.model_dump_json())
```

---

## 9. 可观测性

### 9.1 指标（Prometheus）

```python
# 关键指标
connection_total = Counter("ws_connections_total", "Total WebSocket connections")
connection_active = Gauge("ws_connections_active", "Active WebSocket connections")
messages_sent = Counter("ws_messages_sent_total", "Messages sent", ["type"])
messages_failed = Counter("ws_messages_failed_total", "Failed sends")
send_latency = Histogram("ws_send_latency_seconds", "Send latency")
```

### 9.2 日志（结构化）

```python
logger.info({
    "event": "connection_accepted",
    "connection_id": cid,
    "user_id": uid,
    "total_active": len(self._connections),
})

logger.warning({
    "event": "send_failed",
    "connection_id": cid,
    "error": str(e),
    "message_type": msg.type,
})
```

---

## 10. 测试策略

### 10.1 单元测试

- 连接/断开流程
- user_id 索引正确性
- channel 订阅/退订
- 心跳超时清理
- 并发推送（100 模拟连接）

### 10.2 集成测试

- 真实 WebSocket 客户端连接
- JWT 验证（Sprint 1 完成后）
- 多用户隔离

### 10.3 压力测试（Locust）

```python
# tests/load/test_websocket_load.py
class WebSocketUser(User):
    def on_start(self):
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://localhost:8000/ws/{self.user_id}?token={self.token}")

    @task
    def ping(self):
        self.ws.send(json.dumps({"type": "ping"}))
        self.ws.recv()  # pong
```

---

## 11. 待决问题

| # | 问题 | 默认建议 |
|---|------|---------|
| 1 | 是否支持同一用户多设备登录？ | 是，每设备独立连接 |
| 2 | 最大单用户连接数？ | 5（防滥用） |
| 3 | 消息推送失败重试？ | 不重试，丢弃 |
| 4 | QoS 级别？ | v1.1 best-effort，v1.2 at-least-once |

---

**变更记录**:

- 2026-06-17: v1.0 初版设计（tom）
