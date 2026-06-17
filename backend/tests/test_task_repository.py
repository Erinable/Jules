"""
Tests for TaskRepository
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.task_repository import TaskRepository


class TestTaskRepository:
    """Test cases for TaskRepository"""

    @pytest.fixture
    def setup_project(self, db_session: Session) -> Project:
        """Create a test project"""
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
        return project

    def test_create_task(self, db_session: Session, setup_project: Project) -> None:
        """Test creating a new task"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Test Task",
            description="Test Description",
            priority=1,
        )

        assert task.id is not None
        assert task.project_id == setup_project.id
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.priority == 1

    def test_get_by_id(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving task by ID"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Test Task",
            description="Test Description",
            priority=1,
        )

        retrieved = repo.get_by_id(task.id)
        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == task.title

    def test_get_by_id_not_found(self, db_session: Session, sample_task_id: uuid.UUID) -> None:
        """Test retrieving non-existent task returns None"""
        repo = TaskRepository(db_session)
        task = repo.get_by_id(sample_task_id)
        assert task is None

    def test_get_by_project(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving tasks by project"""
        repo = TaskRepository(db_session)
        repo.create(
            project_id=setup_project.id,
            title="Task 1",
            description="Description 1",
            priority=1,
        )
        repo.create(
            project_id=setup_project.id,
            title="Task 2",
            description="Description 2",
            priority=2,
        )

        tasks = repo.get_by_project(setup_project.id)
        assert len(tasks) == 2
        assert all(task.project_id == setup_project.id for task in tasks)

    def test_get_by_status(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving tasks by status"""
        repo = TaskRepository(db_session)
        task1 = repo.create(
            project_id=setup_project.id,
            title="Task 1",
            description="Description 1",
            priority=1,
        )
        task2 = repo.create(
            project_id=setup_project.id,
            title="Task 2",
            description="Description 2",
            priority=2,
        )
        # Update second task to completed
        repo.update_status(task2.id, status="completed")

        pending_tasks = repo.get_by_status(setup_project.id, "pending")
        assert len(pending_tasks) >= 1
        assert any(task.id == task1.id for task in pending_tasks)

    def test_update_status(self, db_session: Session, setup_project: Project) -> None:
        """Test updating task status"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Test Task",
            description="Test Description",
            priority=1,
        )

        result = repo.update_status(task.id, status="in_progress")
        assert result is True

        updated_task = repo.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.status == "in_progress"

    def test_update_status_not_found(self, db_session: Session, sample_task_id: uuid.UUID) -> None:
        """Test updating non-existent task returns False"""
        repo = TaskRepository(db_session)
        result = repo.update_status(sample_task_id, status="completed")
        assert result is False

    def test_update(self, db_session: Session, setup_project: Project) -> None:
        """Test updating task fields"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Original Title",
            description="Original Description",
            priority=1,
        )

        result = repo.update(
            task.id,
            title="Updated Title",
            description="Updated Description",
            priority=3,
        )
        assert result is True

        updated_task = repo.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == 3

    def test_update_partial(self, db_session: Session, setup_project: Project) -> None:
        """Test updating only some task fields"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Original Title",
            description="Original Description",
            priority=1,
        )

        result = repo.update(task.id, title="Updated Title")
        assert result is True

        updated_task = repo.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"

    def test_delete(self, db_session: Session, setup_project: Project) -> None:
        """Test deleting task"""
        repo = TaskRepository(db_session)
        task = repo.create(
            project_id=setup_project.id,
            title="Test Task",
            description="Test Description",
            priority=1,
        )

        result = repo.delete(task.id)
        assert result is True

        deleted_task = repo.get_by_id(task.id)
        assert deleted_task is None

    def test_delete_not_found(self, db_session: Session, sample_task_id: uuid.UUID) -> None:
        """Test deleting non-existent task returns False"""
        repo = TaskRepository(db_session)
        result = repo.delete(sample_task_id)
        assert result is False
