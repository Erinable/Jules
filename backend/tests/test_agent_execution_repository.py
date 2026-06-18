"""
Tests for AgentExecutionRepository
"""

import uuid
from datetime import datetime

import pytest
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.agent_execution_repository import AgentExecutionRepository
from sqlalchemy.orm import Session


class TestAgentExecutionRepository:
    """Test cases for AgentExecutionRepository"""

    @pytest.fixture
    def setup_task(self, db_session: Session) -> Task:
        """Create a test task"""
        user = User(email="test@example.com", name="Test User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="Test Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.flush()

        task = Task(
            project_id=project.id,
            title="Test Task",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.flush()
        return task

    def test_create_execution(self, db_session: Session, setup_task: Task, now: datetime) -> None:
        """Test creating a new agent execution"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
            state={"step": 1},
        )

        assert execution.id is not None
        assert execution.task_id == setup_task.id
        assert execution.agent_type == "code_generator"
        assert execution.state == {"step": 1}
        assert execution.status == "running"
        assert execution.started_at is not None

    def test_get_by_id(self, db_session: Session, setup_task: Task, now: datetime) -> None:
        """Test retrieving execution by ID"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
        )

        retrieved = repo.get_by_id(execution.id)
        assert retrieved is not None
        assert retrieved.id == execution.id
        assert retrieved.agent_type == execution.agent_type

    def test_get_by_id_not_found(self, db_session: Session, sample_execution_id: uuid.UUID) -> None:
        """Test retrieving non-existent execution returns None"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.get_by_id(sample_execution_id)
        assert execution is None

    def test_get_by_task(self, db_session: Session, setup_task: Task, now: datetime) -> None:
        """Test retrieving executions by task"""
        repo = AgentExecutionRepository(db_session)
        repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
        )
        repo.create(
            task_id=setup_task.id,
            agent_type="test_runner",
        )

        executions = repo.get_by_task(setup_task.id)
        assert len(executions) == 2
        assert all(exec.task_id == setup_task.id for exec in executions)

    def test_update_status(self, db_session: Session, setup_task: Task, now: datetime) -> None:
        """Test updating execution status"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
        )

        result = repo.update_status(execution.id, status="completed")
        assert result is True

        updated_execution = repo.get_by_id(execution.id)
        assert updated_execution is not None
        assert updated_execution.status == "completed"
        assert updated_execution.completed_at is not None

    def test_update_status_with_state(
        self, db_session: Session, setup_task: Task, now: datetime
    ) -> None:
        """Test updating execution status with state"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
            state={"step": 1},
        )

        result = repo.update_status(
            execution.id, status="completed", state={"step": 2, "result": "success"}
        )
        assert result is True

        updated_execution = repo.get_by_id(execution.id)
        assert updated_execution is not None
        assert updated_execution.status == "completed"
        assert updated_execution.state == {"step": 2, "result": "success"}

    def test_update_status_not_found(
        self, db_session: Session, sample_execution_id: uuid.UUID
    ) -> None:
        """Test updating non-existent execution returns False"""
        repo = AgentExecutionRepository(db_session)
        result = repo.update_status(sample_execution_id, status="completed")
        assert result is False

    def test_delete(self, db_session: Session, setup_task: Task, now: datetime) -> None:
        """Test deleting execution"""
        repo = AgentExecutionRepository(db_session)
        execution = repo.create(
            task_id=setup_task.id,
            agent_type="code_generator",
        )

        result = repo.delete(execution.id)
        assert result is True

        deleted_execution = repo.get_by_id(execution.id)
        assert deleted_execution is None

    def test_delete_not_found(self, db_session: Session, sample_execution_id: uuid.UUID) -> None:
        """Test deleting non-existent execution returns False"""
        repo = AgentExecutionRepository(db_session)
        result = repo.delete(sample_execution_id)
        assert result is False
