"""
Integration tests for Agent Execution API endpoints
"""

from datetime import datetime

import pytest
from app.main import app
from app.models.agent import Agent
from app.models.agent_execution import AgentExecution
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

client = TestClient(app)


class TestAgentExecutionAPI:
    """Test cases for Agent Execution API endpoints"""

    @pytest.fixture
    def setup_execution_deps(self, db_session: Session) -> dict:
        """Create test dependencies for executions"""
        user = User(email="exec@example.com", name="Exec User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="Execution Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.flush()

        task = Task(
            project_id=project.id,
            title="Execution Task",
            status="pending",
            priority=1,
            created_at=datetime.now(),
        )
        db_session.add(task)
        db_session.flush()

        agent = Agent(
            name="exec-agent",
            description="Execution Agent",
            config={},
            is_active="true",
            created_at=datetime.now(),
        )
        db_session.add(agent)
        db_session.commit()

        return {
            "task_id": task.id,
            "agent_id": agent.id,
        }

    def test_create_execution(self, db_session: Session, setup_execution_deps: dict) -> None:
        """Test creating a new agent execution"""
        response = client.post(
            "/api/v1/executions/",
            json={
                "task_id": str(setup_execution_deps["task_id"]),
                "agent_type": "test_agent",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "running"
        assert data["task_id"] == str(setup_execution_deps["task_id"])
        assert data["agent_type"] == "test_agent"

    def test_create_execution_with_state(
        self, db_session: Session, setup_execution_deps: dict
    ) -> None:
        """Test creating execution with state data"""
        response = client.post(
            "/api/v1/executions/",
            json={
                "task_id": str(setup_execution_deps["task_id"]),
                "agent_type": "test_agent",
                "state": {"step": "initialization", "progress": 0},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["state"] == {"step": "initialization", "progress": 0}

    def test_get_execution(self, db_session: Session, setup_execution_deps: dict) -> None:
        """Test retrieving execution by ID"""
        execution = AgentExecution(
            task_id=setup_execution_deps["task_id"],
            agent_type="test_agent",
            state={},
            status="running",
            started_at=datetime.now(),
        )
        db_session.add(execution)
        db_session.commit()

        response = client.get(f"/api/v1/executions/{execution.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(execution.id)
        assert data["status"] == "running"

    def test_get_execution_not_found(self, db_session: Session, sample_execution_id) -> None:
        """Test retrieving non-existent execution returns 404"""
        response = client.get(f"/api/v1/executions/{sample_execution_id}")
        assert response.status_code == 404

    def test_list_executions(self, db_session: Session, setup_execution_deps: dict) -> None:
        """Test listing executions with pagination"""
        for i in range(5):
            execution = AgentExecution(
                task_id=setup_execution_deps["task_id"],
                agent_type="test_agent",
                status="running",
                started_at=datetime.now(),
            )
            db_session.add(execution)
        db_session.commit()

        response = client.get("/api/v1/executions/?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_update_execution_status(self, db_session: Session, setup_execution_deps: dict) -> None:
        """Test updating execution status"""
        execution = AgentExecution(
            task_id=setup_execution_deps["task_id"],
            agent_type="test_agent",
            state={},
            status="running",
            started_at=datetime.now(),
        )
        db_session.add(execution)
        db_session.commit()

        response = client.put(
            f"/api/v1/executions/{execution.id}/status",
            json={"status": "completed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_update_execution_status_invalid(
        self, db_session: Session, setup_execution_deps: dict
    ) -> None:
        """Test updating execution with invalid status"""
        execution = AgentExecution(
            task_id=setup_execution_deps["task_id"],
            agent_type="test_agent",
            state={},
            status="running",
            started_at=datetime.now(),
        )
        db_session.add(execution)
        db_session.commit()

        response = client.put(
            f"/api/v1/executions/{execution.id}/status",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 422

    def test_delete_execution(self, db_session: Session, setup_execution_deps: dict) -> None:
        """Test deleting execution"""
        execution = AgentExecution(
            task_id=setup_execution_deps["task_id"],
            agent_type="test_agent",
            state={},
            status="running",
            started_at=datetime.now(),
        )
        db_session.add(execution)
        db_session.commit()

        response = client.delete(f"/api/v1/executions/{execution.id}")
        assert response.status_code == 204

    def test_delete_execution_not_found(self, db_session: Session, sample_execution_id) -> None:
        """Test deleting non-existent execution returns 404"""
        response = client.delete(f"/api/v1/executions/{sample_execution_id}")
        assert response.status_code == 404
