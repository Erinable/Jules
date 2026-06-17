"""
Agent Executor for task execution and code generation.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.agent_execution import AgentExecution
from app.models.code_file import CodeFile
from app.models.quality_metric import QualityMetric
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.code_file_repository import CodeFileRepository
from app.repositories.quality_metric_repository import QualityMetricRepository
from app.repositories.task_repository import TaskRepository
from app.agent.llm_client import LLMClient
from app.agent.analyzer import CodeAnalyzer
from app.agent.config import config


class AgentExecutor:
    """Executor for Agent tasks."""

    def __init__(self, db: Session):
        """
        Initialize the executor.

        Args:
            db: Database session
        """
        self.db = db
        self.llm_client = LLMClient()
        self.analyzer = CodeAnalyzer()
        self.execution_repo = AgentExecutionRepository(db)
        self.code_file_repo = CodeFileRepository(db)
        self.quality_repo = QualityMetricRepository(db)
        self.task_repo = TaskRepository(db)

    def execute_task(self, task: Task, agent_type: str) -> AgentExecution:
        """
        Execute a task.

        Args:
            task: Task to execute
            agent_type: Type of agent

        Returns:
            AgentExecution record
        """
        # Create execution record
        execution = AgentExecution(
            task_id=task.id,
            agent_type=agent_type,
            status="running",
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        try:
            # Update task status
            task.status = "in_progress"
            self.db.commit()

            # Generate code
            code = self.generate_code(task)

            # Save code file
            code_file = self.save_code_version(task.project_id, code, task.title)

            # Analyze quality
            quality_metric = self.analyze_quality(code, task.project_id)

            # Update execution
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.output = f"Generated {len(code)} characters of code"
            self.db.commit()

            # Update task
            task.status = "completed"
            self.db.commit()

            return execution

        except Exception as e:
            # Handle failure
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            self.db.commit()

            task.status = "failed"
            self.db.commit()

            raise

    def generate_code(self, task: Task) -> str:
        """
        Generate code for a task.

        Args:
            task: Task to generate code for

        Returns:
            Generated code
        """
        # Build prompt from task
        prompt = self._build_prompt(task)

        # Generate code using LLM
        code = self.llm_client.generate(prompt, model=config.DEFAULT_LLM_MODEL)

        return code

    def _build_prompt(self, task: Task) -> str:
        """
        Build prompt for code generation.

        Args:
            task: Task

        Returns:
            Prompt string
        """
        prompt = f"""
Generate Python code for the following task:

Title: {task.title}
Description: {task.description or 'No description provided'}

Requirements:
- Write clean, well-documented Python code
- Include type hints
- Follow PEP 8 style guide
- Add docstrings for functions and classes

Return only the Python code without explanations.
"""
        return prompt

    def analyze_quality(self, code: str, project_id: str) -> QualityMetric:
        """
        Analyze code quality.

        Args:
            code: Code to analyze
            project_id: Project ID

        Returns:
            QualityMetric record
        """
        # Analyze code
        analysis = self.analyzer.analyze(code, language="python")

        # Create quality metric
        metric = QualityMetric(
            project_id=project_id,
            avg_complexity=analysis["avg_complexity"],
            maintainability_index=analysis["maintainability_index"],
            security_issues=analysis["security_issues"],
            test_coverage=0.0,  # Not calculated for generated code
            measured_at=datetime.utcnow(),
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)

        return metric

    def save_code_version(
        self,
        project_id: str,
        content: str,
        file_path: str
    ) -> CodeFile:
        """
        Save code file version.

        Args:
            project_id: Project ID
            content: File content
            file_path: File path

        Returns:
            CodeFile record
        """
        import hashlib

        # Calculate hash
        file_hash = hashlib.sha256(content.encode()).hexdigest()

        # Create or update code file
        code_file = CodeFile(
            project_id=project_id,
            path=file_path,
            content=content,
            hash=file_hash,
        )
        self.db.add(code_file)
        self.db.commit()
        self.db.refresh(code_file)

        return code_file
