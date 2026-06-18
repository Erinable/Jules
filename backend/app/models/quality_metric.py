"""
QualityMetric Entity Model

质量指标实体模型
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class QualityMetric(Base):
    """质量指标实体"""

    __tablename__ = "quality_metrics"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    avg_complexity = Column(Float)  # 平均圈复杂度
    maintainability_index = Column(Float)  # 可维护性指数
    security_issues = Column(Integer)  # 安全问题数量
    test_coverage = Column(Float)  # 测试覆盖率
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    project: "Project" = relationship("Project", back_populates="quality_metrics")

    def __repr__(self) -> str:
        return f"<QualityMetric(id={self.id}, project_id={self.project_id}, measured_at={self.measured_at})>"
