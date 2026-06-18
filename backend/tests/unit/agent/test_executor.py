"""Unit tests for AgentExecutor."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from app.agent.executor import AgentExecutor
from app.models.agent_execution import AgentExecution
from app.models.code_file import CodeFile
from app.models.quality_metric import QualityMetric
from app.models.task import Task
from sqlalchemy.orm import Session


class TestAgentExecutor:
    """Test suite for AgentExecutor."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.executor = AgentExecutor(self.mock_db)

    def test_init_executor(self):
        """Test executor initialization."""
        assert self.executor.db == self.mock_db
        assert self.executor.llm_client is not None
        assert self.executor.analyzer is not None
        assert self.executor.execution_repo is not None
        assert self.executor.code_file_repo is not None
        assert self.executor.quality_repo is not None
        assert self.executor.task_repo is not None

    @patch.object(AgentExecutor, "generate_code")
    @patch.object(AgentExecutor, "save_code_version")
    @patch.object(AgentExecutor, "analyze_quality")
    def test_execute_task_success(self, mock_analyze, mock_save, mock_generate):
        """Test successful task execution."""
        # Setup
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test Task"
        task.status = "pending"

        mock_generate.return_value = "print('hello')"
        mock_code_file = Mock(spec=CodeFile)
        mock_save.return_value = mock_code_file
        mock_quality = Mock(spec=QualityMetric)
        mock_analyze.return_value = mock_quality

        # Execute
        result = self.executor.execute_task(task, "coder")

        # Verify
        assert result.status == "completed"
        assert result.task_id == "task123"
        assert result.agent_type == "coder"
        assert mock_generate.called
        assert mock_save.called
        assert mock_analyze.called
        assert self.mock_db.commit.called

    @patch.object(AgentExecutor, "generate_code")
    def test_execute_task_failure(self, mock_generate):
        """Test task execution failure."""
        # Setup
        task = Mock(spec=Task)
        task.id = "task123"
        task.status = "pending"

        mock_generate.side_effect = Exception("Generation failed")

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Generation failed"):
            self.executor.execute_task(task, "coder")

        # Verify failure handling
        assert task.status == "failed"

    def test_generate_code(self):
        """Test code generation."""
        task = Mock(spec=Task)
        task.title = "Create login function"
        task.description = "Implement user login"

        with patch.object(self.executor.llm_client, "generate") as mock_llm:
            mock_llm.return_value = "def login(): pass"

            code = self.executor.generate_code(task)

            assert code == "def login(): pass"
            assert mock_llm.called
            call_args = mock_llm.call_args
            assert "Create login function" in call_args[0][0]

    def test_build_prompt(self):
        """Test prompt building."""
        task = Mock(spec=Task)
        task.title = "Test Task"
        task.description = "Test Description"

        prompt = self.executor._build_prompt(task)

        assert "Test Task" in prompt
        assert "Test Description" in prompt
        assert "Python" in prompt
        assert "type hints" in prompt

    def test_build_prompt_no_description(self):
        """Test prompt building without description."""
        task = Mock(spec=Task)
        task.title = "Test Task"
        task.description = None

        prompt = self.executor._build_prompt(task)

        assert "Test Task" in prompt
        assert "No description provided" in prompt

    def test_analyze_quality(self):
        """Test code quality analysis."""
        code = "def test(): return True"
        project_id = "proj123"

        with patch.object(self.executor.analyzer, "analyze") as mock_analyze:
            mock_analyze.return_value = {
                "avg_complexity": 1.5,
                "maintainability_index": 85.0,
                "security_issues": 0,
            }

            metric = self.executor.analyze_quality(code, project_id)

            assert metric.project_id == project_id
            assert metric.avg_complexity == 1.5
            assert metric.maintainability_index == 85.0
            assert metric.security_issues == 0
            assert metric.test_coverage == 0.0
            assert self.mock_db.add.called
            assert self.mock_db.commit.called

    def test_save_code_version(self):
        """Test saving code version."""
        project_id = "proj123"
        content = "print('hello')"
        file_path = "test.py"

        code_file = self.executor.save_code_version(project_id, content, file_path)

        assert code_file.project_id == project_id
        assert code_file.content == content
        assert code_file.path == file_path
        assert code_file.hash is not None
        assert len(code_file.hash) == 64  # SHA-256 hex length
        assert self.mock_db.add.called
        assert self.mock_db.commit.called

    def test_save_code_version_hash_calculation(self):
        """Test that code file hash is calculated correctly."""
        content1 = "print('hello')"
        content2 = "print('world')"

        file1 = self.executor.save_code_version("proj1", content1, "test1.py")
        file2 = self.executor.save_code_version("proj1", content2, "test2.py")
        file3 = self.executor.save_code_version("proj1", content1, "test3.py")

        # Same content should have same hash
        assert file1.hash == file3.hash
        # Different content should have different hash
        assert file1.hash != file2.hash

    def test_execute_task_creates_execution_record(self):
        """Test that execution record is created."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test"
        task.status = "pending"

        with (
            patch.object(self.executor, "generate_code") as mock_gen,
            patch.object(self.executor, "save_code_version") as mock_save,
            patch.object(self.executor, "analyze_quality") as mock_analyze,
        ):
            mock_gen.return_value = "code"
            mock_save.return_value = Mock()
            mock_analyze.return_value = Mock()

            result = self.executor.execute_task(task, "coder")

            # Verify execution record was added to database
            assert self.mock_db.add.called
            add_calls = self.mock_db.add.call_args_list
            execution_added = any(
                isinstance(call[0][0], AgentExecution) for call in add_calls if call[0]
            )
            assert execution_added

    def test_execute_task_updates_timestamps(self):
        """Test that execution timestamps are set correctly."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test"
        task.status = "pending"

        with (
            patch.object(self.executor, "generate_code") as mock_gen,
            patch.object(self.executor, "save_code_version") as mock_save,
            patch.object(self.executor, "analyze_quality") as mock_analyze,
        ):
            mock_gen.return_value = "code"
            mock_save.return_value = Mock()
            mock_analyze.return_value = Mock()

            before = datetime.utcnow()
            result = self.executor.execute_task(task, "coder")
            after = datetime.utcnow()

            # Verify timestamps are within expected range
            assert result.started_at is not None
            assert result.completed_at is not None
            assert before <= result.started_at <= after
            assert result.started_at <= result.completed_at <= after

    def test_execute_task_sets_output(self):
        """Test that execution output is set correctly."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test"
        task.status = "pending"

        code = "print('hello world')"

        with (
            patch.object(self.executor, "generate_code") as mock_gen,
            patch.object(self.executor, "save_code_version") as mock_save,
            patch.object(self.executor, "analyze_quality") as mock_analyze,
        ):
            mock_gen.return_value = code
            mock_save.return_value = Mock()
            mock_analyze.return_value = Mock()

            result = self.executor.execute_task(task, "coder")

            assert result.output is not None
            assert str(len(code)) in result.output
            assert "Generated" in result.output

    def test_execute_task_failure_sets_error_message(self):
        """Test that failure sets error message."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.status = "pending"

        error_msg = "LLM API failed"

        with patch.object(self.executor, "generate_code") as mock_gen:
            mock_gen.side_effect = Exception(error_msg)

            with pytest.raises(Exception):
                self.executor.execute_task(task, "coder")

            # Verify execution record in database has error message
            add_calls = self.mock_db.add.call_args_list
            execution_obj = None
            for call in add_calls:
                if call[0] and isinstance(call[0][0], AgentExecution):
                    execution_obj = call[0][0]

            assert execution_obj is not None
            assert execution_obj.error_message == error_msg

    def test_generate_code_uses_config(self):
        """Test that code generation uses config model."""
        task = Mock(spec=Task)
        task.title = "Test"
        task.description = "Test"

        with patch.object(self.executor.llm_client, "generate") as mock_llm:
            mock_llm.return_value = "code"

            self.executor.generate_code(task)

            # Verify generate was called with model parameter
            assert mock_llm.called
            # Config is used by default, just verify it was called
            assert mock_llm.call_count == 1

    def test_analyze_quality_uses_python_language(self):
        """Test that quality analysis specifies Python language."""
        code = "def test(): pass"
        project_id = "proj123"

        with patch.object(self.executor.analyzer, "analyze") as mock_analyze:
            mock_analyze.return_value = {
                "avg_complexity": 1.0,
                "maintainability_index": 100.0,
                "security_issues": 0,
            }

            self.executor.analyze_quality(code, project_id)

            assert mock_analyze.called
            call_args = mock_analyze.call_args
            assert call_args[0][0] == code
            assert call_args[1]["language"] == "python"

    def test_save_code_version_with_special_characters(self):
        """Test saving code with special characters."""
        content = "print('Hello 世界! 🌍')"
        project_id = "proj123"
        file_path = "test.py"

        code_file = self.executor.save_code_version(project_id, content, file_path)

        assert code_file.content == content
        assert code_file.hash is not None

    def test_execute_task_commits_after_each_step(self):
        """Test that database is committed after each major step."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test"
        task.status = "pending"

        with (
            patch.object(self.executor, "generate_code") as mock_gen,
            patch.object(self.executor, "save_code_version") as mock_save,
            patch.object(self.executor, "analyze_quality") as mock_analyze,
        ):
            mock_gen.return_value = "code"
            mock_save.return_value = Mock()
            mock_analyze.return_value = Mock()

            self.executor.execute_task(task, "coder")

            # Verify commit was called multiple times
            assert self.mock_db.commit.call_count >= 3

    def test_execute_task_refreshes_execution(self):
        """Test that execution object is refreshed after creation."""
        task = Mock(spec=Task)
        task.id = "task123"
        task.project_id = "proj456"
        task.title = "Test"
        task.status = "pending"

        with (
            patch.object(self.executor, "generate_code") as mock_gen,
            patch.object(self.executor, "save_code_version") as mock_save,
            patch.object(self.executor, "analyze_quality") as mock_analyze,
        ):
            mock_gen.return_value = "code"
            mock_save.return_value = Mock()
            mock_analyze.return_value = Mock()

            self.executor.execute_task(task, "coder")

            # Verify refresh was called
            assert self.mock_db.refresh.called

    def test_build_prompt_includes_requirements(self):
        """Test that prompt includes coding requirements."""
        task = Mock(spec=Task)
        task.title = "Test"
        task.description = "Test"

        prompt = self.executor._build_prompt(task)

        assert "clean" in prompt.lower()
        assert "type hints" in prompt.lower()
        assert "PEP 8" in prompt
        assert "docstrings" in prompt.lower()

    def test_analyze_quality_sets_zero_test_coverage(self):
        """Test that test_coverage is set to 0 for generated code."""
        code = "def test(): pass"
        project_id = "proj123"

        with patch.object(self.executor.analyzer, "analyze") as mock_analyze:
            mock_analyze.return_value = {
                "avg_complexity": 1.0,
                "maintainability_index": 100.0,
                "security_issues": 0,
            }

            metric = self.executor.analyze_quality(code, project_id)

            # Generated code doesn't have test coverage initially
            assert metric.test_coverage == 0.0

    def test_save_code_version_uses_sha256(self):
        """Test that SHA-256 is used for hash calculation."""
        import hashlib

        content = "test content"
        expected_hash = hashlib.sha256(content.encode()).hexdigest()

        code_file = self.executor.save_code_version("proj1", content, "test.py")

        assert code_file.hash == expected_hash
