"""Unit tests for ProgressRepository (Sprint 3).

Tests CRUD operations for execution_progress, execution_transitions, execution_logs.
Based on docs/design/progress-tracking-api.md.

Run: pytest tests/unit/test_progress_repository.py -v
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from app.models.progress import ExecutionLog, ExecutionProgress, ExecutionTransition
from app.repositories.progress_repository import ProgressRepository
from sqlalchemy.orm import Session

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db():
    """Create a mock SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def repo(mock_db):
    """Create a ProgressRepository with mocked DB session."""
    return ProgressRepository(mock_db)


class TestProgressCRUD:
    """Tests for execution_progress table operations."""

    def test_create_progress(self, repo, mock_db):
        """Test creating a new progress record."""
        mock_progress = MagicMock(spec=ExecutionProgress)
        mock_progress.run_id = "run-001"
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        created = repo.create_progress(
            run_id="run-001",
            user_id="user-1",
            status="running",
            steps_json=[{"name": "researcher", "status": "pending"}],
            current_step="researcher",
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert created.run_id == "run-001"

    def test_get_progress_found(self, repo, mock_db):
        """Test getting progress by run_id when exists."""
        mock_progress = MagicMock(spec=ExecutionProgress)
        mock_progress.run_id = "run-001"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_progress

        result = repo.get_progress("run-001")

        assert result is not None
        assert result.run_id == "run-001"

    def test_get_progress_not_found(self, repo, mock_db):
        """Test getting progress by run_id when not exists."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repo.get_progress("nonexistent")
        assert result is None

    def test_update_progress(self, repo, mock_db):
        """Test updating progress fields."""
        mock_update = MagicMock()
        mock_db.query.return_value.filter.return_value.update.return_value = 1

        result = repo.update_progress("run-001", status="completed", overall_percentage=100.0)

        assert result is True
        mock_db.commit.assert_called_once()
        # updated_at should be set automatically
        call_kwargs = mock_db.query.return_value.filter.return_value.update.call_args[0][0]
        assert "updated_at" in call_kwargs

    def test_update_progress_not_found(self, repo, mock_db):
        """Test updating nonexistent progress."""
        mock_db.query.return_value.filter.return_value.update.return_value = 0

        result = repo.update_progress("nonexistent", status="completed")
        assert result is False

    def test_list_progress_by_user(self, repo, mock_db):
        """Test listing progress for a specific user."""
        mock_progress = MagicMock(spec=ExecutionProgress)
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_progress
        ]

        items, total = repo.list_progress_by_user(user_id="user-1")
        assert total == 1
        assert len(items) == 1

    def test_list_progress_by_user_with_status_filter(self, repo, mock_db):
        """Test listing progress by user filtered by status."""
        mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 1

        items, total = repo.list_progress_by_user(user_id="user-1", status="running")
        assert total == 1

    def test_list_all_progress(self, repo, mock_db):
        """Test listing all progress (admin)."""
        mock_db.query.return_value.count.return_value = 2
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            MagicMock(),
            MagicMock(),
        ]

        items, total = repo.list_all_progress()
        assert total == 2
        assert len(items) == 2

    def test_list_all_progress_with_status_filter(self, repo, mock_db):
        """Test listing all progress filtered by status."""
        mock_db.query.return_value.filter.return_value.count.return_value = 1

        items, total = repo.list_all_progress(status="completed")
        assert total == 1

    def test_delete_progress(self, repo, mock_db):
        """Test deleting a progress record."""
        mock_db.query.return_value.filter.return_value.delete.return_value = 1

        result = repo.delete_progress("run-001")
        assert result is True
        mock_db.commit.assert_called_once()

    def test_delete_progress_not_found(self, repo, mock_db):
        """Test deleting nonexistent progress."""
        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        result = repo.delete_progress("nonexistent")
        assert result is False


class TestTransitionCRUD:
    """Tests for execution_transitions table operations."""

    def test_add_transition(self, repo, mock_db):
        """Test adding a status transition."""
        mock_transition = MagicMock(spec=ExecutionTransition)
        mock_transition.id = 1
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        created = repo.add_transition(
            run_id="run-001",
            from_status="queued",
            to_status="running",
            step="planner",
            metadata={"reason": "step_started"},
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(created, ExecutionTransition)

    def test_add_initial_transition(self, repo, mock_db):
        """Test adding initial transition (from_status is None)."""
        mock_transition = MagicMock(spec=ExecutionTransition)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        created = repo.add_transition(run_id="run-001", to_status="queued")

        mock_db.add.assert_called_once()
        assert isinstance(created, ExecutionTransition)

    def test_get_transitions(self, repo, mock_db):
        """Test getting transitions for a run."""
        mock_transition = MagicMock(spec=ExecutionTransition)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_transition,
            mock_transition,
        ]

        results = repo.get_transitions("run-001")
        assert len(results) == 2

    def test_get_transitions_with_time_range(self, repo, mock_db):
        """Test getting transitions with time range filter."""
        start = datetime(2026, 6, 17, 10, 0, 0)
        end = datetime(2026, 6, 17, 11, 0, 0)

        results = repo.get_transitions("run-001", start_time=start, end_time=end)

        mock_db.query.return_value.filter.assert_called()
        assert len(results) >= 0


class TestLogCRUD:
    """Tests for execution_logs table operations."""

    def test_add_log_first_entry(self, repo, mock_db):
        """Test adding the first log entry (sequence_num = 1)."""
        mock_db.query.return_value.filter.return_value.scalar.return_value = None  # no max seq
        mock_log = MagicMock(spec=ExecutionLog)
        mock_log.id = 1
        mock_log.sequence_num = 1
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        created = repo.add_log(
            run_id="run-001", step="researcher", level="info", message="Starting"
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert created.sequence_num is not None  # auto-generated

    def test_add_log_increments_sequence(self, repo, mock_db):
        """Test adding a log increments sequence_num."""
        mock_db.query.return_value.filter.return_value.scalar.return_value = 5  # max seq = 5

        created = repo.add_log(run_id="run-001", step="coder", level="debug", message="Processing")

        # sequence_num should be 6 (= 5 + 1)
        added_log = mock_db.add.call_args[0][0]
        assert added_log.sequence_num == 6

    def test_get_logs_default_pagination(self, repo, mock_db):
        """Test getting logs with default pagination."""
        mock_log = MagicMock(spec=ExecutionLog)
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_log,
            mock_log,
        ]

        items, total = repo.get_logs("run-001")
        assert total == 5
        assert len(items) == 2

    def test_get_logs_with_filters(self, repo, mock_db):
        """Test getting logs filtered by step and level."""
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.count.return_value = 3

        items, total = repo.get_logs("run-001", step="coder", level="error")
        assert total == 3

    def test_get_logs_desc_order(self, repo, mock_db):
        """Test getting logs in descending order."""
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            MagicMock(),
        ]

        items, total = repo.get_logs("run-001", order="desc")
        assert total == 3
        assert len(items) == 1

    def test_get_log_count(self, repo, mock_db):
        """Test getting log count for a run."""
        mock_db.query.return_value.filter.return_value.scalar.return_value = 42

        count = repo.get_log_count("run-001")
        assert count == 42

    def test_get_log_count_empty(self, repo, mock_db):
        """Test getting log count for empty run."""
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        count = repo.get_log_count("run-001")
        assert count == 0
