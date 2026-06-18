"""
Agent Scheduler for managing task queue and execution.
"""

import asyncio
from collections import deque
from datetime import datetime

from app.agent.config import config


class AgentScheduler:
    """Scheduler for Agent task execution."""

    def __init__(self):
        """Initialize the scheduler."""
        self.task_queue: deque = deque()
        self.running_tasks: dict = {}
        self.failed_tasks: dict = {}
        self.max_concurrent = config.MAX_CONCURRENT_AGENTS

    def submit_task(self, task_id: str, agent_type: str, priority: int = 5) -> str:
        """
        Submit a task to the execution queue.

        Args:
            task_id: Task ID
            agent_type: Type of agent to use
            priority: Task priority (0-10, higher = more urgent)

        Returns:
            Task submission ID
        """
        task_entry = {
            "task_id": task_id,
            "agent_type": agent_type,
            "priority": priority,
            "submitted_at": datetime.utcnow(),
            "retry_count": 0,
        }

        # Insert based on priority (higher priority first)
        inserted = False
        for i, existing_task in enumerate(self.task_queue):
            if priority > existing_task["priority"]:
                self.task_queue.insert(i, task_entry)
                inserted = True
                break

        if not inserted:
            self.task_queue.append(task_entry)

        return task_id

    def get_next_task(self) -> dict | None:
        """
        Get the next task to execute.

        Returns:
            Task entry or None if queue is empty or at capacity
        """
        if len(self.running_tasks) >= self.max_concurrent:
            return None

        if not self.task_queue:
            return None

        task_entry = self.task_queue.popleft()
        self.running_tasks[task_entry["task_id"]] = task_entry
        return task_entry

    def update_task_status(self, task_id: str, status: str, error: str | None = None):
        """
        Update task execution status.

        Args:
            task_id: Task ID
            status: New status
            error: Error message if failed
        """
        if task_id in self.running_tasks:
            task_entry = self.running_tasks[task_id]
            task_entry["status"] = status
            task_entry["updated_at"] = datetime.utcnow()

            if status == "completed":
                del self.running_tasks[task_id]
            elif status == "failed":
                task_entry["error"] = error
                # Keep existing retry_count, don't reset it
                self.failed_tasks[task_id] = task_entry
                del self.running_tasks[task_id]

    def retry_failed_task(self, task_id: str) -> bool:
        """
        Retry a failed task.

        Args:
            task_id: Task ID to retry

        Returns:
            True if task was resubmitted, False otherwise
        """
        if task_id not in self.failed_tasks:
            return False

        task_entry = self.failed_tasks[task_id]
        retry_count = task_entry.get("retry_count", 0)

        if retry_count >= config.MAX_RETRY_ATTEMPTS:
            return False

        # Calculate backoff delay
        if retry_count < len(config.RETRY_BACKOFF_SECONDS):
            backoff = config.RETRY_BACKOFF_SECONDS[retry_count]
        else:
            backoff = config.RETRY_BACKOFF_SECONDS[-1]

        # Resubmit with incremented retry count
        task_entry["retry_count"] = retry_count + 1
        task_entry["retry_after"] = datetime.utcnow()
        task_entry["backoff_seconds"] = backoff

        self.task_queue.append(task_entry)
        del self.failed_tasks[task_id]

        return True

    def get_queue_status(self) -> dict:
        """
        Get current queue status.

        Returns:
            Dictionary with queue statistics
        """
        return {
            "queued": len(self.task_queue),
            "running": len(self.running_tasks),
            "failed": len(self.failed_tasks),
            "max_concurrent": self.max_concurrent,
            "capacity_available": self.max_concurrent - len(self.running_tasks),
        }

    def get_running_tasks(self) -> list[dict]:
        """
        Get list of currently running tasks.

        Returns:
            List of running task entries
        """
        return list(self.running_tasks.values())

    def get_failed_tasks(self) -> list[dict]:
        """
        Get list of failed tasks.

        Returns:
            List of failed task entries
        """
        return list(self.failed_tasks.values())

    def clear_completed(self):
        """Clear all completed tasks from tracking."""
        pass  # Already removed in update_task_status

    async def auto_retry_failed_tasks(self):
        """Background task to auto-retry failed tasks with backoff."""
        while True:
            current_time = datetime.utcnow()

            for task_id in list(self.failed_tasks.keys()):
                task_entry = self.failed_tasks[task_id]
                retry_after = task_entry.get("retry_after")

                if retry_after and (current_time - retry_after).total_seconds() >= task_entry.get(
                    "backoff_seconds", 0
                ):
                    self.retry_failed_task(task_id)

            await asyncio.sleep(config.QUEUE_POLL_INTERVAL_SECONDS)


# Global scheduler instance
scheduler = AgentScheduler()
