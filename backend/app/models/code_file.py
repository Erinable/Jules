"""
CodeFile Entity Model

代码文件实体模型
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.code_version import CodeVersion
    from app.models.project import Project


class CodeFile(Base):
    """代码文件实体"""

    __tablename__ = "code_files"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    path = Column(String(500), nullable=False)
    content = Column(Text)
    hash = Column(String(64), index=True)  # SHA256
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    project: "Project" = relationship("Project", back_populates="code_files")
    versions: list["CodeVersion"] = relationship(
        "CodeVersion", back_populates="file", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CodeFile(id={self.id}, path='{self.path}', hash='{self.hash}')>"
