"""
User API routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Create a new user

    Args:
        user: User creation data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: 400 if email already exists
    """
    repo = UserRepository(db)

    # Check if email already exists
    existing = repo.get_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists",
        )

    created = repo.create(email=user.email, name=user.name)
    return UserResponse.model_validate(created)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserResponse:
    """
    Get user by ID

    Args:
        user_id: User unique identifier
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: 404 if user not found
    """
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return UserResponse.model_validate(user)


@router.get("/", response_model=list[UserResponse])
def list_users(
    pagination: dict = Depends(get_pagination), db: Session = Depends(get_db)
) -> list[UserResponse]:
    """
    List all users with pagination

    Args:
        pagination: Pagination parameters (limit, offset)
        db: Database session

    Returns:
        List of users
    """
    repo = UserRepository(db)
    users = repo.get_all(limit=pagination["limit"], offset=pagination["offset"])
    return [UserResponse.model_validate(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Update user

    Args:
        user_id: User unique identifier
        user: User update data
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: 404 if user not found, 400 if email already exists
    """
    repo = UserRepository(db)

    # Check if user exists
    existing = repo.get_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    # Update user (email is immutable, only update name)
    success = repo.update(user_id, name=user.name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )

    # Fetch updated user
    updated = repo.get_by_id(user_id)
    return UserResponse.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete user

    Args:
        user_id: User unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    repo = UserRepository(db)
    success = repo.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
