# Agent 执行进度追踪 - 状态机设计

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #56c7bb89 (Sprint 3)
**依赖**: Sprint 2 (WebSocket) - 仅实施阶段需要

---

## 1. 概述

本文档定义 Agent 执行的 5 步骤状态机，包括状态枚举、流转规则、异常处理、持久化策略。该状态机为 Sprint 3 进度追踪系统的核心数据模型。

### 设计原则

- **不可变性** (Immutability): 状态变更生成新对象，避免原地修改
- **可追溯** (Traceable): 每次状态变更记录时间戳和触发原因
- **可回放** (Replayable): 完整状态变更序列支持历史回放
- **可扩展** (Extensible): 未来支持自定义步骤（如 v2.0 多 Agent 协作）

---

## 2. 步骤定义

Agent 执行采用线性流水线模型，包含 5 个固定步骤：

| 顺序 | 步骤名 | 标识 | 职责 | 默认权重 |
|------|--------|------|------|----------|
| 1 | Researcher | `researcher` | 需求分析、竞品调研 | 0.15 |
| 2 | Planner | `planner` | 架构设计、任务拆解 | 0.15 |
| 3 | Coder | `coder` | 代码生成、实现 | 0.40 |
| 4 | Reviewer | `reviewer` | 代码审查、质量检查 | 0.15 |
| 5 | Tester | `tester` | 单元测试、集成测试 | 0.15 |

**权重说明**:
- 权重总和为 1.0，用于进度百分比计算
- Coder 步骤权重最高（0.40），因为耗时最长
- 权重可在运行时基于历史数据动态调整

---

## 3. 状态枚举

### 3.1 步骤状态 (StepStatus)

```python
from enum import Enum


class StepStatus(str, Enum):
    """单个步骤的执行状态"""
    PENDING = "pending"        # 未开始
    RUNNING = "running"        # 执行中
    COMPLETED = "completed"    # 成功完成
    FAILED = "failed"          # 失败（不可恢复）
    SKIPPED = "skipped"        # 条件跳过（如无测试需求）
    RETRYING = "retrying"      # 重试中（Reviewer→Coder 修复循环）
    CANCELLED = "cancelled"    # 用户取消
```

### 3.2 执行状态 (RunStatus)

```python
class RunStatus(str, Enum):
    """完整 Agent 执行的状态"""
    QUEUED = "queued"            # 排队等待调度
    RUNNING = "running"          # 正在执行
    PAUSED = "paused"            # 用户暂停
    COMPLETED = "completed"      # 全部步骤成功
    FAILED = "failed"            # 某步骤失败
    CANCELLED = "cancelled"      # 用户取消
    TIMEOUT = "timeout"          # 超时（默认 300s）
```

### 3.3 步骤枚举 (AgentStep)

```python
class AgentStep(str, Enum):
    RESEARCHER = "researcher"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"

    @classmethod
    def ordered(cls) -> list["AgentStep"]:
        """返回顺序步骤列表"""
        return [cls.RESEARCHER, cls.PLANNER, cls.CODER, cls.REVIEWER, cls.TESTER]
```

---

## 4. 状态流转规则

### 4.1 正常流程

```
[pending] → [running] → [completed] → (next step: pending → running → ...)
```

**触发条件**:
- `pending → running`: 前置步骤全部 `completed`，或本步骤是第一步
- `running → completed`: 步骤执行成功，记录 `completed_at` 和 `duration_ms`

### 4.2 异常流程

#### 4.2.1 失败重试（Reviewer→Coder 修复循环）

```
[running] → [failed]
              ↓
        retry_count < MAX_RETRIES (3)?
              ↓ yes              ↓ no
        [retrying]            终止执行，RunStatus = FAILED
              ↓
        [running] (重试)
```

**重试规则**:
- 最大重试次数: `MAX_RETRIES = 3`
- 仅 Coder 步骤支持重试（Reviewer 反馈后修复）
- 每次重试递增 `retry_count`
- 超过上限则整次执行标记为 FAILED

#### 4.2.2 条件跳过

```
[pending] → [skipped]
```

**跳过场景**:
- Tester 步骤在配置 `enable_tests=False` 时跳过
- Reviewer 步骤在配置 `enable_review=False` 时跳过
- 跳过不视为失败，进度百分比正常推进

#### 4.2.3 用户取消

