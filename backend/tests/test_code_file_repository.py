"""
Tests for CodeFileRepository
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.code_file_repository import CodeFileRepository


class TestCodeFileRepository:
    """Test cases for CodeFileRepository"""

    @pytest.fixture
    def setup_project(self, db_session: Session) -> Project:
        """Create a test project"""
        user = User(email="test@example.com", name="Test User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="Test Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.flush()
        return project

    def test_create_file(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test creating a new code file"""
        repo = CodeFileRepository(db_session)
        file = repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="print('hello')",
            file_hash="abc123",
        )

        assert file.id is not None
        assert file.project_id == setup_project.id
        assert file.path == "src/main.py"
        assert file.content == "print('hello')"
        assert file.hash == "abc123"

    def test_get_by_id(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test retrieving file by ID"""
        repo = CodeFileRepository(db_session)
        file = repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="print('hello')",
            file_hash="abc123",
        )

        retrieved = repo.get_by_id(file.id)
        assert retrieved is not None
        assert retrieved.id == file.id
        assert retrieved.path == file.path

    def test_get_by_id_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test retrieving non-existent file returns None"""
        repo = CodeFileRepository(db_session)
        file = repo.get_by_id(sample_file_id)
        assert file is None

    def test_get_by_path(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test retrieving file by project and path"""
        repo = CodeFileRepository(db_session)
        file = repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="print('hello')",
            file_hash="abc123",
        )

        retrieved = repo.get_by_path(setup_project.id, "src/main.py")
        assert retrieved is not None
        assert retrieved.id == file.id
        assert retrieved.path == "src/main.py"

    def test_get_by_path_not_found(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving non-existent path returns None"""
        repo = CodeFileRepository(db_session)
        file = repo.get_by_path(setup_project.id, "nonexistent.py")
        assert file is None

    def test_list_by_project(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test listing files by project"""
        repo = CodeFileRepository(db_session)
        repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="main",
            file_hash="hash1",
        )
        repo.create(
            project_id=setup_project.id,
            path="src/utils.py",
            content="utils",
            file_hash="hash2",
        )

        files = repo.list_by_project(setup_project.id)
        assert len(files) == 2
        assert all(f.project_id == setup_project.id for f in files)

    def test_update_content(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test updating file content"""
        repo = CodeFileRepository(db_session)
        file = repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="original",
            file_hash="hash1",
        )

        result = repo.update_content(file.id, content="updated", file_hash="hash2")
        assert result is True

        updated_file = repo.get_by_id(file.id)
        assert updated_file is not None
        assert updated_file.content == "updated"
        assert updated_file.hash == "hash2"
        assert updated_file.updated_at > now

    def test_update_content_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test updating non-existent file returns False"""
        repo = CodeFileRepository(db_session)
        result = repo.update_content(sample_file_id, content="updated", file_hash="hash2")
        assert result is False

    def test_delete(self, db_session: Session, setup_project: Project, now: datetime) -> None:
        """Test deleting file"""
        repo = CodeFileRepository(db_session)
        file = repo.create(
            project_id=setup_project.id,
            path="src/main.py",
            content="content",
            file_hash="hash1",
        )

        result = repo.delete(file.id)
        assert result is True

        deleted_file = repo.get_by_id(file.id)
        assert deleted_file is None

    def test_delete_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test deleting non-existent file returns False"""
        repo = CodeFileRepository(db_session)
        result = repo.delete(sample_file_id)
        assert result is False
