"""
Agent Execution Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExecutionCreate(BaseModel):
    """Schema for creating a new agent execution"""

    task_id: UUID = Field(..., description="Task ID this execution belongs to")
    agent_type: str = Field(..., min_length=1, max_length=50, description="Type of agent")
    state: dict[str, Any] | None = Field(None, description="Execution state")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_type": "code_generator",
                "state": {"step": 1, "progress": 0.2},
            }
        }
    )


class ExecutionStatusUpdate(BaseModel):
    """Schema for updating execution status"""

    status: str = Field(..., pattern="^(running|completed|failed)$", description="Execution status")
    state: dict[str, Any] | None = Field(None, description="Execution state")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "state": {"step": 3, "progress": 1.0, "result": "success"},
            }
        }
    )


class ExecutionResponse(BaseModel):
    """Schema for agent execution response"""

    id: UUID = Field(..., description="Execution unique identifier")
    task_id: UUID = Field(..., description="Task ID")
    agent_type: str = Field(..., description="Type of agent")
    state: dict[str, Any] | None = Field(None, description="Execution state")
    status: str = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Execution start timestamp")
    completed_at: datetime | None = Field(None, description="Execution completion timestamp")

    model_config = ConfigDict(from_attributes=True)
