"""
Integration tests for Task API endpoints
"""

from datetime import datetime

import pytest
from app.main import app
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

client = TestClient(app)


class TestTaskAPI:
    """Test cases for Task API endpoints"""

    @pytest.fixture
    def setup_project(self, db_session: Session) -> Project:
        """Create a test project"""
        user = User(email="task@example.com", name="Task User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="Task Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.commit()
        return project

    def test_create_task(self, db_session: Session, setup_project: Project) -> None:
        """Test creating a new task"""
        response = client.post(
            "/api/v1/tasks/",
            json={
                "project_id": str(setup_project.id),
                "title": "Test Task",
                "description": "Test Description",
                "priority": 5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == 5
        assert data["status"] == "pending"

    def test_get_task(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving task by ID"""
        task = Task(
            project_id=setup_project.id,
            title="Get Task",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.commit()

        response = client.get(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Get Task"

    def test_get_task_not_found(self, db_session: Session, sample_task_id) -> None:
        """Test retrieving non-existent task returns 404"""
        response = client.get(f"/api/v1/tasks/{sample_task_id}")
        assert response.status_code == 404

    def test_list_tasks(self, db_session: Session, setup_project: Project) -> None:
        """Test listing tasks with pagination"""
        for i in range(5):
            task = Task(
                project_id=setup_project.id,
                title=f"Task {i}",
                status="pending",
                priority=i,
                created_at=datetime.now(),
            )
            db_session.add(task)
        db_session.commit()

        response = client.get("/api/v1/tasks/?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_update_task(self, db_session: Session, setup_project: Project) -> None:
        """Test updating task"""
        task = Task(
            project_id=setup_project.id,
            title="Original Title",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.commit()

        response = client.put(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated Title", "priority": 8},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == 8

    def test_update_task_status(self, db_session: Session, setup_project: Project) -> None:
        """Test updating task status"""
        task = Task(
            project_id=setup_project.id,
            title="Status Task",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.commit()

        response = client.put(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "in_progress"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_delete_task(self, db_session: Session, setup_project: Project) -> None:
        """Test deleting task"""
        task = Task(
            project_id=setup_project.id,
            title="Delete Task",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.commit()

        response = client.delete(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 204
