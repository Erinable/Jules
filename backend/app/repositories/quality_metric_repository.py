"""
QualityMetric Repository

质量指标仓储层，提供质量指标数据访问方法
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.quality_metric import QualityMetric


class QualityMetricRepository:
    """质量指标仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化质量指标仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(
        self,
        project_id: uuid.UUID,
        avg_complexity: float,
        maintainability_index: float = 0.0,
        security_issues: int = 0,
        test_coverage: float = 0.0,
        measured_at: Optional[datetime] = None,
    ) -> QualityMetric:
        """
        创建新的质量指标记录

        Args:
            project_id: 项目 ID
            avg_complexity: 平均圈复杂度
            maintainability_index: 可维护性指数（默认 0.0）
            security_issues: 安全问题数量（默认 0）
            test_coverage: 测试覆盖率（默认 0.0）
            measured_at: 测量时间（可选，默认为当前时间）

        Returns:
            QualityMetric: 创建的质量指标对象
        """
        metric = QualityMetric(
            project_id=project_id,
            avg_complexity=avg_complexity,
            maintainability_index=maintainability_index,
            security_issues=security_issues,
            test_coverage=test_coverage,
            measured_at=measured_at if measured_at is not None else datetime.utcnow(),
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_by_id(self, metric_id: uuid.UUID) -> Optional[QualityMetric]:
        """
        根据 ID 获取质量指标

        Args:
            metric_id: 指标 ID

        Returns:
            Optional[QualityMetric]: 质量指标对象，不存在则返回 None
        """
        return self.db.query(QualityMetric).filter(QualityMetric.id == metric_id).first()

    def get_latest(self, project_id: uuid.UUID) -> Optional[QualityMetric]:
        """
        获取项目的最新质量指标

        Args:
            project_id: 项目 ID

        Returns:
            Optional[QualityMetric]: 最新质量指标对象，不存在则返回 None
        """
        return self.db.query(QualityMetric).filter(QualityMetric.project_id == project_id).order_by(QualityMetric.measured_at.desc()).first()

    def get_history(self, project_id: uuid.UUID, limit: int = 10) -> list[QualityMetric]:
        """
        获取项目的质量指标历史

        Args:
            project_id: 项目 ID
            limit: 返回数量限制

        Returns:
            list[QualityMetric]: 质量指标历史列表
        """
        return self.db.query(QualityMetric).filter(QualityMetric.project_id == project_id).order_by(QualityMetric.measured_at.desc()).limit(limit).all()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[QualityMetric]:
        """
        获取所有质量指标（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[QualityMetric]: 质量指标列表
        """
        return self.db.query(QualityMetric).order_by(QualityMetric.measured_at.desc()).limit(limit).offset(offset).all()

    def delete(self, metric_id: uuid.UUID) -> bool:
        """
        删除质量指标记录

        Args:
            metric_id: 指标 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(QualityMetric).filter(QualityMetric.id == metric_id).delete()
        self.db.commit()
        return result > 0