```
任何状态 → [cancelled]
```

**取消规则**:
- 用户主动调用 `POST /api/v1/progress/{run_id}/cancel`
- 当前 RUNNING 步骤等待当前 LLM 请求完成后终止（避免浪费 token）
- 未开始步骤标记为 `cancelled`

#### 4.2.4 超时

```
[running] → (timeout 300s) → [failed]
```

**超时规则**:
- 单步骤默认超时: 300 秒（可通过 Agent 配置覆盖）
- 总执行超时: 1800 秒（30 分钟）
- 超时后步骤标记为 FAILED，不可重试

### 4.3 流转状态机图

```
                          ┌─────────────────────────────┐
                          │                             │
                          ▼                             │ retry
[pending] ───start──► [running] ───success──► [completed]
    │                     │
    │                     ├──failure (retry<3)──► [retrying] ──► [running]
    │                     │
    │                     ├──failure (retry=3)──► [failed]
    │                     │
    │                     └──timeout────────────► [failed]
    │
    ├──skip────────────► [skipped]
    │
    └──cancel──────────► [cancelled]
```

---

## 5. 数据模型

### 5.1 步骤状态对象（不可变）

```python
from datetime import datetime
from pydantic import BaseModel, Field


class StepState(BaseModel):
    """单个步骤的状态快照（不可变）"""

    name: AgentStep
    status: StepStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    error_message: str | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        frozen = True  # Pydantic 不可变模式


class RunProgress(BaseModel):
    """完整执行的进度快照（不可变）"""

    run_id: str
    user_id: str
    status: RunStatus
    steps: list[StepState]
    current_step: AgentStep | None = None
    overall_percentage: float = 0.0
    eta_seconds: int | None = None
    started_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
```

**不可变性实现**:
- 状态变更通过 `dataclasses.replace()` 或 Pydantic `model_copy(update={...})` 生成新对象
- 不允许直接修改字段（`frozen = True`）

### 5.2 状态变更事件

每次状态变更记录为不可变事件，用于回溯和审计：

```python
class StateTransition(BaseModel):
    """状态变更事件"""

    id: str
    run_id: str
    step: AgentStep | None  # None 表示整次执行的状态变更
    from_status: StepStatus | RunStatus
    to_status: StepStatus | RunStatus
    timestamp: datetime
    reason: str  # "llm_completed" / "user_cancel" / "timeout" / "retry"
    actor: str  # "system" / "user:{user_id}"
    metadata: dict = Field(default_factory=dict)
```

---

## 6. 数据库 Schema

### 6.1 execution_progress 表（主表）

```sql
CREATE TABLE execution_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),

    -- 状态快照
    status VARCHAR(20) NOT NULL,  -- RunStatus 枚举值
    current_step VARCHAR(20),      -- AgentStep 枚举值或 NULL
    overall_percentage FLOAT NOT NULL DEFAULT 0.0,
    eta_seconds INT,

    -- 步骤状态（JSONB，避免 join 开销）
    steps JSONB NOT NULL,  -- list[StepState] 序列化

    -- 时间戳
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 元数据
    total_duration_ms INT,
    retry_count INT DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

-- 索引
CREATE INDEX idx_progress_user_started ON execution_progress(user_id, started_at DESC);
CREATE INDEX idx_progress_run ON execution_progress(run_id);
CREATE INDEX idx_progress_status ON execution_progress(status) WHERE status IN ('running', 'queued');
```

### 6.2 execution_transitions 表（状态变更日志）

```sql
CREATE TABLE execution_transitions (
    id BIGSERIAL PRIMARY KEY,
    progress_id UUID NOT NULL REFERENCES execution_progress(id) ON DELETE CASCADE,
    step VARCHAR(20),
    from_status VARCHAR(20) NOT NULL,
    to_status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason VARCHAR(100),
    actor VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_transitions_progress_time ON execution_transitions(progress_id, timestamp);
```

### 6.3 execution_logs 表（执行日志）

```sql
CREATE TABLE execution_logs (
    id BIGSERIAL PRIMARY KEY,
    progress_id UUID NOT NULL REFERENCES execution_progress(id) ON DELETE CASCADE,
    step VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,  -- info/warn/error/debug
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_output TEXT,             -- LLM 原始输出（可选）
    sequence_num BIGINT NOT NULL  -- 单调递增序列号，保证顺序
);

CREATE INDEX idx_logs_progress_time ON execution_logs(progress_id, timestamp);
CREATE INDEX idx_logs_progress_seq ON execution_logs(progress_id, sequence_num);
```

