"""
Tests for Agent Scheduler
"""
import pytest
from datetime import datetime

from app.agent.scheduler import AgentScheduler


class TestAgentScheduler:
    """Test suite for Agent Scheduler."""

    def setup_method(self):
        """Setup for each test method."""
        self.scheduler = AgentScheduler()

    def test_submit_task(self):
        """Test task submission."""
        task_id = self.scheduler.submit_task("task-1", "code-gen", priority=5)

        assert task_id == "task-1"
        assert len(self.scheduler.task_queue) == 1

    def test_submit_multiple_tasks(self):
        """Test multiple task submissions."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.submit_task("task-2", "refactor", priority=3)
        self.scheduler.submit_task("task-3", "bug-fix", priority=8)

        assert len(self.scheduler.task_queue) == 3

    def test_priority_ordering(self):
        """Test tasks are ordered by priority."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.submit_task("task-2", "refactor", priority=3)
        self.scheduler.submit_task("task-3", "bug-fix", priority=8)

        # Highest priority should be first
        next_task = self.scheduler.get_next_task()
        assert next_task["task_id"] == "task-3"
        assert next_task["priority"] == 8

    def test_get_next_task_empty_queue(self):
        """Test getting next task from empty queue."""
        next_task = self.scheduler.get_next_task()

        assert next_task is None

    def test_get_next_task_moves_to_running(self):
        """Test that getting next task moves it to running."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)

        next_task = self.scheduler.get_next_task()

        assert next_task is not None
        assert len(self.scheduler.task_queue) == 0
        assert len(self.scheduler.running_tasks) == 1
        assert "task-1" in self.scheduler.running_tasks

    def test_max_concurrent_limit(self):
        """Test max concurrent tasks limit."""
        # Fill up to max concurrent
        for i in range(self.scheduler.max_concurrent):
            self.scheduler.submit_task(f"task-{i}", "code-gen", priority=5)
            self.scheduler.get_next_task()

        # Submit one more task
        self.scheduler.submit_task("task-extra", "code-gen", priority=5)

        # Should not get next task (at capacity)
        next_task = self.scheduler.get_next_task()
        assert next_task is None

    def test_update_task_status_completed(self):
        """Test updating task status to completed."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.get_next_task()

        self.scheduler.update_task_status("task-1", "completed")

        assert len(self.scheduler.running_tasks) == 0
        assert "task-1" not in self.scheduler.running_tasks

    def test_update_task_status_failed(self):
        """Test updating task status to failed."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.get_next_task()

        self.scheduler.update_task_status("task-1", "failed", error="Test error")

        assert len(self.scheduler.running_tasks) == 0
        assert len(self.scheduler.failed_tasks) == 1
        assert "task-1" in self.scheduler.failed_tasks
        assert self.scheduler.failed_tasks["task-1"]["error"] == "Test error"

    def test_retry_failed_task(self):
        """Test retrying a failed task."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task-1", "failed", error="Test error")

        success = self.scheduler.retry_failed_task("task-1")

        assert success is True
        assert len(self.scheduler.task_queue) == 1
        assert "task-1" not in self.scheduler.failed_tasks

    def test_retry_non_existent_task(self):
        """Test retrying a task that doesn't exist."""
        success = self.scheduler.retry_failed_task("non-existent")

        assert success is False

    def test_retry_max_attempts_reached(self):
        """Test retry when max attempts reached."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.get_next_task()

        # Retry up to MAX_RETRY_ATTEMPTS (3)
        # First failure + 3 retries = 4 attempts total
        for attempt in range(4):
            self.scheduler.update_task_status("task-1", "failed", error="Test error")
            success = self.scheduler.retry_failed_task("task-1")

            if attempt < 3:  # First 3 retries should succeed
                assert success is True
                self.scheduler.get_next_task()  # Get task to run it
            else:  # 4th retry should fail (already retried 3 times)
                assert success is False

    def test_get_queue_status(self):
        """Test getting queue status."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.submit_task("task-2", "refactor", priority=3)
        self.scheduler.get_next_task()

        status = self.scheduler.get_queue_status()

        assert status["queued"] == 1
        assert status["running"] == 1
        assert status["failed"] == 0
        assert status["max_concurrent"] == self.scheduler.max_concurrent
        assert status["capacity_available"] == self.scheduler.max_concurrent - 1

    def test_get_running_tasks(self):
        """Test getting running tasks."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.submit_task("task-2", "refactor", priority=3)
        self.scheduler.get_next_task()
        self.scheduler.get_next_task()

        running = self.scheduler.get_running_tasks()

        assert len(running) == 2
        assert any(t["task_id"] == "task-1" for t in running)
        assert any(t["task_id"] == "task-2" for t in running)

    def test_get_failed_tasks(self):
        """Test getting failed tasks."""
        self.scheduler.submit_task("task-1", "code-gen", priority=5)
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task-1", "failed", error="Test error")

        failed = self.scheduler.get_failed_tasks()

        assert len(failed) == 1
        assert failed[0]["task_id"] == "task-1"
        assert failed[0]["error"] == "Test error"

    def test_task_entry_has_metadata(self):
        """Test that task entry contains required metadata."""
        self.scheduler.submit_task("task-1", "code-gen", priority=7)

        task_entry = self.scheduler.get_next_task()

        assert task_entry["task_id"] == "task-1"
        assert task_entry["agent_type"] == "code-gen"
        assert task_entry["priority"] == 7
        assert task_entry["retry_count"] == 0
        assert "submitted_at" in task_entry
        assert isinstance(task_entry["submitted_at"], datetime)
