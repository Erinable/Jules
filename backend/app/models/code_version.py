"""
CodeVersion Entity Model

代码版本实体模型
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile


class CodeVersion(Base):
    """代码版本实体"""

    __tablename__ = "code_versions"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("code_files.id"), nullable=False, index=True)
    content = Column(Text)
    version_number = Column(Integer, nullable=False)
    commit_hash = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    file: "CodeFile" = relationship("CodeFile", back_populates="versions")

    def __repr__(self) -> str:
        return f"<CodeVersion(id={self.id}, file_id={self.file_id}, version={self.version_number})>"
