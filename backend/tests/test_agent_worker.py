"""
Tests for Agent Worker
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from app.agent.worker import AgentWorker


class TestAgentWorker:
    """Test suite for Agent Worker."""

    def setup_method(self):
        """Setup for each test method."""
        self.worker = AgentWorker()

    def test_init(self):
        """Test worker initialization."""
        assert self.worker.running is False

    @pytest.mark.asyncio
    async def test_start_sets_running(self):
        """Test that start sets running flag."""

        # Mock the process methods to avoid infinite loop
        async def mock_process():
            await asyncio.sleep(0.1)
            self.worker.running = False

        with patch.object(self.worker, "process_tasks", mock_process):
            with patch("app.agent.worker.scheduler") as mock_scheduler:
                mock_scheduler.auto_retry_failed_tasks = AsyncMock(return_value=None)
                await self.worker.start()

        assert self.worker.running is False  # Should be False after stopping

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping the worker."""
        self.worker.running = True
        await self.worker.stop()
        assert self.worker.running is False

    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test successful task execution."""
        task_entry = {
            "task_id": "task-123",
            "agent_type": "code-gen",
        }

        # Mock dependencies
        with patch("app.agent.worker.SessionLocal") as mock_session:
            with patch("app.agent.worker.TaskRepository") as mock_task_repo_class:
                with patch("app.agent.worker.AgentExecutor") as mock_executor_class:
                    with patch("app.agent.worker.scheduler") as mock_scheduler:
                        # Setup mocks
                        mock_db = Mock()
                        mock_session.return_value = mock_db

                        mock_task = Mock()
                        mock_task.id = "task-123"
                        mock_task_repo = Mock()
                        mock_task_repo.get_by_id.return_value = mock_task
                        mock_task_repo_class.return_value = mock_task_repo

                        mock_execution = Mock()
                        mock_executor = Mock()
                        mock_executor.execute_task.return_value = mock_execution
                        mock_executor_class.return_value = mock_executor

                        # Execute
                        await self.worker._execute_task(task_entry)

                        # Verify
                        mock_executor.execute_task.assert_called_once_with(mock_task, "code-gen")
                        mock_scheduler.update_task_status.assert_called_once_with(
                            "task-123", "completed"
                        )

    @pytest.mark.asyncio
    async def test_execute_task_not_found(self):
        """Test task execution when task not found."""
        task_entry = {
            "task_id": "task-123",
            "agent_type": "code-gen",
        }

        with patch("app.agent.worker.SessionLocal") as mock_session:
            with patch("app.agent.worker.TaskRepository") as mock_task_repo_class:
                with patch("app.agent.worker.scheduler") as mock_scheduler:
                    mock_db = Mock()
                    mock_session.return_value = mock_db

                    mock_task_repo = Mock()
                    mock_task_repo.get_by_id.return_value = None
                    mock_task_repo_class.return_value = mock_task_repo

                    await self.worker._execute_task(task_entry)

                    mock_scheduler.update_task_status.assert_called_once_with(
                        "task-123", "failed", "Task not found"
                    )

    @pytest.mark.asyncio
    async def test_execute_task_failure(self):
        """Test task execution failure."""
        task_entry = {
            "task_id": "task-123",
            "agent_type": "code-gen",
        }

        with patch("app.agent.worker.SessionLocal") as mock_session:
            with patch("app.agent.worker.TaskRepository") as mock_task_repo_class:
                with patch("app.agent.worker.AgentExecutor") as mock_executor_class:
                    with patch("app.agent.worker.scheduler") as mock_scheduler:
                        mock_db = Mock()
                        mock_session.return_value = mock_db

                        mock_task = Mock()
                        mock_task_repo = Mock()
                        mock_task_repo.get_by_id.return_value = mock_task
                        mock_task_repo_class.return_value = mock_task_repo

                        mock_executor = Mock()
                        mock_executor.execute_task.side_effect = Exception("Execution failed")
                        mock_executor_class.return_value = mock_executor

                        await self.worker._execute_task(task_entry)

                        mock_scheduler.update_task_status.assert_called_once_with(
                            "task-123", "failed", "Execution failed"
                        )
