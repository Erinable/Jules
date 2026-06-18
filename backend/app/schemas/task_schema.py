"""
Task Pydantic schemas for request/response validation
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """Base task schema with common fields"""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, description="Task description")
    priority: int = Field(0, ge=0, le=10, description="Task priority (0-10)")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    project_id: UUID = Field(..., description="Project ID this task belongs to")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication to the API",
                "priority": 5,
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: str | None = Field(None, min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, description="Task description")
    priority: int | None = Field(None, ge=0, le=10, description="Task priority (0-10)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "priority": 8,
            }
        }
    )


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status"""

    status: str = Field(..., pattern="^(pending|in_progress|completed)$", description="Task status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
            }
        }
    )


class TaskResponse(TaskBase):
    """Schema for task response"""

    id: UUID = Field(..., description="Task unique identifier")
    project_id: UUID = Field(..., description="Project ID")
    status: str = Field(..., description="Task status")
    created_at: datetime = Field(..., description="Task creation timestamp")

    model_config = ConfigDict(from_attributes=True)