### 6.4 Alembic 迁移规划

```python
# alembic/versions/xxx_add_progress_tables.py
"""add progress tables

Revision ID: xxx
Revises: previous_revision
Create Date: 2026-07-xx
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.create_table("execution_progress", ...)
    op.create_table("execution_transitions", ...)
    op.create_table("execution_logs", ...)


def downgrade() -> None:
    op.drop_table("execution_logs")
    op.drop_table("execution_transitions")
    op.drop_table("execution_progress")
```

---

## 7. 状态变更 API（仓库层接口）

```python
# app/repositories/progress_repository.py
from abc import ABC, abstractmethod


class ProgressRepository(ABC):
    """进度数据仓库（抽象接口，便于测试 mock）"""

    @abstractmethod
    async def create(self, run_id: str, user_id: str) -> RunProgress:
        """创建新的执行进度记录（所有步骤初始化为 pending）"""

    @abstractmethod
    async def get_by_run(self, run_id: str) -> RunProgress | None:
        """获取执行进度"""

    @abstractmethod
    async def list_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[RunProgress]:
        """获取用户的执行历史"""

    @abstractmethod
    async def update_step(
        self, run_id: str, step: AgentStep, new_status: StepStatus, reason: str
    ) -> RunProgress:
        """更新步骤状态（生成新快照，记录 transition）"""

    @abstractmethod
    async def append_log(
        self,
        run_id: str,
        step: AgentStep,
        level: str,
        message: str,
        raw_output: str | None = None,
    ) -> None:
        """追加执行日志"""

    @abstractmethod
    async def get_transitions(self, run_id: str) -> list[StateTransition]:
        """获取状态变更历史（用于回放）"""

    @abstractmethod
    async def get_logs(
        self, run_id: str, step: AgentStep | None = None, level: str | None = None
    ) -> list[ExecutionLog]:
        """获取执行日志（支持过滤）"""
```

---

## 8. 测试策略

### 8.1 单元测试覆盖

- **状态枚举**: 验证 `AgentStep.ordered()` 返回正确顺序
- **状态转换函数**: 验证所有合法转换
- **进度计算**: 验证不同步骤组合下的百分比
- **不可变性**: 验证 `StepState` 和 `RunProgress` 无法被修改

### 8.2 测试用例示例

```python
def test_step_state_is_frozen():
    """验证 StepState 不可变"""
    state = StepState(name=AgentStep.RESEARCHER, status=StepStatus.PENDING)
    with pytest.raises(ValidationError):
        state.status = StepStatus.RUNNING  # type: ignore


def test_progress_calculation():
    """验证进度百分比"""
    steps = [
        StepState(name=AgentStep.RESEARCHER, status=StepStatus.COMPLETED),
        StepState(name=AgentStep.PLANNER, status=StepStatus.RUNNING, duration_ms=5000),
        StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
        StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
        StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
    ]
    # Researcher 完成 = 15%，Planner 运行中部分进度
    pct = ProgressCalculator.calculate(steps)
    assert 15.0 <= pct < 30.0


def test_retry_transitions():
    """验证 Reviewer→Coder 重试循环"""
    # Coder failed → retrying → running → failed (retry_count=3) → run FAILED
    ...
```

---

## 9. 待决问题

| # | 问题 | 默认建议 | 决策方 |
|---|------|---------|--------|
| 1 | 是否支持并发步骤（v2.0 多 Agent）？ | 当前线性，v2.0 扩展 | architect |
| 2 | 步骤权重是否可配置？ | 默认权重 + 数据库覆盖 | team-lead |
| 3 | 状态变更是否同步推送 WebSocket？ | 是，事务提交后异步推送 | team-lead |

---

## 10. 后续工作

1. ✅ 状态机设计（本文档）
2. ⏳ 进度计算引擎详细算法（独立文档）
3. ⏳ WebSocket 集成（依赖 Sprint 2）
4. ⏳ Alembic 迁移脚本编写
5. ⏳ 实施编码（待 Sprint 1/2 完成）

---

**变更记录**:
- 2026-06-17: v1.0 初版设计（tom）
