"""
Tests for AgentRepository
"""
import uuid

from sqlalchemy.orm import Session

from app.repositories.agent_repository import AgentRepository


class TestAgentRepository:
    """Test cases for AgentRepository"""

    def test_create_agent(self, db_session: Session, unique_agent_name: str) -> None:
        """Test creating a new agent"""
        repo = AgentRepository(db_session)
        agent = repo.create(
            name=unique_agent_name,
            description="Test Agent Description",
            config={"key": "value"},
        )

        assert agent.id is not None
        assert agent.name == unique_agent_name
        assert agent.description == "Test Agent Description"
        assert agent.config == {"key": "value"}
        assert agent.is_active == "true"

    def test_get_by_id(self, db_session: Session, unique_agent_name: str) -> None:
        """Test retrieving agent by ID"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Test", config={})

        retrieved = repo.get_by_id(agent.id)
        assert retrieved is not None
        assert retrieved.id == agent.id
        assert retrieved.name == agent.name

    def test_get_by_id_not_found(self, db_session: Session, sample_agent_id: uuid.UUID) -> None:
        """Test retrieving non-existent agent returns None"""
        repo = AgentRepository(db_session)
        agent = repo.get_by_id(sample_agent_id)
        assert agent is None

    def test_get_by_name(self, db_session: Session, unique_agent_name: str) -> None:
        """Test retrieving agent by name"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Test", config={})

        retrieved = repo.get_by_name(unique_agent_name)
        assert retrieved is not None
        assert retrieved.id == agent.id
        assert retrieved.name == unique_agent_name

    def test_get_by_name_not_found(self, db_session: Session) -> None:
        """Test retrieving non-existent agent by name returns None"""
        repo = AgentRepository(db_session)
        agent = repo.get_by_name("nonexistent_agent")
        assert agent is None

    def test_get_all_active(self, db_session: Session) -> None:
        """Test retrieving all active agents"""
        repo = AgentRepository(db_session)
        repo.create(name=f"agent1-{uuid.uuid4().hex[:8]}", description="Agent 1", config={})
        repo.create(name=f"agent2-{uuid.uuid4().hex[:8]}", description="Agent 2", config={})

        active_agents = repo.get_all_active()
        assert len(active_agents) >= 2
        assert all(agent.is_active == "true" for agent in active_agents)

    def test_get_all(self, db_session: Session) -> None:
        """Test retrieving all agents with pagination"""
        repo = AgentRepository(db_session)
        repo.create(name=f"agent1-{uuid.uuid4().hex[:8]}", description="Agent 1", config={})
        repo.create(name=f"agent2-{uuid.uuid4().hex[:8]}", description="Agent 2", config={})
        repo.create(name=f"agent3-{uuid.uuid4().hex[:8]}", description="Agent 3", config={})

        agents = repo.get_all(limit=100, offset=0)
        assert len(agents) >= 3

    def test_update_description(self, db_session: Session, unique_agent_name: str) -> None:
        """Test updating agent description"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Original", config={})

        result = repo.update(agent.id, description="Updated Description")
        assert result is True

        updated_agent = repo.get_by_id(agent.id)
        assert updated_agent is not None
        assert updated_agent.description == "Updated Description"

    def test_update_config(self, db_session: Session, unique_agent_name: str) -> None:
        """Test updating agent config"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Test", config={"old": "config"})

        result = repo.update(agent.id, config={"new": "config"})
        assert result is True

        updated_agent = repo.get_by_id(agent.id)
        assert updated_agent is not None
        assert updated_agent.config == {"new": "config"}

    def test_update_both_fields(self, db_session: Session, unique_agent_name: str) -> None:
        """Test updating both description and config"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Original", config={"old": "config"})

        result = repo.update(agent.id, description="Updated", config={"new": "config"})
        assert result is True

        updated_agent = repo.get_by_id(agent.id)
        assert updated_agent is not None
        assert updated_agent.description == "Updated"
        assert updated_agent.config == {"new": "config"}

    def test_update_no_fields(self, db_session: Session, unique_agent_name: str) -> None:
        """Test update with no fields returns False"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Test", config={})

        result = repo.update(agent.id)
        assert result is False

    def test_update_not_found(self, db_session: Session, sample_agent_id: uuid.UUID) -> None:
        """Test updating non-existent agent returns False"""
        repo = AgentRepository(db_session)
        result = repo.update(sample_agent_id, description="Updated")
        assert result is False

    def test_delete(self, db_session: Session, unique_agent_name: str) -> None:
        """Test deleting agent"""
        repo = AgentRepository(db_session)
        agent = repo.create(name=unique_agent_name, description="Test", config={})

        result = repo.delete(agent.id)
        assert result is True

        deleted_agent = repo.get_by_id(agent.id)
        assert deleted_agent is None

    def test_delete_not_found(self, db_session: Session, sample_agent_id: uuid.UUID) -> None:
        """Test deleting non-existent agent returns False"""
        repo = AgentRepository(db_session)
        result = repo.delete(sample_agent_id)
        assert result is False
