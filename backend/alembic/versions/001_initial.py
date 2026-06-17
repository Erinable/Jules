"""initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-06-16 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables and indexes"""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_users_email", "users", ["email"], unique=False)

    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_projects_user_id", "projects", ["user_id"], unique=False)
    op.create_index("idx_projects_status", "projects", ["status"], unique=False)
    op.create_index("idx_projects_created_at", "projects", ["created_at"], unique=False)

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tasks_project_id", "tasks", ["project_id"], unique=False)
    op.create_index("idx_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("idx_tasks_priority", "tasks", ["priority"], unique=False)
    op.create_index("idx_tasks_created_at", "tasks", ["created_at"], unique=False)

    # Create code_files table
    op.create_table(
        "code_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("hash", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_code_files_project_id", "code_files", ["project_id"], unique=False)
    op.create_index("idx_code_files_hash", "code_files", ["hash"], unique=False)
    op.create_index("idx_code_files_project_path", "code_files", ["project_id", "path"], unique=True)

    # Create quality_metrics table
    op.create_table(
        "quality_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("avg_complexity", sa.Float(), nullable=True),
        sa.Column("maintainability_index", sa.Float(), nullable=True),
        sa.Column("security_issues", sa.Integer(), nullable=True),
        sa.Column("test_coverage", sa.Float(), nullable=True),
        sa.Column("measured_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_quality_metrics_project_id", "quality_metrics", ["project_id"], unique=False)
    op.create_index("idx_quality_metrics_measured_at", "quality_metrics", ["measured_at"], unique=False)

    # Create agents table
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("idx_agents_name", "agents", ["name"], unique=False)
    op.create_index("idx_agents_is_active", "agents", ["is_active"], unique=False)

    # Create agent_executions table
    op.create_table(
        "agent_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_type", sa.String(length=50), nullable=False),
        sa.Column("state", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_agent_executions_task_id", "agent_executions", ["task_id"], unique=False)
    op.create_index("idx_agent_executions_status", "agent_executions", ["status"], unique=False)
    op.create_index("idx_agent_executions_started_at", "agent_executions", ["started_at"], unique=False)

    # Create code_versions table
    op.create_table(
        "code_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("commit_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["code_files.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_code_versions_file_id", "code_versions", ["file_id"], unique=False)
    op.create_index("idx_code_versions_file_version", "code_versions", ["file_id", "version_number"], unique=True)
    op.create_index("idx_code_versions_commit_hash", "code_versions", ["commit_hash"], unique=False)

    # Create llm_calls table
    op.create_table(
        "llm_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["agent_executions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_llm_calls_execution_id", "llm_calls", ["execution_id"], unique=False)
    op.create_index("idx_llm_calls_created_at", "llm_calls", ["created_at"], unique=False)


def downgrade() -> None:
    """Drop all tables in reverse order"""
    # Drop tables in reverse order of creation to respect foreign key constraints
    op.drop_index("idx_llm_calls_created_at", table_name="llm_calls")
    op.drop_index("idx_llm_calls_execution_id", table_name="llm_calls")
    op.drop_table("llm_calls")

    op.drop_index("idx_code_versions_commit_hash", table_name="code_versions")
    op.drop_index("idx_code_versions_file_version", table_name="code_versions")
    op.drop_index("idx_code_versions_file_id", table_name="code_versions")
    op.drop_table("code_versions")

    op.drop_index("idx_agent_executions_started_at", table_name="agent_executions")
    op.drop_index("idx_agent_executions_status", table_name="agent_executions")
    op.drop_index("idx_agent_executions_task_id", table_name="agent_executions")
    op.drop_table("agent_executions")

    op.drop_index("idx_agents_is_active", table_name="agents")
    op.drop_index("idx_agents_name", table_name="agents")
    op.drop_table("agents")

    op.drop_index("idx_quality_metrics_measured_at", table_name="quality_metrics")
    op.drop_index("idx_quality_metrics_project_id", table_name="quality_metrics")
    op.drop_table("quality_metrics")

    op.drop_index("idx_code_files_project_path", table_name="code_files")
    op.drop_index("idx_code_files_hash", table_name="code_files")
    op.drop_index("idx_code_files_project_id", table_name="code_files")
    op.drop_table("code_files")

    op.drop_index("idx_tasks_created_at", table_name="tasks")
    op.drop_index("idx_tasks_priority", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_project_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("idx_projects_created_at", table_name="projects")
    op.drop_index("idx_projects_status", table_name="projects")
    op.drop_index("idx_projects_user_id", table_name="projects")
    op.drop_table("projects")

    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
