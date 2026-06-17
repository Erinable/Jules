"""
Pytest configuration and fixtures
"""
import uuid
from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.dependencies.database import get_db
from app.main import app


@pytest.fixture(scope="function")
def engine():
    """Create a fresh in-memory SQLite engine for each test.

    A new database per test guarantees full isolation even though the
    repository methods call commit() internally.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Override the FastAPI dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close here, the outer fixture handles it

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_project_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("87654321-4321-8765-4321-876543218765")


@pytest.fixture
def sample_task_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def sample_file_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("22222222-3333-4444-5555-666666666666")


@pytest.fixture
def sample_code_file_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("66666666-7777-8888-9999-000000000000")


@pytest.fixture
def sample_agent_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("33333333-4444-5555-6666-777777777777")


@pytest.fixture
def sample_execution_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("44444444-5555-6666-7777-888888888888")


@pytest.fixture
def sample_quality_metric_id() -> uuid.UUID:
    """Return a fixed UUID for testing"""
    return uuid.UUID("55555555-6666-7777-8888-999999999999")


@pytest.fixture
def now() -> datetime:
    """Return a fixed datetime for testing"""
    return datetime(2026, 6, 16, 12, 0, 0)


@pytest.fixture
def unique_email() -> str:
    """Generate a unique email for each test"""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_agent_name() -> str:
    """Generate a unique agent name for each test"""
    return f"agent-{uuid.uuid4().hex[:8]}"

