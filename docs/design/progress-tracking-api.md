# 进度追踪 API 设计

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #56c7bb89 (Sprint 3)
**依赖**: Sprint 1 (认证授权) - 实施阶段需要

---

## 1. 概述

定义进度追踪系统的 REST API 端点契约。本文档仅设计接口，不实现代码。实施需等待 Sprint 1（JWT/RBAC）和 Sprint 2（WebSocket）完成。

### 设计原则

- **RESTful 风格**: 资源导向，标准 HTTP 方法
- **统一响应格式**: `{success, data, error, meta}` 信封
- **分页标准**: `meta: {total, page, limit}`
- **权限分层**: admin / developer / viewer 三种角色

---

## 2. 端点概览

| 方法 | 路径 | 描述 | 角色 |
|------|------|------|------|
| GET | `/api/v1/progress/{run_id}` | 获取单次执行进度 | viewer+ |
| GET | `/api/v1/progress/{run_id}/logs` | 获取执行日志（分页） | viewer+ |
| GET | `/api/v1/progress/{run_id}/replay` | 获取回放数据 | viewer+ |
| GET | `/api/v1/progress` | 列出当前用户进度 | developer+ |
| GET | `/api/v1/progress/all` | 列出全部进度（admin） | admin |
| POST | `/api/v1/progress/{run_id}/cancel` | 取消执行 | developer+ |
| POST | `/api/v1/progress/{run_id}/pause` | 暂停执行 | developer+ |
| POST | `/api/v1/progress/{run_id}/resume` | 恢复执行 | developer+ |
| DELETE | `/api/v1/progress/{run_id}` | 删除执行记录 | admin |
| WS | `/ws/{user_id}` | 实时进度推送 | developer+ |

---

## 3. 统一响应格式

### 3.1 成功响应

```json
{
  "success": true,
  "data": { /* 资源 */ },
  "error": null,
  "meta": {
    "timestamp": "2026-06-17T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### 3.2 分页响应

```json
{
  "success": true,
  "data": [ /* 资源列表 */ ],
  "error": null,
  "meta": {
    "total": 42,
    "page": 1,
    "limit": 20,
    "has_next": true
  }
}
```

### 3.3 错误响应

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PROGRESS_NOT_FOUND",
    "message": "Execution progress not found",
    "details": {"run_id": "xxx"}
  },
  "meta": {
    "timestamp": "2026-06-17T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## 4. 端点详细设计

### 4.1 GET /api/v1/progress/{run_id}

获取单次执行的进度详情。

**权限**: `viewer` + (只能查看自己的)；`admin` 可查看任意用户

**响应 (200)**:

```json
{
  "success": true,
  "data": {
    "run_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-123",
    "status": "running",
    "current_step": "coder",
    "overall_percentage": 45.0,
    "eta_seconds": 150,
    "started_at": "2026-06-17T10:25:00Z",
    "updated_at": "2026-06-17T10:28:30Z",
    "completed_at": null,
    "steps": [
      {
        "name": "researcher",
        "status": "completed",
        "started_at": "2026-06-17T10:25:00Z",
        "completed_at": "2026-06-17T10:25:30Z",
        "duration_ms": 30000,
        "retry_count": 0,
        "error_message": null
      },
      {
        "name": "planner",
        "status": "completed",
        "started_at": "2026-06-17T10:25:30Z",
        "completed_at": "2026-06-17T10:26:15Z",
        "duration_ms": 45000,
        "retry_count": 0,
        "error_message": null
      },
      {
        "name": "coder",
        "status": "running",
        "started_at": "2026-06-17T10:26:15Z",
        "completed_at": null,
        "duration_ms": 135000,
        "retry_count": 0,
        "error_message": null
      },
      {
        "name": "reviewer",
        "status": "pending",
        "started_at": null,
        "completed_at": null,
        "duration_ms": null,
        "retry_count": 0,
        "error_message": null
      },
      {
        "name": "tester",
        "status": "pending",
        "started_at": null,
        "completed_at": null,
        "duration_ms": null,
        "retry_count": 0,
        "error_message": null
      }
    ],
    "total_duration_ms": 210000,
    "retry_count": 0
  }
}
```

**错误**:

- 404 `PROGRESS_NOT_FOUND` - run_id 不存在
- 403 `FORBIDDEN` - viewer 查看他人进度

---

### 4.2 GET /api/v1/progress/{run_id}/logs

获取执行日志（支持分页、过滤）。

**权限**: `viewer` +

**查询参数**:
| 参数 | 类型 | 默认 | 描述 |
|------|------|------|------|
| `step` | string | - | 按步骤过滤（researcher/planner/coder/reviewer/tester） |
| `level` | string | - | 按级别过滤（info/warn/error/debug） |
| `page` | int | 1 | 页码 |
| `limit` | int | 50 | 每页数量（max 200） |
| `order` | string | asc | 排序（asc/desc） |

**响应 (200)**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "step": "planner",
      "level": "info",
      "message": "分析任务需求...",
      "timestamp": "2026-06-17T10:25:30.123Z",
      "sequence_num": 1,
      "raw_output": null
    },
    {
      "id": 2,
      "step": "planner",
      "level": "info",
      "message": "生成架构方案 v1",
      "timestamp": "2026-06-17T10:25:33.456Z",
      "sequence_num": 2,
      "raw_output": "## Architecture\n..."
    }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "limit": 50,
    "has_next": false
  }
}
```

