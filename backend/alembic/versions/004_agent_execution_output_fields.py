"""add agent execution output fields

Revision ID: 004_execution_output
Revises: 003_progress_tables
Create Date: 2026-06-18 11:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_execution_output"
down_revision: str | None = "003_progress_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add execution result fields expected by the AgentExecution model."""
    op.add_column("agent_executions", sa.Column("output", sa.String(length=1000), nullable=True))
    op.add_column(
        "agent_executions", sa.Column("error_message", sa.String(length=1000), nullable=True)
    )


def downgrade() -> None:
    """Remove execution result fields."""
    op.drop_column("agent_executions", "error_message")
    op.drop_column("agent_executions", "output")
