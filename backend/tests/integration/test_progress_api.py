"""
Integration tests for Progress API endpoints (Sprint 3).

Tests all 10 REST API endpoints:
- GET /progress/{run_id}
- GET /progress/{run_id}/logs
- GET /progress/{run_id}/transitions
- GET /progress/user/{user_id}
- POST /progress/{run_id}/start
- POST /progress/{run_id}/pause
- POST /progress/{run_id}/resume
- POST /progress/{run_id}/cancel
- POST /progress/{run_id}/retry
- DELETE /progress/{run_id}
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.progress import ExecutionProgress
from app.repositories.progress_repository import ProgressRepository


@pytest.fixture
def progress_repo(db: Session) -> ProgressRepository:
    """Provide ProgressRepository instance."""
    return ProgressRepository(db)


@pytest.fixture
def sample_run_id() -> str:
    """Generate unique run_id for tests."""
    return str(uuid.uuid4())


@pytest.fixture
def test_user_id(registered_user) -> str:
    """Reusable test user ID from registered_user."""
    return str(registered_user.id)


@pytest.fixture
def sample_progress(
    progress_repo: ProgressRepository, sample_run_id: str, test_user_id: str
) -> ExecutionProgress:
    """Create a sample progress record."""
    steps_json = [
        {
            "name": "researcher",
            "status": "completed",
            "started_at": "2026-06-17T10:00:00Z",
            "completed_at": "2026-06-17T10:00:30Z",
            "duration_ms": 30000,
            "retry_count": 0,
            "error_message": None,
            "metadata": {},
        },
        {
            "name": "planner",
            "status": "running",
            "started_at": "2026-06-17T10:00:30Z",
            "completed_at": None,
            "duration_ms": None,
            "retry_count": 0,
            "error_message": None,
            "metadata": {},
        },
        {
            "name": "coder",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "duration_ms": None,
            "retry_count": 0,
            "error_message": None,
            "metadata": {},
        },
        {
            "name": "reviewer",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "duration_ms": None,
            "retry_count": 0,
            "error_message": None,
            "metadata": {},
        },
        {
            "name": "tester",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "duration_ms": None,
            "retry_count": 0,
            "error_message": None,
            "metadata": {},
        },
    ]

    return progress_repo.create_progress(
        run_id=sample_run_id,
        user_id=test_user_id,
        status="running",
        current_step="planner",
        overall_percentage=25.0,
        eta_seconds=180,
        steps_json=steps_json,
    )


class TestGetProgress:
    """GET /api/v1/progress/{run_id}"""

    def test_get_progress_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test retrieving progress snapshot."""
        response = client.get(f"/api/v1/progress/{sample_run_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == sample_run_id
        assert data["status"] == "running"
        assert data["current_step"] == "planner"
        assert data["overall_percentage"] == 25.0
        assert data["eta_seconds"] == 180
        assert len(data["steps"]) == 5
        assert data["steps"][0]["name"] == "researcher"
        assert data["steps"][0]["status"] == "completed"

    def test_get_progress_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 when progress not found."""
        fake_run_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/progress/{fake_run_id}", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_progress_unauthorized(
        self, client: TestClient, sample_progress: ExecutionProgress, sample_run_id: str
    ):
        """Test 401 when not authenticated."""
        response = client.get(f"/api/v1/progress/{sample_run_id}")

        assert response.status_code == 401


class TestGetLogs:
    """GET /api/v1/progress/{run_id}/logs"""

    def test_get_logs_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test retrieving logs with pagination."""
        # Add some logs
        progress_repo.add_log(sample_run_id, "researcher", "info", "Starting research")
        progress_repo.add_log(sample_run_id, "researcher", "info", "Research completed")
        progress_repo.add_log(sample_run_id, "planner", "info", "Generating plan")

        response = client.get(f"/api/v1/progress/{sample_run_id}/logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["items"][0]["step"] == "researcher"
        assert data["items"][0]["level"] == "info"
        assert data["items"][0]["message"] == "Starting research"

    def test_get_logs_with_filter(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test log filtering by step and level."""
        progress_repo.add_log(sample_run_id, "researcher", "info", "Log 1")
        progress_repo.add_log(sample_run_id, "researcher", "error", "Log 2")
        progress_repo.add_log(sample_run_id, "planner", "info", "Log 3")

        response = client.get(
            f"/api/v1/progress/{sample_run_id}/logs?step=researcher&level=error",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["message"] == "Log 2"

    def test_get_logs_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test log pagination."""
        for i in range(55):
            progress_repo.add_log(sample_run_id, "coder", "info", f"Log {i}")

        response = client.get(
            f"/api/v1/progress/{sample_run_id}/logs?page=1&limit=50", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 55
        assert len(data["items"]) == 50
        assert data["has_next"] is True


class TestGetTransitions:
    """GET /api/v1/progress/{run_id}/transitions"""

    def test_get_transitions_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test retrieving state transitions."""
        # Add transitions
        progress_repo.add_transition(sample_run_id, from_status="queued", to_status="running")
        progress_repo.add_transition(
            sample_run_id, from_status="running", to_status="paused", step="planner"
        )

        response = client.get(f"/api/v1/progress/{sample_run_id}/transitions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["items"][0]["from_status"] == "queued"
        assert data["items"][0]["to_status"] == "running"
        assert data["items"][1]["step"] == "planner"


class TestListUserProgress:
    """GET /api/v1/progress/user/{user_id}"""

    def test_list_user_progress_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test listing user's progress records."""
        # Create multiple progress records
        for i in range(3):
            run_id = str(uuid.uuid4())
            progress_repo.create_progress(
                run_id=run_id,
                user_id=test_user_id,
                status="running" if i < 2 else "completed",
                steps_json=[],
            )

        response = client.get(f"/api/v1/progress/user/{test_user_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_user_progress_with_filter(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_id: str,
        progress_repo: ProgressRepository,
    ):
        """Test filtering by status."""
        progress_repo.create_progress(
            run_id=str(uuid.uuid4()), user_id=test_user_id, status="running", steps_json=[]
        )
        progress_repo.create_progress(
            run_id=str(uuid.uuid4()), user_id=test_user_id, status="completed", steps_json=[]
        )

        response = client.get(
            f"/api/v1/progress/user/{test_user_id}?status=running", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "running"


class TestStartExecution:
    """POST /api/v1/progress/{run_id}/start"""

    def test_start_execution_success(
        self,
        client: TestClient,
        auth_headers: dict,
        progress_repo: ProgressRepository,
        test_user_id: str,
    ):
        """Test starting a queued execution."""
        run_id = str(uuid.uuid4())
        progress_repo.create_progress(
            run_id=run_id, user_id=test_user_id, status="queued", steps_json=[]
        )

        response = client.post(
            f"/api/v1/progress/{run_id}/start",
            json={"initial_step": None},
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["previous_status"] == "queued"
        assert data["new_status"] == "running"
        assert "started" in data["message"].lower()

    def test_start_execution_invalid_state(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test starting an already running execution (409 conflict)."""
        response = client.post(
            f"/api/v1/progress/{sample_run_id}/start", json={}, headers=auth_headers
        )

        assert response.status_code == 409
        assert "cannot start" in response.json()["detail"].lower()


class TestPauseExecution:
    """POST /api/v1/progress/{run_id}/pause"""

    def test_pause_execution_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test pausing a running execution."""
        response = client.post(
            f"/api/v1/progress/{sample_run_id}/pause",
            json={"duration_seconds": 300},
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["previous_status"] == "running"
        assert data["new_status"] == "paused"
        assert "paused" in data["message"].lower()


class TestResumeExecution:
    """POST /api/v1/progress/{run_id}/resume"""

    def test_resume_execution_success(
        self,
        client: TestClient,
        auth_headers: dict,
        progress_repo: ProgressRepository,
        test_user_id: str,
    ):
        """Test resuming a paused execution."""
        run_id = str(uuid.uuid4())
        progress_repo.create_progress(
            run_id=run_id, user_id=test_user_id, status="paused", steps_json=[]
        )

        response = client.post(f"/api/v1/progress/{run_id}/resume", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["previous_status"] == "paused"
        assert data["new_status"] == "running"
        assert "resumed" in data["message"].lower()


class TestCancelExecution:
    """POST /api/v1/progress/{run_id}/cancel"""

    def test_cancel_execution_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test cancelling a running execution."""
        response = client.post(
            f"/api/v1/progress/{sample_run_id}/cancel",
            json={"reason": "user_requested", "force": False},
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["previous_status"] == "running"
        assert data["new_status"] == "cancelled"
        assert "cancelled" in data["message"].lower()

    def test_cancel_terminal_state(
        self,
        client: TestClient,
        auth_headers: dict,
        progress_repo: ProgressRepository,
        test_user_id: str,
    ):
        """Test cancelling a completed execution (409 conflict)."""
        run_id = str(uuid.uuid4())
        progress_repo.create_progress(
            run_id=run_id, user_id=test_user_id, status="completed", steps_json=[]
        )

        response = client.post(f"/api/v1/progress/{run_id}/cancel", json={}, headers=auth_headers)

        assert response.status_code == 409
        assert "terminal" in response.json()["detail"].lower()


class TestRetryExecution:
    """POST /api/v1/progress/{run_id}/retry"""

    def test_retry_execution_success(
        self,
        client: TestClient,
        auth_headers: dict,
        progress_repo: ProgressRepository,
        test_user_id: str,
    ):
        """Test retrying a failed execution."""
        run_id = str(uuid.uuid4())
        progress_repo.create_progress(
            run_id=run_id, user_id=test_user_id, status="failed", steps_json=[]
        )

        response = client.post(
            f"/api/v1/progress/{run_id}/retry",
            json={"from_step": None, "reset_all": False},
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["previous_status"] == "failed"
        assert data["new_status"] == "running"
        assert "retry" in data["message"].lower()

    def test_retry_non_failed(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test retrying a running execution (409 conflict)."""
        response = client.post(
            f"/api/v1/progress/{sample_run_id}/retry", json={}, headers=auth_headers
        )

        assert response.status_code == 409
        assert "failed" in response.json()["detail"].lower()


class TestDeleteProgress:
    """DELETE /api/v1/progress/{run_id}"""

    def test_delete_progress_success_admin(
        self,
        client: TestClient,
        admin_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test deleting progress (admin only)."""
        response = client.delete(f"/api/v1/progress/{sample_run_id}", headers=admin_headers)

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/progress/{sample_run_id}", headers=admin_headers)
        assert get_response.status_code == 404

    def test_delete_progress_forbidden_non_admin(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_progress: ExecutionProgress,
        sample_run_id: str,
    ):
        """Test deleting progress as non-admin (403 forbidden)."""
        response = client.delete(f"/api/v1/progress/{sample_run_id}", headers=auth_headers)

        assert response.status_code == 403
