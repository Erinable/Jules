"""
Integration tests for Quality Metric API endpoints
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.project import Project
from app.models.quality_metric import QualityMetric
from app.models.user import User

client = TestClient(app)


class TestQualityMetricAPI:
    """Test cases for Quality Metric API endpoints"""

    @pytest.fixture
    def setup_project(self, db_session: Session) -> Project:
        """Create a test project"""
        user = User(email="quality@example.com", name="Quality User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="Quality Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.commit()
        return project

    def test_create_quality_metric(self, db_session: Session, setup_project: Project) -> None:
        """Test creating a new quality metric"""
        response = client.post(
            "/api/v1/quality/",
            json={
                "project_id": str(setup_project.id),
                "avg_complexity": 5.5,
                "maintainability_index": 75.0,
                "security_issues": 2,
                "test_coverage": 85.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["avg_complexity"] == 5.5
        assert data["maintainability_index"] == 75.0
        assert data["security_issues"] == 2
        assert data["test_coverage"] == 85.0

    def test_create_quality_metric_with_defaults(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test creating quality metric with default values"""
        response = client.post(
            "/api/v1/quality/",
            json={
                "project_id": str(setup_project.id),
                "avg_complexity": 5.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["avg_complexity"] == 5.0
        assert data["maintainability_index"] == 0.0
        assert data["security_issues"] == 0
        assert data["test_coverage"] == 0.0

    def test_create_quality_metric_invalid_complexity(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test creating quality metric with negative complexity fails"""
        response = client.post(
            "/api/v1/quality/",
            json={
                "project_id": str(setup_project.id),
                "avg_complexity": -1.0,
            },
        )
        assert response.status_code == 422

    def test_create_quality_metric_invalid_maintainability(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test creating quality metric with invalid maintainability index fails"""
        response = client.post(
            "/api/v1/quality/",
            json={
                "project_id": str(setup_project.id),
                "avg_complexity": 5.0,
                "maintainability_index": 101.0,
            },
        )
        assert response.status_code == 422

    def test_create_quality_metric_invalid_coverage(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test creating quality metric with invalid coverage fails"""
        response = client.post(
            "/api/v1/quality/",
            json={
                "project_id": str(setup_project.id),
                "avg_complexity": 5.0,
                "test_coverage": 150.0,
            },
        )
        assert response.status_code == 422

    def test_get_quality_metric(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving quality metric by ID"""
        metric = QualityMetric(
            project_id=setup_project.id,
            avg_complexity=5.0,
            maintainability_index=80.0,
            security_issues=1,
            test_coverage=90.0,
            measured_at=datetime.now(),
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(f"/api/v1/quality/{metric.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["avg_complexity"] == 5.0

    def test_get_quality_metric_not_found(
        self, db_session: Session, sample_quality_metric_id
    ) -> None:
        """Test retrieving non-existent quality metric returns 404"""
        response = client.get(f"/api/v1/quality/{sample_quality_metric_id}")
        assert response.status_code == 404

    def test_get_latest_quality_metric(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test retrieving latest quality metric for project"""
        # Create multiple metrics with different timestamps
        metric1 = QualityMetric(
            project_id=setup_project.id,
            avg_complexity=5.0,
            maintainability_index=75.0,
            security_issues=2,
            test_coverage=85.0,
            measured_at=datetime(2024, 1, 1),
        )
        metric2 = QualityMetric(
            project_id=setup_project.id,
            avg_complexity=4.0,
            maintainability_index=80.0,
            security_issues=1,
            test_coverage=90.0,
            measured_at=datetime(2024, 1, 15),
        )
        db_session.add_all([metric1, metric2])
        db_session.commit()

        response = client.get(f"/api/v1/quality/project/{setup_project.id}/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["measured_at"] == "2024-01-15T00:00:00"

    def test_get_latest_quality_metric_not_found(
        self, db_session: Session, sample_project_id
    ) -> None:
        """Test retrieving latest metric for non-existent project returns 404"""
        response = client.get(f"/api/v1/quality/project/{sample_project_id}/latest")
        assert response.status_code == 404

    def test_get_quality_metric_history(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test retrieving quality metric history for project"""
        for i in range(5):
            metric = QualityMetric(
                project_id=setup_project.id,
                avg_complexity=5.0 + i,
                maintainability_index=75.0,
                security_issues=i,
                test_coverage=85.0,
                measured_at=datetime(2024, 1, i + 1),
            )
            db_session.add(metric)
        db_session.commit()

        response = client.get(f"/api/v1/quality/project/{setup_project.id}/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_quality_metric_history_with_pagination(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test retrieving quality metric history with pagination"""
        for i in range(10):
            metric = QualityMetric(
                project_id=setup_project.id,
                avg_complexity=5.0 + i,
                maintainability_index=75.0,
                security_issues=i,
                test_coverage=85.0,
                measured_at=datetime(2024, 1, i + 1),
            )
            db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/api/v1/quality/project/{setup_project.id}/history?limit=3&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_delete_quality_metric(self, db_session: Session, setup_project: Project) -> None:
        """Test deleting quality metric"""
        metric = QualityMetric(
            project_id=setup_project.id,
            measured_at=datetime.now(),
        )
        db_session.add(metric)
        db_session.commit()

        response = client.delete(f"/api/v1/quality/{metric.id}")
        assert response.status_code == 204

    def test_delete_quality_metric_not_found(
        self, db_session: Session, sample_quality_metric_id
    ) -> None:
        """Test deleting non-existent quality metric returns 404"""
        response = client.delete(f"/api/v1/quality/{sample_quality_metric_id}")
        assert response.status_code == 404
