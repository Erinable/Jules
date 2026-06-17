"""
Tests for Agent Executor
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.agent.executor import AgentExecutor
from app.models.task import Task


class TestAgentExecutor:
    """Test suite for Agent Executor."""

    def setup_method(self):
        """Setup for each test method."""
        self.mock_db = Mock()
        self.executor = AgentExecutor(self.mock_db)

    def test_init(self):
        """Test executor initialization."""
        assert self.executor.db == self.mock_db
        assert self.executor.llm_client is not None
        assert self.executor.analyzer is not None

    @patch('app.agent.executor.AgentExecution')
    def test_execute_task_success(self, mock_execution_class):
        """Test successful task execution."""
        # Create mock task
        mock_task = Mock(spec=Task)
        mock_task.id = "task-123"
        mock_task.project_id = "proj-1"
        mock_task.title = "Test Task"
        mock_task.description = "Test description"
        mock_task.status = "pending"

        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "exec-123"
        mock_execution_class.return_value = mock_execution

        # Mock LLM client
        self.executor.llm_client.generate = Mock(return_value="def test():\n    pass")

        # Mock analyzer
        self.executor.analyzer.analyze = Mock(return_value={
            "avg_complexity": 1.0,
            "maintainability_index": 90.0,
            "security_issues": 0
        })

        # Execute
        result = self.executor.execute_task(mock_task, "code-gen")

        # Verify
        assert result == mock_execution
        assert mock_execution.status == "completed"
        assert mock_task.status == "completed"

    @patch('app.agent.executor.AgentExecution')
    def test_execute_task_failure(self, mock_execution_class):
        """Test task execution failure."""
        mock_task = Mock(spec=Task)
        mock_task.id = "task-123"
        mock_task.project_id = "proj-1"
        mock_task.title = "Test Task"
        mock_task.description = "Test"
        mock_task.status = "pending"

        mock_execution = Mock()
        mock_execution_class.return_value = mock_execution

        # Make LLM client raise exception
        self.executor.llm_client.generate = Mock(side_effect=Exception("LLM Error"))

        # Execute and expect exception
        with pytest.raises(Exception, match="LLM Error"):
            self.executor.execute_task(mock_task, "code-gen")

        # Verify failure handling
        assert mock_execution.status == "failed"
        assert mock_task.status == "failed"
        assert mock_execution.error_message == "LLM Error"

    def test_generate_code(self):
        """Test code generation."""
        mock_task = Mock(spec=Task)
        mock_task.title = "Create API"
        mock_task.description = "RESTful API"

        self.executor.llm_client.generate = Mock(return_value="# Generated code")

        code = self.executor.generate_code(mock_task)

        assert code == "# Generated code"
        assert self.executor.llm_client.generate.called

    def test_build_prompt(self):
        """Test prompt building."""
        mock_task = Mock(spec=Task)
        mock_task.title = "Test Task"
        mock_task.description = "Task description"

        prompt = self.executor._build_prompt(mock_task)

        assert "Test Task" in prompt
        assert "Task description" in prompt
        assert "Python" in prompt

    def test_build_prompt_no_description(self):
        """Test prompt building with no description."""
        mock_task = Mock(spec=Task)
        mock_task.title = "Test Task"
        mock_task.description = None

        prompt = self.executor._build_prompt(mock_task)

        assert "Test Task" in prompt
        assert "No description provided" in prompt

    @patch('app.agent.executor.QualityMetric')
    def test_analyze_quality(self, mock_metric_class):
        """Test quality analysis."""
        code = "def test():\n    pass"
        project_id = "proj-1"

        mock_metric = Mock()
        mock_metric_class.return_value = mock_metric

        self.executor.analyzer.analyze = Mock(return_value={
            "avg_complexity": 1.5,
            "maintainability_index": 85.0,
            "security_issues": 0
        })

        result = self.executor.analyze_quality(code, project_id)

        assert result == mock_metric
        self.mock_db.add.assert_called_with(mock_metric)
        self.mock_db.commit.assert_called()

    @patch('app.agent.executor.CodeFile')
    def test_save_code_version(self, mock_codefile_class):
        """Test saving code version."""
        project_id = "proj-1"
        content = "def test():\n    pass"
        file_path = "test.py"

        mock_file = Mock()
        mock_codefile_class.return_value = mock_file

        result = self.executor.save_code_version(project_id, content, file_path)

        assert result == mock_file
        self.mock_db.add.assert_called_with(mock_file)
        self.mock_db.commit.assert_called()

    def test_save_code_version_calculates_hash(self):
        """Test that code file hash is calculated."""
        import hashlib

        project_id = "proj-1"
        content = "test content"
        file_path = "test.py"

        with patch('app.agent.executor.CodeFile') as mock_codefile_class:
            mock_file = Mock()
            mock_codefile_class.return_value = mock_file

            self.executor.save_code_version(project_id, content, file_path)

            # Verify CodeFile was called with hash
            call_kwargs = mock_codefile_class.call_args[1]
            expected_hash = hashlib.sha256(content.encode()).hexdigest()
            assert call_kwargs["hash"] == expected_hash
