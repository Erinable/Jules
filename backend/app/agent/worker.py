"""
Background worker for processing agent tasks.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from app.agent.config import config
from app.agent.executor import AgentExecutor
from app.agent.scheduler import scheduler
from app.database import SessionLocal
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class AgentWorker:
    """Background worker for agent task processing."""

    def __init__(self):
        """Initialize the worker."""
        self.running = False

    async def start(self):
        """Start the worker."""
        self.running = True
        logger.info("Agent worker started")

        # Start both processing and retry loops
        await asyncio.gather(
            self.process_tasks(),
            scheduler.auto_retry_failed_tasks(),
        )

    async def stop(self):
        """Stop the worker."""
        self.running = False
        logger.info("Agent worker stopped")

    async def process_tasks(self):
        """Process tasks from the queue."""
        while self.running:
            try:
                # Get next task from scheduler
                task_entry = scheduler.get_next_task()

                if task_entry:
                    # Process task in background
                    asyncio.create_task(self._execute_task(task_entry))
                else:
                    # No tasks available, wait before checking again
                    await asyncio.sleep(config.QUEUE_POLL_INTERVAL_SECONDS)

            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task_entry: dict):
        """
        Execute a single task.

        Args:
            task_entry: Task entry from scheduler
        """
        task_id = task_entry["task_id"]
        agent_type = task_entry["agent_type"]

        db: Session = SessionLocal()
        try:
            # Get task
            task_repo = TaskRepository(db)
            task = task_repo.get_by_id(task_id)

            if not task:
                logger.error(f"Task {task_id} not found")
                scheduler.update_task_status(task_id, "failed", "Task not found")
                return

            # Execute task
            executor = AgentExecutor(db)
            execution = executor.execute_task(task, agent_type)

            # Update scheduler
            scheduler.update_task_status(task_id, "completed")
            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            scheduler.update_task_status(task_id, "failed", str(e))

        finally:
            db.close()

    async def cleanup_old_executions(self):
        """Cleanup old execution records (optional maintenance task)."""
        while self.running:
            try:
                # Wait 1 hour between cleanups
                await asyncio.sleep(3600)

                # TODO: Implement cleanup logic
                # - Remove executions older than X days
                # - Archive completed tasks
                logger.info("Cleanup task executed")

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")


# Global worker instance
worker = AgentWorker()
