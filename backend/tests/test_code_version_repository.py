"""
Tests for CodeVersionRepository
"""

import uuid
from datetime import datetime

import pytest
from app.models.code_file import CodeFile
from app.models.project import Project
from app.models.user import User
from app.repositories.code_version_repository import CodeVersionRepository
from sqlalchemy.orm import Session


class TestCodeVersionRepository:
    """Test cases for CodeVersionRepository"""

    @pytest.fixture
    def setup_file(self, db_session: Session) -> CodeFile:
        """Create a test code file"""
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

        file = CodeFile(
            project_id=project.id,
            path="src/main.py",
            content="current content",
            updated_at=datetime.now(),
        )
        db_session.add(file)
        db_session.flush()
        return file

    def test_create_version(self, db_session: Session, setup_file: CodeFile, now: datetime) -> None:
        """Test creating a new version"""
        repo = CodeVersionRepository(db_session)
        version = repo.create(
            file_id=setup_file.id,
            content="version 1 content",
            version_number=1,
            commit_hash="abc123",
        )

        assert version.id is not None
        assert version.file_id == setup_file.id
        assert version.content == "version 1 content"
        assert version.version_number == 1
        assert version.commit_hash == "abc123"

    def test_get_by_id(self, db_session: Session, setup_file: CodeFile, now: datetime) -> None:
        """Test retrieving version by ID"""
        repo = CodeVersionRepository(db_session)
        version = repo.create(
            file_id=setup_file.id,
            content="version content",
            version_number=1,
        )

        retrieved = repo.get_by_id(version.id)
        assert retrieved is not None
        assert retrieved.id == version.id
        assert retrieved.content == version.content

    def test_get_by_id_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test retrieving non-existent version returns None"""
        repo = CodeVersionRepository(db_session)
        version = repo.get_by_id(sample_file_id)
        assert version is None

    def test_get_latest(self, db_session: Session, setup_file: CodeFile, now: datetime) -> None:
        """Test retrieving latest version"""
        repo = CodeVersionRepository(db_session)
        repo.create(
            file_id=setup_file.id,
            content="version 1",
            version_number=1,
        )
        repo.create(
            file_id=setup_file.id,
            content="version 2",
            version_number=2,
        )
        latest = repo.create(
            file_id=setup_file.id,
            content="version 3",
            version_number=3,
        )

        retrieved = repo.get_latest(setup_file.id)
        assert retrieved is not None
        assert retrieved.id == latest.id
        assert retrieved.version_number == 3

    def test_get_latest_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test retrieving latest version for non-existent file returns None"""
        repo = CodeVersionRepository(db_session)
        version = repo.get_latest(sample_file_id)
        assert version is None

    def test_get_history(self, db_session: Session, setup_file: CodeFile, now: datetime) -> None:
        """Test retrieving version history"""
        repo = CodeVersionRepository(db_session)
        repo.create(
            file_id=setup_file.id,
            content="version 1",
            version_number=1,
        )
        repo.create(
            file_id=setup_file.id,
            content="version 2",
            version_number=2,
        )
        repo.create(
            file_id=setup_file.id,
            content="version 3",
            version_number=3,
        )

        history = repo.get_history(setup_file.id)
        assert len(history) == 3
        assert history[0].version_number == 3
        assert history[1].version_number == 2
        assert history[2].version_number == 1

    def test_get_history_with_limit(
        self, db_session: Session, setup_file: CodeFile, now: datetime
    ) -> None:
        """Test retrieving version history with limit"""
        repo = CodeVersionRepository(db_session)
        repo.create(
            file_id=setup_file.id,
            content="version 1",
            version_number=1,
        )
        repo.create(
            file_id=setup_file.id,
            content="version 2",
            version_number=2,
        )
        repo.create(
            file_id=setup_file.id,
            content="version 3",
            version_number=3,
        )

        history = repo.get_history(setup_file.id, limit=2)
        assert len(history) == 2
        assert history[0].version_number == 3
        assert history[1].version_number == 2

    def test_get_by_version_number(
        self, db_session: Session, setup_file: CodeFile, now: datetime
    ) -> None:
        """Test retrieving version by version number"""
        repo = CodeVersionRepository(db_session)
        repo.create(
            file_id=setup_file.id,
            content="version 1",
            version_number=1,
        )
        v2 = repo.create(
            file_id=setup_file.id,
            content="version 2",
            version_number=2,
        )

        retrieved = repo.get_by_version_number(setup_file.id, 2)
        assert retrieved is not None
        assert retrieved.id == v2.id
        assert retrieved.version_number == 2

    def test_get_by_version_number_not_found(
        self, db_session: Session, setup_file: CodeFile
    ) -> None:
        """Test retrieving non-existent version number returns None"""
        repo = CodeVersionRepository(db_session)
        version = repo.get_by_version_number(setup_file.id, 999)
        assert version is None

    def test_delete(self, db_session: Session, setup_file: CodeFile, now: datetime) -> None:
        """Test deleting version"""
        repo = CodeVersionRepository(db_session)
        version = repo.create(
            file_id=setup_file.id,
            content="version 1",
            version_number=1,
        )

        result = repo.delete(version.id)
        assert result is True

        deleted_version = repo.get_by_id(version.id)
        assert deleted_version is None

    def test_delete_not_found(self, db_session: Session, sample_file_id: uuid.UUID) -> None:
        """Test deleting non-existent version returns False"""
        repo = CodeVersionRepository(db_session)
        result = repo.delete(sample_file_id)
        assert result is False
