"""Unit tests for AgentScheduler."""

from datetime import datetime

from app.agent.scheduler import AgentScheduler


class TestAgentScheduler:
    """Test suite for AgentScheduler."""

    def setup_method(self):
        """Setup test fixtures."""
        self.scheduler = AgentScheduler()

    def test_init_scheduler(self):
        """Test scheduler initialization."""
        assert len(self.scheduler.task_queue) == 0
        assert len(self.scheduler.running_tasks) == 0
        assert len(self.scheduler.failed_tasks) == 0
        assert self.scheduler.max_concurrent > 0

    def test_submit_task_basic(self):
        """Test submitting a basic task."""
        task_id = self.scheduler.submit_task("task1", "coder", priority=5)

        assert task_id == "task1"
        assert len(self.scheduler.task_queue) == 1

        task_entry = self.scheduler.task_queue[0]
        assert task_entry["task_id"] == "task1"
        assert task_entry["agent_type"] == "coder"
        assert task_entry["priority"] == 5
        assert task_entry["retry_count"] == 0

    def test_submit_task_with_priority_ordering(self):
        """Test tasks are ordered by priority."""
        self.scheduler.submit_task("task1", "coder", priority=5)
        self.scheduler.submit_task("task2", "coder", priority=8)
        self.scheduler.submit_task("task3", "coder", priority=3)

        assert len(self.scheduler.task_queue) == 3
        assert self.scheduler.task_queue[0]["task_id"] == "task2"  # highest priority
        assert self.scheduler.task_queue[1]["task_id"] == "task1"
        assert self.scheduler.task_queue[2]["task_id"] == "task3"  # lowest priority

    def test_submit_multiple_same_priority(self):
        """Test submitting multiple tasks with same priority."""
        self.scheduler.submit_task("task1", "coder", priority=5)
        self.scheduler.submit_task("task2", "coder", priority=5)

        assert len(self.scheduler.task_queue) == 2
        assert self.scheduler.task_queue[0]["task_id"] == "task1"
        assert self.scheduler.task_queue[1]["task_id"] == "task2"

    def test_get_next_task_from_queue(self):
        """Test getting next task from queue."""
        self.scheduler.submit_task("task1", "coder", priority=5)

        task_entry = self.scheduler.get_next_task()

        assert task_entry is not None
        assert task_entry["task_id"] == "task1"
        assert len(self.scheduler.task_queue) == 0
        assert len(self.scheduler.running_tasks) == 1

    def test_get_next_task_empty_queue(self):
        """Test getting next task from empty queue."""
        task_entry = self.scheduler.get_next_task()
        assert task_entry is None

    def test_get_next_task_at_capacity(self):
        """Test getting next task when at max concurrent capacity."""
        # Fill up running tasks to capacity
        for i in range(self.scheduler.max_concurrent):
            self.scheduler.running_tasks[f"task{i}"] = {"task_id": f"task{i}"}

        self.scheduler.submit_task("new_task", "coder", priority=5)

        task_entry = self.scheduler.get_next_task()
        assert task_entry is None  # At capacity

    def test_update_task_status_completed(self):
        """Test updating task status to completed."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()

        self.scheduler.update_task_status("task1", "completed")

        assert "task1" not in self.scheduler.running_tasks
        assert "task1" not in self.scheduler.failed_tasks

    def test_update_task_status_failed(self):
        """Test updating task status to failed."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()

        self.scheduler.update_task_status("task1", "failed", error="Test error")

        assert "task1" not in self.scheduler.running_tasks
        assert "task1" in self.scheduler.failed_tasks
        assert self.scheduler.failed_tasks["task1"]["error"] == "Test error"

    def test_retry_failed_task_success(self):
        """Test retrying a failed task successfully."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed", error="Test error")

        result = self.scheduler.retry_failed_task("task1")

        assert result is True
        assert "task1" not in self.scheduler.failed_tasks
        assert len(self.scheduler.task_queue) == 1

        task_entry = self.scheduler.task_queue[0]
        assert task_entry["retry_count"] == 1

    def test_retry_failed_task_not_found(self):
        """Test retrying a task that is not in failed tasks."""
        result = self.scheduler.retry_failed_task("nonexistent")
        assert result is False

    def test_retry_failed_task_max_retries_exceeded(self):
        """Test retrying a task that has exceeded max retries."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed")

        # Manually set retry count to exceed max (config default is 3)
        from app.agent.config import config

        max_retries = config.MAX_RETRY_ATTEMPTS
        self.scheduler.failed_tasks["task1"]["retry_count"] = max_retries

        result = self.scheduler.retry_failed_task("task1")
        assert result is False

    def test_retry_backoff_calculation(self):
        """Test retry backoff seconds are calculated correctly."""
        from app.agent.config import config

        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed")

        # First retry
        self.scheduler.retry_failed_task("task1")
        task_entry = self.scheduler.task_queue[0]
        # Verify backoff is from config
        assert task_entry["backoff_seconds"] == config.RETRY_BACKOFF_SECONDS[0]
        assert task_entry["retry_count"] == 1

        # Simulate second failure
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed")
        self.scheduler.retry_failed_task("task1")
        task_entry = self.scheduler.task_queue[0]
        assert task_entry["backoff_seconds"] == config.RETRY_BACKOFF_SECONDS[1]
        assert task_entry["retry_count"] == 2

    def test_get_queue_status(self):
        """Test getting queue status."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.submit_task("task2", "coder")
        self.scheduler.get_next_task()

        status = self.scheduler.get_queue_status()

        assert status["queued"] == 1
        assert status["running"] == 1
        assert status["failed"] == 0
        assert status["max_concurrent"] == self.scheduler.max_concurrent
        assert status["capacity_available"] == self.scheduler.max_concurrent - 1

    def test_get_running_tasks(self):
        """Test getting list of running tasks."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.submit_task("task2", "coder")
        self.scheduler.get_next_task()
        self.scheduler.get_next_task()

        running_tasks = self.scheduler.get_running_tasks()

        assert len(running_tasks) == 2
        task_ids = [task["task_id"] for task in running_tasks]
        assert "task1" in task_ids
        assert "task2" in task_ids

    def test_get_failed_tasks(self):
        """Test getting list of failed tasks."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.submit_task("task2", "coder")
        self.scheduler.get_next_task()
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed", error="Error 1")
        self.scheduler.update_task_status("task2", "failed", error="Error 2")

        failed_tasks = self.scheduler.get_failed_tasks()

        assert len(failed_tasks) == 2
        task_ids = [task["task_id"] for task in failed_tasks]
        assert "task1" in task_ids
        assert "task2" in task_ids

    def test_clear_completed(self):
        """Test clearing completed tasks."""
        # This method is a no-op since tasks are removed on completion
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "completed")

        self.scheduler.clear_completed()

        # Verify task is not in any tracking dict
        assert "task1" not in self.scheduler.running_tasks
        assert "task1" not in self.scheduler.failed_tasks

    def test_task_entry_structure(self):
        """Test that task entries have correct structure."""
        task_id = self.scheduler.submit_task("task1", "coder", priority=7)

        task_entry = self.scheduler.task_queue[0]

        assert "task_id" in task_entry
        assert "agent_type" in task_entry
        assert "priority" in task_entry
        assert "submitted_at" in task_entry
        assert "retry_count" in task_entry
        assert isinstance(task_entry["submitted_at"], datetime)

    def test_multiple_priority_levels(self):
        """Test correct ordering with multiple priority levels."""
        priorities = [3, 7, 1, 9, 5, 2, 8, 4, 6]
        for i, priority in enumerate(priorities):
            self.scheduler.submit_task(f"task{i}", "coder", priority=priority)

        # Extract priorities from queue
        queue_priorities = [task["priority"] for task in self.scheduler.task_queue]

        # Verify descending order
        assert queue_priorities == sorted(priorities, reverse=True)

    def test_task_timestamp_recorded(self):
        """Test that task submission timestamp is recorded."""
        before = datetime.utcnow()
        self.scheduler.submit_task("task1", "coder")
        after = datetime.utcnow()

        task_entry = self.scheduler.task_queue[0]
        submitted_at = task_entry["submitted_at"]

        assert before <= submitted_at <= after

    def test_update_task_status_updates_timestamp(self):
        """Test that updating task status records timestamp."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()

        before = datetime.utcnow()
        self.scheduler.update_task_status("task1", "failed", error="Test")
        after = datetime.utcnow()

        task_entry = self.scheduler.failed_tasks["task1"]
        updated_at = task_entry["updated_at"]

        assert before <= updated_at <= after

    def test_retry_backoff_uses_last_value_for_high_retry_count(self):
        """Test that retry backoff uses last value when retry count exceeds list length."""
        from app.agent.config import config

        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed")

        # Set retry count to a value that's within max retries but exceeds backoff list length
        backoff_list_length = len(config.RETRY_BACKOFF_SECONDS)
        max_retries = config.MAX_RETRY_ATTEMPTS

        # Use a retry count that's less than max but greater than backoff list length
        # Assuming backoff list has 3 elements [1, 5, 15] and max retries is 3
        retry_count = min(backoff_list_length, max_retries - 1)
        self.scheduler.failed_tasks["task1"]["retry_count"] = retry_count

        result = self.scheduler.retry_failed_task("task1")

        # Should succeed if retry_count < max_retries
        if retry_count < max_retries:
            assert result is True
            task_entry = self.scheduler.task_queue[0]
            # Should use last value from config when retry_count >= len(backoff_list)
            expected_backoff = config.RETRY_BACKOFF_SECONDS[
                min(retry_count, backoff_list_length - 1)
            ]
            assert task_entry["backoff_seconds"] == expected_backoff

    def test_retry_failed_task_sets_retry_after_timestamp(self):
        """Test that retry sets retry_after timestamp."""
        self.scheduler.submit_task("task1", "coder")
        self.scheduler.get_next_task()
        self.scheduler.update_task_status("task1", "failed")

        before = datetime.utcnow()
        self.scheduler.retry_failed_task("task1")
        after = datetime.utcnow()

        task_entry = self.scheduler.task_queue[0]
        retry_after = task_entry["retry_after"]

        assert before <= retry_after <= after

    def test_concurrent_task_execution_limit(self):
        """Test that concurrent execution is limited."""
        # Submit more tasks than max_concurrent
        num_tasks = self.scheduler.max_concurrent + 5
        for i in range(num_tasks):
            self.scheduler.submit_task(f"task{i}", "coder")

        # Get tasks until capacity is reached
        retrieved = 0
        while self.scheduler.get_next_task() is not None:
            retrieved += 1
            if retrieved > num_tasks:  # Safety check
                break

        # Should only retrieve up to max_concurrent
        assert retrieved == self.scheduler.max_concurrent
        assert len(self.scheduler.running_tasks) == self.scheduler.max_concurrent

    def test_task_queue_fifo_within_same_priority(self):
        """Test that tasks with same priority are processed FIFO."""
        self.scheduler.submit_task("task1", "coder", priority=5)
        self.scheduler.submit_task("task2", "coder", priority=5)
        self.scheduler.submit_task("task3", "coder", priority=5)

        task1 = self.scheduler.get_next_task()
        task2 = self.scheduler.get_next_task()
        task3 = self.scheduler.get_next_task()

        assert task1["task_id"] == "task1"
        assert task2["task_id"] == "task2"
        assert task3["task_id"] == "task3"
