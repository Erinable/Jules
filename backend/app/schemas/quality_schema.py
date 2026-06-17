"""
Quality Metric Pydantic schemas for request/response validation
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QualityMetricCreate(BaseModel):
    """Schema for creating a new quality metric"""

    project_id: UUID = Field(..., description="Project ID this metric belongs to")
    avg_complexity: float = Field(..., ge=0, description="Average cyclomatic complexity")
    maintainability_index: float = Field(0.0, ge=0, le=100, description="Maintainability index (0-100)")
    security_issues: int = Field(0, ge=0, description="Number of security issues")
    test_coverage: float = Field(0.0, ge=0, le=100, description="Test coverage percentage (0-100)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "avg_complexity": 5.2,
                "maintainability_index": 75.5,
                "security_issues": 2,
                "test_coverage": 85.0,
            }
        }
    )


class QualityMetricResponse(BaseModel):
    """Schema for quality metric response"""

    id: UUID = Field(..., description="Metric unique identifier")
    project_id: UUID = Field(..., description="Project ID")
    avg_complexity: float = Field(..., description="Average cyclomatic complexity")
    maintainability_index: float = Field(..., description="Maintainability index")
    security_issues: int = Field(..., description="Number of security issues")
    test_coverage: float = Field(..., description="Test coverage percentage")
    measured_at: datetime = Field(..., description="Measurement timestamp")

    model_config = ConfigDict(from_attributes=True)
