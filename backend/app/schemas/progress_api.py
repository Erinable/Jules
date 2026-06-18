"""
Progress API Schemas (Sprint 3).

Pydantic models for progress tracking REST API endpoints.
Based on docs/design/progress-tracking-api.md.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_progress import AgentStep, RunStatus, StepState

# ── Request Schemas ──────────────────────────────────────────────────────


class CancelRequest(BaseModel):
    """Request body for cancelling an execution."""

    reason: str = Field(default="user_requested", max_length=255)
    force: bool = Field(
        default=False,
        description="If true, terminate immediately; if false, graceful shutdown",
    )


class PauseRequest(BaseModel):
    """Request body for pausing an execution."""

    duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=3600,
        description="Auto-resume after N seconds (max 1 hour)",
    )


class StartRequest(BaseModel):
    """Request body for starting an execution."""

    initial_step: AgentStep | None = Field(
        default=None,
        description="Start from specific step (default: researcher)",
    )


class RetryRequest(BaseModel):
    """Request body for retrying a failed execution."""

    from_step: AgentStep | None = Field(
        default=None,
        description="Retry from specific step (default: failed step)",
    )
    reset_all: bool = Field(
        default=False,
        description="Reset all steps and start from beginning",
    )


# ── Response Schemas ─────────────────────────────────────────────────────


class ProgressResponse(BaseModel):
    """Full progress snapshot response."""

    model_config = ConfigDict(from_attributes=True)

    run_id: str
    user_id: str
    status: RunStatus
    current_step: AgentStep | None = None
    overall_percentage: float = Field(ge=0.0, le=100.0)
    eta_seconds: int | None = None
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    steps: list[StepState]
    total_duration_ms: int | None = None
    retry_count: int = Field(ge=0)


class ProgressSummary(BaseModel):
    """Lightweight progress summary (for list endpoints)."""

    model_config = ConfigDict(from_attributes=True)

    run_id: str
    user_id: str
    status: RunStatus
    current_step: AgentStep | None = None
    overall_percentage: float
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TransitionResponse(BaseModel):
    """State transition record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: str
    from_status: str | None = None
    to_status: str
    step: AgentStep | None = None
    timestamp: datetime
    metadata: dict = Field(default_factory=dict)


class LogEntryResponse(BaseModel):
    """Single log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: str
    step: AgentStep
    level: str
    message: str
    sequence_num: int
    timestamp: datetime
    metadata: dict = Field(default_factory=dict)


class ControlResponse(BaseModel):
    """Response for control operations (cancel/pause/resume/start)."""

    run_id: str
    previous_status: RunStatus
    new_status: RunStatus
    message: str
    affected_step: AgentStep | None = None


class PaginatedProgressResponse(BaseModel):
    """Paginated list of progress records."""

    items: list[ProgressSummary]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    has_next: bool


class PaginatedLogsResponse(BaseModel):
    """Paginated list of log entries."""

    items: list[LogEntryResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=200)
    has_next: bool


class TransitionsResponse(BaseModel):
    """List of transitions (non-paginated, typically small)."""

    items: list[TransitionResponse]
    total: int = Field(ge=0)


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: dict
    meta: dict = Field(default_factory=dict)
