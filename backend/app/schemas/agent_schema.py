"""
Agent Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    """Base agent schema with common fields"""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    config: dict[str, Any] = Field(default_factory=dict, description="Agent configuration")


class AgentCreate(AgentBase):
    """Schema for creating a new agent"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "code-generator",
                "description": "Generates code based on requirements",
                "config": {"model": "gpt-4", "temperature": 0.7},
            }
        }
    )


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""

    description: str | None = Field(None, description="Agent description")
    config: dict[str, Any] | None = Field(None, description="Agent configuration")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "config": {"model": "gpt-4", "temperature": 0.5},
            }
        }
    )


class AgentResponse(AgentBase):
    """Schema for agent response"""

    id: UUID = Field(..., description="Agent unique identifier")
    is_active: str = Field(..., description="Agent active status")
    created_at: datetime = Field(..., description="Agent creation timestamp")

    model_config = ConfigDict(from_attributes=True)
