"""
Integration tests for Health Check API endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthAPI:
    """Test cases for Health Check API endpoints"""

    def test_health_check(self) -> None:
        """Test basic health check endpoint"""
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "jules-backend"
        assert data["version"] == "0.1.0"

    def test_readiness_check(self) -> None:
        """Test readiness check endpoint"""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["service"] == "jules-backend"

    def test_liveness_check(self) -> None:
        """Test liveness check endpoint"""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert data["service"] == "jules-backend"
