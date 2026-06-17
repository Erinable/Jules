"""
Integration tests for User API endpoints
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User

client = TestClient(app)


class TestUserAPI:
    """Test cases for User API endpoints"""

    def test_create_user(self, db_session: Session) -> None:
        """Test creating a new user"""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_email(self, db_session: Session) -> None:
        """Test creating user with duplicate email fails"""
        user = User(email="duplicate@example.com", name="User 1", created_at=datetime.now())
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/v1/users/",
            json={
                "email": "duplicate@example.com",
                "name": "User 2",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_user(self, db_session: Session) -> None:
        """Test retrieving user by ID"""
        user = User(email="get@example.com", name="Get User", created_at=datetime.now())
        db_session.add(user)
        db_session.commit()

        response = client.get(f"/api/v1/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["email"] == "get@example.com"
        assert data["name"] == "Get User"

    def test_get_user_not_found(self, db_session: Session, sample_user_id) -> None:
        """Test retrieving non-existent user returns 404"""
        response = client.get(f"/api/v1/users/{sample_user_id}")
        assert response.status_code == 404

    def test_list_users(self, db_session: Session) -> None:
        """Test listing users with pagination"""
        for i in range(5):
            user = User(email=f"list{i}@example.com", name=f"User {i}", created_at=datetime.now())
            db_session.add(user)
        db_session.commit()

        response = client.get("/api/v1/users/?limit=3&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_update_user(self, db_session: Session) -> None:
        """Test updating user"""
        user = User(email="update@example.com", name="Original Name", created_at=datetime.now())
        db_session.add(user)
        db_session.commit()

        response = client.put(
            f"/api/v1/users/{user.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_user_not_found(self, db_session: Session, sample_user_id) -> None:
        """Test updating non-existent user returns 404"""
        response = client.put(
            f"/api/v1/users/{sample_user_id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 404

    def test_delete_user(self, db_session: Session) -> None:
        """Test deleting user"""
        user = User(email="delete@example.com", name="Delete User", created_at=datetime.now())
        db_session.add(user)
        db_session.commit()

        response = client.delete(f"/api/v1/users/{user.id}")
        assert response.status_code == 204

    def test_delete_user_not_found(self, db_session: Session, sample_user_id) -> None:
        """Test deleting non-existent user returns 404"""
        response = client.delete(f"/api/v1/users/{sample_user_id}")
        assert response.status_code == 404
