"""
Tests for UserRepository
"""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


class TestUserRepository:
    """Test cases for UserRepository"""

    def test_create_user(self, db_session: Session, unique_email: str, now: datetime) -> None:
        """Test creating a new user"""
        repo = UserRepository(db_session)
        user = repo.create(email=unique_email, name="Test User")

        assert user.id is not None
        assert user.email == unique_email
        assert user.name == "Test User"
        assert user.created_at is not None

    def test_get_by_id(self, db_session: Session, unique_email: str) -> None:
        """Test retrieving user by ID"""
        repo = UserRepository(db_session)
        user = repo.create(email=unique_email, name="Test User")

        retrieved = repo.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email

    def test_get_by_id_not_found(self, db_session: Session, sample_user_id: uuid.UUID) -> None:
        """Test retrieving non-existent user returns None"""
        repo = UserRepository(db_session)
        user = repo.get_by_id(sample_user_id)
        assert user is None

    def test_get_by_email(self, db_session: Session, unique_email: str) -> None:
        """Test retrieving user by email"""
        repo = UserRepository(db_session)
        user = repo.create(email=unique_email, name="Test User")

        retrieved = repo.get_by_email(unique_email)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == unique_email

    def test_get_by_email_not_found(self, db_session: Session) -> None:
        """Test retrieving non-existent email returns None"""
        repo = UserRepository(db_session)
        user = repo.get_by_email("nonexistent@example.com")
        assert user is None

    def test_get_all(self, db_session: Session) -> None:
        """Test retrieving all users with pagination"""
        repo = UserRepository(db_session)
        repo.create(email=f"user1-{uuid.uuid4().hex[:8]}@example.com", name="User 1")
        repo.create(email=f"user2-{uuid.uuid4().hex[:8]}@example.com", name="User 2")
        repo.create(email=f"user3-{uuid.uuid4().hex[:8]}@example.com", name="User 3")

        users = repo.get_all(limit=2, offset=0)
        assert len(users) >= 2

        users_all = repo.get_all(limit=100, offset=0)
        assert len(users_all) >= 3

    def test_update(self, db_session: Session, unique_email: str) -> None:
        """Test updating user name"""
        repo = UserRepository(db_session)
        user = repo.create(email=unique_email, name="Original Name")

        result = repo.update(user.id, name="Updated Name")
        assert result is True

        updated_user = repo.get_by_id(user.id)
        assert updated_user is not None
        assert updated_user.name == "Updated Name"

    def test_update_not_found(self, db_session: Session, sample_user_id: uuid.UUID) -> None:
        """Test updating non-existent user returns False"""
        repo = UserRepository(db_session)
        result = repo.update(sample_user_id, name="Updated Name")
        assert result is False

    def test_delete(self, db_session: Session, unique_email: str) -> None:
        """Test deleting user"""
        repo = UserRepository(db_session)
        user = repo.create(email=unique_email, name="Test User")

        result = repo.delete(user.id)
        assert result is True

        deleted_user = repo.get_by_id(user.id)
        assert deleted_user is None

    def test_delete_not_found(self, db_session: Session, sample_user_id: uuid.UUID) -> None:
        """Test deleting non-existent user returns False"""
        repo = UserRepository(db_session)
        result = repo.delete(sample_user_id)
        assert result is False
