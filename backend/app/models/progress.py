"""
ExecutionProgress, ExecutionTransition, ExecutionLog ORM models (Sprint 3).

Maps to the 3 progress tracking tables created by 003_progress_tables.py migration.
Based on docs/design/agent-progress-state-machine.md.
"""

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from app.database.base import Base


class ExecutionProgress(Base):
    """Current state snapshot for an agent execution run."""

    __tablename__ = "execution_progress"

    run_id = Column(String(36), primary_key=True, nullable=False)
    user_id = Column(String(36), nullable=False)
    status = Column(
        String(20),
        nullable=False,
        comment="queued, running, paused, completed, failed, cancelled, timeout",
    )
    current_step = Column(
        String(20),
        nullable=True,
        comment="researcher, planner, coder, reviewer, tester",
    )
    overall_percentage = Column(
        Float(),
        nullable=False,
        server_default="0.0",
        comment="0.0 - 100.0",
    )
    eta_seconds = Column(
        Integer(),
        nullable=True,
        comment="Estimated seconds remaining",
    )
    started_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
    completed_at = Column(DateTime(), nullable=True)
    total_duration_ms = Column(
        Integer(),
        nullable=True,
        comment="Total execution time in milliseconds",
    )
    retry_count = Column(
        Integer(),
        nullable=False,
        server_default="0",
        comment="Number of retries",
    )
    steps_json = Column(
        JSON(),
        nullable=False,
        comment="Array of step states with status, started_at, completed_at, duration_ms, retry_count, error_message",
    )

    def __repr__(self) -> str:
        return f"<ExecutionProgress(run_id='{self.run_id}', status='{self.status}', percentage={self.overall_percentage}%)>"


class ExecutionTransition(Base):
    """Audit trail for status changes during execution."""

    __tablename__ = "execution_transitions"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    run_id = Column(String(36), nullable=False)
    from_status = Column(
        String(20),
        nullable=True,
        comment="Previous status (null for initial)",
    )
    to_status = Column(
        String(20),
        nullable=False,
        comment="New status",
    )
    step = Column(
        String(20),
        nullable=True,
        comment="Step associated with transition",
    )
    timestamp = Column(DateTime(), nullable=False)
    metadata_json = Column(
        JSON(),
        nullable=True,
        comment="Additional context (error_message, retry_count, etc.)",
    )

    def __repr__(self) -> str:
        return f"<ExecutionTransition(id={self.id}, run_id='{self.run_id}', {self.from_status}->{self.to_status})>"


class ExecutionLog(Base):
    """Structured logs for each execution run."""

    __tablename__ = "execution_logs"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    run_id = Column(String(36), nullable=False)
    step = Column(
        String(20),
        nullable=False,
        comment="Step that generated the log",
    )
    level = Column(
        String(10),
        nullable=False,
        comment="debug, info, warning, error",
    )
    message = Column(
        Text(),
        nullable=False,
        comment="Log message content",
    )
    sequence_num = Column(
        Integer(),
        nullable=False,
        comment="Sequential number within run (for ordering)",
    )
    timestamp = Column(DateTime(), nullable=False)
    metadata_json = Column(
        JSON(),
        nullable=True,
        comment="Additional structured data",
    )

    def __repr__(self) -> str:
        return f"<ExecutionLog(id={self.id}, run_id='{self.run_id}', step='{self.step}', level='{self.level}')>"