---

### 4.3 GET /api/v1/progress/{run_id}/replay

获取执行回放数据（按时间轴，包含状态变更和日志）。

**权限**: `viewer` +

**查询参数**:
| 参数 | 类型 | 默认 | 描述 |
|------|------|------|------|
| `start_time` | ISO8601 | - | 起始时间 |
| `end_time` | ISO8601 | - | 结束时间 |
| `include_logs` | bool | true | 是否包含日志 |
| `speed` | float | 1.0 | 回放速度（仅客户端提示） |

**响应 (200)**:

```json
{
  "success": true,
  "data": {
    "run_id": "...",
    "total_events": 87,
    "total_duration_ms": 210000,
    "timeline": [
      {
        "timestamp": "2026-06-17T10:25:00.000Z",
        "type": "transition",
        "data": {
          "step": null,
          "from": "queued",
          "to": "running",
          "reason": "scheduler_picked"
        }
      },
      {
        "timestamp": "2026-06-17T10:25:00.001Z",
        "type": "transition",
        "data": {
          "step": "researcher",
          "from": "pending",
          "to": "running",
          "reason": "step_started"
        }
      },
      {
        "timestamp": "2026-06-17T10:25:00.500Z",
        "type": "log",
        "data": {
          "step": "researcher",
          "level": "info",
          "message": "开始分析..."
        }
      }
      // ... more events
    ]
  }
}
```

---

### 4.4 GET /api/v1/progress

列出当前用户的执行进度（分页）。

**权限**: `developer` + (viewers 仅能通过 run_id 单独查询)

**查询参数**:
| 参数 | 类型 | 默认 | 描述 |
|------|------|------|------|
| `status` | string | - | 按状态过滤（running/completed/failed） |
| `agent_type` | string | - | 按 Agent 类型过滤 |
| `page` | int | 1 | 页码 |
| `limit` | int | 20 | 每页数量 |

**响应**: 同统一分页格式，每项为 `RunProgress` 摘要（不含详细 steps）

---

### 4.5 GET /api/v1/progress/all

列出全部执行进度（仅 admin）。

**权限**: `admin`

**响应**: 同 4.4，但包含所有用户

---

### 4.6 POST /api/v1/progress/{run_id}/cancel

取消正在执行的 Agent。

**权限**: `developer` + (仅能取消自己的)；`admin` 可取消任意

**请求体**:

```json
{
  "reason": "user_requested",
  "force": false
}
```

- `force: true`: 立即终止（可能丢失数据）
- `force: false`: 优雅终止（等待当前 LLM 请求完成）

**响应 (202)**:

```json
{
  "success": true,
  "data": {
    "run_id": "...",
    "previous_status": "running",
    "new_status": "cancelled",
    "cancelled_step": "coder",
    "message": "Cancellation requested, will complete after current LLM call"
  }
}
```

**错误**:

- 409 `CONFLICT` - 已经是终态（completed/failed/cancelled）
- 403 `FORBIDDEN` - developer 取消他人任务

---

### 4.7 POST /api/v1/progress/{run_id}/pause

暂停执行。

**权限**: `developer` +

**请求体**:

```json
{
  "duration_seconds": 300
}
```

**响应 (202)**: 同 4.6，`new_status: paused`

**注意**: 暂停超过 1 小时自动取消，释放调度资源

---

### 4.8 POST /api/v1/progress/{run_id}/resume

