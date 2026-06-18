"""
User Pydantic schemas for request/response validation
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User name")


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str | None = Field(
        None,
        min_length=8,
        max_length=128,
        description="Password (optional, only for auth registration)",
    )
    role: str = Field("viewer", description="User role")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "StrongP@ss1",
                "role": "viewer",
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: EmailStr | None = Field(None, description="User email address")
    name: str | None = Field(None, min_length=1, max_length=255, description="User name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user response"""

    id: UUID = Field(..., description="User unique identifier")
    created_at: datetime = Field(..., description="User creation timestamp")

    model_config = ConfigDict(from_attributes=True)
