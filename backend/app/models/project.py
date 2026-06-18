"""
Project Entity Model

项目实体模型
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile
    from app.models.quality_metric import QualityMetric
    from app.models.task import Task
    from app.models.user import User


class Project(Base):
    """项目实体"""

    __tablename__ = "projects"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(50))  # web/cli/data
    config = Column(JSON)
    status = Column(
        String(50), default="pending", index=True
    )  # pending/in_progress/completed/failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    user: "User" = relationship("User", back_populates="projects")
    tasks: list["Task"] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )
    code_files: list["CodeFile"] = relationship(
        "CodeFile", back_populates="project", cascade="all, delete-orphan"
    )
    quality_metrics: list["QualityMetric"] = relationship(
        "QualityMetric", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