恢复已暂停的执行。

**权限**: `developer` +

**响应 (200)**:

```json
{
  "success": true,
  "data": {
    "run_id": "...",
    "previous_status": "paused",
    "new_status": "running",
    "resumed_step": "coder"
  }
}
```

**错误**:

- 409 `CONFLICT` - 不是暂停状态
- 410 `GONE` - 暂停超时已自动取消

---

### 4.9 DELETE /api/v1/progress/{run_id}

删除执行记录（软删除）。

**权限**: `admin`

**响应 (204)**: 无内容

**说明**: 软删除，数据保留 30 天后物理删除

---

### 4.10 WS /ws/{user_id}

实时进度推送（详见 Sprint 2 设计文档）。

**权限**: `developer` +

**事件类型**（与进度追踪相关）:

- `progress.step.started` - 步骤开始
- `progress.step.completed` - 步骤完成
- `progress.step.failed` - 步骤失败
- `progress.updated` - 进度百分比更新
- `progress.log.appended` - 新日志
- `progress.run.completed` - 执行完成

---

## 5. Pydantic Schema 定义（待实施）

```python
# app/schemas/progress.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.agent_progress import StepState, RunStatus, AgentStep


class ProgressResponse(BaseModel):
    run_id: str
    user_id: str
    status: RunStatus
    current_step: AgentStep | None = None
    overall_percentage: float
    eta_seconds: int | None = None
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    steps: list[StepState]
    total_duration_ms: int | None = None
    retry_count: int = 0


class ProgressListResponse(BaseModel):
    items: list[ProgressResponse]
    total: int
    page: int
    limit: int


class LogEntry(BaseModel):
    id: int
    step: AgentStep
    level: str
    message: str
    timestamp: datetime
    sequence_num: int
    raw_output: str | None = None


class CancelRequest(BaseModel):
    reason: str = "user_requested"
    force: bool = False


class CancelResponse(BaseModel):
    run_id: str
    previous_status: RunStatus
    new_status: RunStatus
    cancelled_step: AgentStep | None = None
    message: str
```

---

## 6. 错误码定义

| HTTP | 错误码 | 描述 |
|------|--------|------|
| 400 | `INVALID_REQUEST` | 请求参数无效 |
| 401 | `UNAUTHORIZED` | 未认证 |
| 403 | `FORBIDDEN` | 无权限 |
| 404 | `PROGRESS_NOT_FOUND` | 进度记录不存在 |
| 409 | `INVALID_STATE_TRANSITION` | 非法状态转换 |
| 409 | `ALREADY_TERMINAL` | 已是终态 |
| 410 | `GONE` | 资源已删除 |
| 429 | `RATE_LIMITED` | 请求频率超限 |
| 500 | `INTERNAL_ERROR` | 服务器错误 |

---

## 7. 速率限制

| 端点 | 限制 | 说明 |
|------|------|------|
| GET /progress/* | 100 req/min | 查询接口 |
| POST /cancel | 10 req/min | 控制操作 |
| POST /pause/resume | 5 req/min | 控制操作 |
| WS /ws/{user_id} | 1 connection/user | 单连接 |

---

## 8. OpenAPI 文档集成

所有端点需在 FastAPI 中通过装饰器声明：

- 完整的 response_model
- 错误响应示例
- 权限依赖 (`Depends(require_role("developer"))`)
- 标签分组 (`tags=["progress"]`)

生成的 OpenAPI 文档自动反映在 `/docs` (Swagger UI) 和 `/redoc`。

---

## 9. 测试契约

每个端点至少覆盖以下场景：

| 场景 | 类型 |
|------|------|
| 正常请求 + 正确权限 | unit + integration |
| 未认证 (401) | integration |
| 无权限 (403) | integration |
| 资源不存在 (404) | integration |
| 非法状态转换 (409) | unit |
| 分页边界 | unit |
| 速率限制 (429) | integration |

---

## 10. 待决问题

| # | 问题 | 默认建议 |
|---|------|---------|
| 1 | 是否支持批量查询（POST /progress/batch）？ | v1.1 不支持，v1.2 考虑 |
| 2 | 进度详情是否缓存？ | Redis 缓存 30s，状态变更时失效 |
| 3 | 日志导出（CSV/JSON）？ | v1.2 实现，需权限审计 |

---

**变更记录**:

- 2026-06-17: v1.0 初版设计（tom）
