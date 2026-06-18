"""Agent execution progress schemas (Sprint 3).

Defines the state machine data models for agent execution progress tracking.
Based on docs/design/agent-progress-state-machine.md.

All models are immutable (frozen=True) per project coding standards.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AgentStep(str, Enum):
    """The 5 fixed steps in agent execution pipeline."""

    RESEARCHER = "researcher"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"

    @classmethod
    def ordered(cls) -> list["AgentStep"]:
        """Return steps in execution order."""
        return [cls.RESEARCHER, cls.PLANNER, cls.CODER, cls.REVIEWER, cls.TESTER]


class StepStatus(str, Enum):
    """Status of a single execution step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class RunStatus(str, Enum):
    """Status of a complete agent execution run."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Terminal statuses that cannot transition further
TERMINAL_STEP_STATUSES = frozenset(
    {StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED, StepStatus.CANCELLED}
)
TERMINAL_RUN_STATUSES = frozenset(
    {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED, RunStatus.TIMEOUT}
)

# Statuses still consuming time (for ETA calculation)
ACTIVE_STEP_STATUSES = frozenset({StepStatus.PENDING, StepStatus.RUNNING, StepStatus.RETRYING})


class StepState(BaseModel):
    """Immutable snapshot of a single step's state."""

    model_config = ConfigDict(frozen=True)

    name: AgentStep
    status: StepStatus = StepStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    error_message: str | None = None
    metadata: dict = Field(default_factory=dict)


class RunProgress(BaseModel):
    """Immutable snapshot of a complete run's progress."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    user_id: str
    status: RunStatus
    steps: tuple[StepState, ...]
    current_step: AgentStep | None = None
    overall_percentage: float = 0.0
    eta_seconds: int | None = None
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    total_duration_ms: int | None = None
    retry_count: int = 0
