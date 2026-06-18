"""
Code File Pydantic schemas for request/response validation
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CodeFileBase(BaseModel):
    """Base code file schema with common fields"""

    path: str = Field(..., min_length=1, max_length=500, description="File path")
    content: str = Field(..., description="File content")


class CodeFileCreate(CodeFileBase):
    """Schema for creating a new code file"""

    project_id: UUID = Field(..., description="Project ID this file belongs to")
    file_hash: str = Field(..., min_length=1, max_length=64, description="File hash")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "path": "src/main.py",
                "content": "print('Hello, World!')",
                "file_hash": "abc123def456",
            }
        }
    )


class CodeFileUpdate(BaseModel):
    """Schema for updating a code file"""

    content: str = Field(..., description="File content")
    file_hash: str = Field(..., min_length=1, max_length=64, description="File hash")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "print('Hello, Jules!')",
                "file_hash": "xyz789abc012",
            }
        }
    )


class CodeFileResponse(CodeFileBase):
    """Schema for code file response"""

    id: UUID = Field(..., description="File unique identifier")
    project_id: UUID = Field(..., description="Project ID")
    hash: str = Field(..., description="File hash")
    updated_at: datetime = Field(..., description="File last update timestamp")

    model_config = ConfigDict(from_attributes=True)
