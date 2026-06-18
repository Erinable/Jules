"""add progress tracking tables

Revision ID: 003_progress_tables
Revises: 002_user_auth
Create Date: 2026-06-17 10:12:00.000000

Sprint 3: Agent execution progress tracking system.
Based on docs/design/agent-progress-state-machine.md
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_progress_tables"
down_revision: Union[str, None] = "002_user_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create progress tracking tables: execution_progress, execution_transitions, execution_logs."""

    # Table 1: execution_progress (current state snapshot)
    op.create_table(
        "execution_progress",
        sa.Column("run_id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            comment="queued, running, paused, completed, failed, cancelled, timeout",
        ),
        sa.Column(
            "current_step",
            sa.String(20),
            nullable=True,
            comment="researcher, planner, coder, reviewer, tester",
        ),
        sa.Column(
            "overall_percentage",
            sa.Float(),
            nullable=False,
            server_default="0.0",
            comment="0.0 - 100.0",
        ),
        sa.Column(
            "eta_seconds",
            sa.Integer(),
            nullable=True,
            comment="Estimated seconds remaining",
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "total_duration_ms",
            sa.Integer(),
            nullable=True,
            comment="Total execution time in milliseconds",
        ),
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Number of retries",
        ),
        # Steps JSON (5 steps: researcher, planner, coder, reviewer, tester)
        sa.Column(
            "steps_json",
            sa.JSON(),
            nullable=False,
            comment="Array of step states with status, started_at, completed_at, duration_ms, retry_count, error_message",
        ),
    )

    # Indexes for execution_progress
    op.create_index(
        "idx_execution_progress_user_id",
        "execution_progress",
        ["user_id"],
    )
    op.create_index(
        "idx_execution_progress_status",
        "execution_progress",
        ["status"],
    )
    op.create_index(
        "idx_execution_progress_started_at",
        "execution_progress",
        ["started_at"],
    )
    op.create_index(
        "idx_execution_progress_user_status",
        "execution_progress",
        ["user_id", "status"],
    )

    # Table 2: execution_transitions (audit trail for status changes)
    op.create_table(
        "execution_transitions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column(
            "from_status",
            sa.String(20),
            nullable=True,
            comment="Previous status (null for initial)",
        ),
        sa.Column(
            "to_status",
            sa.String(20),
            nullable=False,
            comment="New status",
        ),
        sa.Column(
            "step",
            sa.String(20),
            nullable=True,
            comment="Step associated with transition",
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=True,
            comment="Additional context (error_message, retry_count, etc.)",
        ),
    )

    # Indexes for execution_transitions
    op.create_index(
        "idx_execution_transitions_run_id",
        "execution_transitions",
        ["run_id"],
    )
    op.create_index(
        "idx_execution_transitions_timestamp",
        "execution_transitions",
        ["timestamp"],
    )
    op.create_index(
        "idx_execution_transitions_run_timestamp",
        "execution_transitions",
        ["run_id", "timestamp"],
    )

    # Table 3: execution_logs (structured logs for each run)
    op.create_table(
        "execution_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column(
            "step",
            sa.String(20),
            nullable=False,
            comment="Step that generated the log",
        ),
        sa.Column(
            "level",
            sa.String(10),
            nullable=False,
            comment="debug, info, warning, error",
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
            comment="Log message content",
        ),
        sa.Column(
            "sequence_num",
            sa.Integer(),
            nullable=False,
            comment="Sequential number within run (for ordering)",
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=True,
            comment="Additional structured data",
        ),
    )

    # Indexes for execution_logs
    op.create_index(
        "idx_execution_logs_run_id",
        "execution_logs",
        ["run_id"],
    )
    op.create_index(
        "idx_execution_logs_timestamp",
        "execution_logs",
        ["timestamp"],
    )
    op.create_index(
        "idx_execution_logs_run_sequence",
        "execution_logs",
        ["run_id", "sequence_num"],
    )
    op.create_index(
        "idx_execution_logs_level",
        "execution_logs",
        ["level"],
    )


def downgrade() -> None:
    """Drop progress tracking tables."""

    # Drop tables in reverse order
    op.drop_index("idx_execution_logs_level", table_name="execution_logs")
    op.drop_index("idx_execution_logs_run_sequence", table_name="execution_logs")
    op.drop_index("idx_execution_logs_timestamp", table_name="execution_logs")
    op.drop_index("idx_execution_logs_run_id", table_name="execution_logs")
    op.drop_table("execution_logs")

    op.drop_index("idx_execution_transitions_run_timestamp", table_name="execution_transitions")
    op.drop_index("idx_execution_transitions_timestamp", table_name="execution_transitions")
    op.drop_index("idx_execution_transitions_run_id", table_name="execution_transitions")
    op.drop_table("execution_transitions")

    op.drop_index("idx_execution_progress_user_status", table_name="execution_progress")
    op.drop_index("idx_execution_progress_started_at", table_name="execution_progress")
    op.drop_index("idx_execution_progress_status", table_name="execution_progress")
    op.drop_index("idx_execution_progress_user_id", table_name="execution_progress")
    op.drop_table("execution_progress")
