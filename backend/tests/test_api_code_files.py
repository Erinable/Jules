"""
Integration tests for Code File API endpoints
"""

from datetime import datetime

import pytest
from app.main import app
from app.models.code_file import CodeFile
from app.models.project import Project
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

client = TestClient(app)


class TestCodeFileAPI:
    """Test cases for Code File API endpoints"""

    @pytest.fixture
    def setup_project(self, db_session: Session) -> Project:
        """Create a test project"""
        user = User(email="file@example.com", name="File User", created_at=datetime.now())
        db_session.add(user)
        db_session.flush()

        project = Project(
            user_id=user.id,
            name="File Project",
            type="web",
            status="active",
            created_at=datetime.now(),
        )
        db_session.add(project)
        db_session.commit()
        return project

    def test_create_code_file(self, db_session: Session, setup_project: Project) -> None:
        """Test creating a new code file"""
        response = client.post(
            "/api/v1/code-files/",
            json={
                "project_id": str(setup_project.id),
                "path": "src/main.py",
                "content": "print('Hello')",
                "file_hash": "abc123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["path"] == "src/main.py"
        assert data["hash"] == "abc123"

    def test_create_code_file_duplicate_path(
        self, db_session: Session, setup_project: Project
    ) -> None:
        """Test creating code file with duplicate path fails"""
        code_file = CodeFile(
            project_id=setup_project.id,
            path="src/duplicate.py",
            content="content",
            hash="hash1",
            updated_at=datetime.now(),
        )
        db_session.add(code_file)
        db_session.commit()

        response = client.post(
            "/api/v1/code-files/",
            json={
                "project_id": str(setup_project.id),
                "path": "src/duplicate.py",
                "content": "new content",
                "file_hash": "hash2",
            },
        )
        assert response.status_code == 400

    def test_get_code_file(self, db_session: Session, setup_project: Project) -> None:
        """Test retrieving code file by ID"""
        code_file = CodeFile(
            project_id=setup_project.id,
            path="src/test.py",
            content="test content",
            hash="hash123",
            updated_at=datetime.now(),
        )
        db_session.add(code_file)
        db_session.commit()

        response = client.get(f"/api/v1/code-files/{code_file.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "src/test.py"
        assert data["content"] == "test content"

    def test_get_code_file_not_found(self, db_session: Session, sample_code_file_id) -> None:
        """Test retrieving non-existent code file returns 404"""
        response = client.get(f"/api/v1/code-files/{sample_code_file_id}")
        assert response.status_code == 404

    def test_list_code_files_by_project(self, db_session: Session, setup_project: Project) -> None:
        """Test listing code files filtered by project"""
        for i in range(3):
            code_file = CodeFile(
                project_id=setup_project.id,
                path=f"src/project_file{i}.py",
                content=f"content {i}",
                hash=f"hash{i}",
                updated_at=datetime.now(),
            )
            db_session.add(code_file)
        db_session.commit()

        response = client.get(f"/api/v1/code-files/project/{setup_project.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(f["project_id"] == str(setup_project.id) for f in data)

    def test_update_code_file(self, db_session: Session, setup_project: Project) -> None:
        """Test updating code file"""
        code_file = CodeFile(
            project_id=setup_project.id,
            path="src/update.py",
            content="original content",
            hash="original_hash",
            updated_at=datetime.now(),
        )
        db_session.add(code_file)
        db_session.commit()

        response = client.put(
            f"/api/v1/code-files/{code_file.id}",
            json={
                "content": "updated content",
                "file_hash": "updated_hash",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "updated content"
        assert data["hash"] == "updated_hash"

    def test_update_code_file_not_found(self, db_session: Session, sample_code_file_id) -> None:
        """Test updating non-existent code file returns 404"""
        response = client.put(
            f"/api/v1/code-files/{sample_code_file_id}",
            json={"content": "new content", "file_hash": "newhash"},
        )
        assert response.status_code == 404

    def test_delete_code_file(self, db_session: Session, setup_project: Project) -> None:
        """Test deleting code file"""
        code_file = CodeFile(
            project_id=setup_project.id,
            path="src/delete.py",
            content="content",
            hash="hash",
            updated_at=datetime.now(),
        )
        db_session.add(code_file)
        db_session.commit()

        response = client.delete(f"/api/v1/code-files/{code_file.id}")
        assert response.status_code == 204

    def test_delete_code_file_not_found(self, db_session: Session, sample_code_file_id) -> None:
        """Test deleting non-existent code file returns 404"""
        response = client.delete(f"/api/v1/code-files/{sample_code_file_id}")
        assert response.status_code == 404
