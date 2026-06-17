"""
Tests for QualityMetricRepository
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.quality_metric_repository import QualityMetricRepository


class TestQualityMetricRepository:
    """Test cases for QualityMetricRepository"""

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

    def test_create_metric(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test creating a new quality metric"""
        repo = QualityMetricRepository(db_session)
        metric = repo.create(
            project_id=setup_project.id,
            avg_complexity=5.2,
            maintainability_index=75.5,
            security_issues=2,
            test_coverage=85.0,
            measured_at=now,
        )

        assert metric.id is not None
        assert metric.project_id == setup_project.id
        assert metric.avg_complexity == 5.2
        assert metric.maintainability_index == 75.5
        assert metric.security_issues == 2
        assert metric.test_coverage == 85.0

    def test_get_by_id(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test retrieving metric by ID"""
        repo = QualityMetricRepository(db_session)
        metric = repo.create(
            project_id=setup_project.id,
            avg_complexity=5.2,
            maintainability_index=75.5,
            measured_at=now,
        )

        retrieved = repo.get_by_id(metric.id)
        assert retrieved is not None
        assert retrieved.id == metric.id
        assert retrieved.avg_complexity == metric.avg_complexity

    def test_get_by_id_not_found(self, db_session: Session, sample_project_id: uuid.UUID) -> None:
        """Test retrieving non-existent metric returns None"""
        repo = QualityMetricRepository(db_session)
        metric = repo.get_by_id(sample_project_id)
        assert metric is None

    def test_get_latest(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test retrieving latest metric for project"""
        repo = QualityMetricRepository(db_session)
        repo.create(
            project_id=setup_project.id,
            avg_complexity=5.0,
            measured_at=datetime(2026, 6, 1),
        )
        latest = repo.create(
            project_id=setup_project.id,
            avg_complexity=6.0,
            measured_at=datetime(2026, 6, 15),
        )

        retrieved = repo.get_latest(setup_project.id)
        assert retrieved is not None
        assert retrieved.id == latest.id
        assert retrieved.avg_complexity == 6.0

    def test_get_latest_not_found(self, db_session: Session, sample_project_id: uuid.UUID) -> None:
        """Test retrieving latest metric for non-existent project returns None"""
        repo = QualityMetricRepository(db_session)
        metric = repo.get_latest(sample_project_id)
        assert metric is None

    def test_get_history(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving metric history"""
        repo = QualityMetricRepository(db_session)
        repo.create(
            project_id=setup_project.id,
            avg_complexity=5.0,
            measured_at=datetime(2026, 6, 1),
        )
        repo.create(
            project_id=setup_project.id,
            avg_complexity=5.5,
            measured_at=datetime(2026, 6, 10),
        )
        repo.create(
            project_id=setup_project.id,
            avg_complexity=6.0,
            measured_at=datetime(2026, 6, 15),
        )

        history = repo.get_history(setup_project.id)
        assert len(history) == 3
        assert history[0].avg_complexity == 6.0
        assert history[1].avg_complexity == 5.5
        assert history[2].avg_complexity == 5.0

    def test_get_history_with_limit(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving metric history with limit"""
        repo = QualityMetricRepository(db_session)
        repo.create(
            project_id=setup_project.id,
            avg_complexity=5.0,
            measured_at=datetime(2026, 6, 1),
        )
        repo.create(
            project_id=setup_project.id,
            avg_complexity=5.5,
            measured_at=datetime(2026, 6, 10),
        )
        repo.create(
            project_id=setup_project.id,
            avg_complexity=6.0,
            measured_at=datetime(2026, 6, 15),
        )

        history = repo.get_history(setup_project.id, limit=2)
        assert len(history) == 2
        assert history[0].avg_complexity == 6.0
        assert history[1].avg_complexity == 5.5

    def test_delete(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test deleting metric"""
        repo = QualityMetricRepository(db_session)
        metric = repo.create(
            project_id=setup_project.id,
            avg_complexity=5.0,
            measured_at=now,
        )

        result = repo.delete(metric.id)
        assert result is True

        deleted_metric = repo.get_by_id(metric.id)
        assert deleted_metric is None

    def test_delete_not_found(self, db_session: Session, sample_project_id: uuid.UUID) -> None:
        """Test deleting non-existent metric returns False"""
        repo = QualityMetricRepository(db_session)
        result = repo.delete(sample_project_id)
        assert result is False
