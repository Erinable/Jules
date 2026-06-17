"""
Integration tests for Agent API endpoints
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.agent import Agent

client = TestClient(app)


class TestAgentAPI:
    """Test cases for Agent API endpoints"""

    def test_create_agent(self, db_session: Session) -> None:
        """Test creating a new agent"""
        response = client.post(
            "/api/v1/agents/",
            json={
                "name": "test-agent",
                "description": "Test Agent",
                "config": {"model": "gpt-4"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-agent"
        assert data["config"]["model"] == "gpt-4"

    def test_create_agent_duplicate_name(self, db_session: Session) -> None:
        """Test creating agent with duplicate name fails"""
        agent = Agent(name="duplicate-agent", description="Agent 1", config={}, is_active="true", created_at=datetime.now())
        db_session.add(agent)
        db_session.commit()

        response = client.post(
            "/api/v1/agents/",
            json={
                "name": "duplicate-agent",
                "description": "Agent 2",
                "config": {},
            },
        )
        assert response.status_code == 400

    def test_get_agent(self, db_session: Session) -> None:
        """Test retrieving agent by ID"""
        agent = Agent(name="get-agent", description="Get Agent", config={}, is_active="true", created_at=datetime.now())
        db_session.add(agent)
        db_session.commit()

        response = client.get(f"/api/v1/agents/{agent.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get-agent"

    def test_list_agents(self, db_session: Session) -> None:
        """Test listing agents"""
        for i in range(3):
            agent = Agent(name=f"agent-{i}", description=f"Agent {i}", config={}, is_active="true", created_at=datetime.now())
            db_session.add(agent)
        db_session.commit()

        response = client.get("/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_list_active_agents(self, db_session: Session) -> None:
        """Test listing active agents"""
        agent = Agent(name="active-agent", description="Active", config={}, is_active="true", created_at=datetime.now())
        db_session.add(agent)
        db_session.commit()

        response = client.get("/api/v1/agents/active/list")
        assert response.status_code == 200
        data = response.json()
        assert all(a["is_active"] == "true" for a in data)

    def test_update_agent(self, db_session: Session) -> None:
        """Test updating agent"""
        agent = Agent(name="update-agent", description="Original", config={}, is_active="true", created_at=datetime.now())
        db_session.add(agent)
        db_session.commit()

        response = client.put(
            f"/api/v1/agents/{agent.id}",
            json={"description": "Updated", "config": {"model": "gpt-4"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"

    def test_delete_agent(self, db_session: Session) -> None:
        """Test deleting agent"""
        agent = Agent(name="delete-agent", description="Delete", config={}, is_active="true", created_at=datetime.now())
        db_session.add(agent)
        db_session.commit()

        response = client.delete(f"/api/v1/agents/{agent.id}")
        assert response.status_code == 204
