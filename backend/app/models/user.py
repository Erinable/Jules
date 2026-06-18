"""
User Entity Model

用户实体模型（含认证授权字段）
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class User(Base):
    """用户实体"""

    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    # 认证字段
    password_hash = Column(String(255), nullable=True, comment="bcrypt 哈希")
    role = Column(String(20), nullable=False, default="viewer", index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_login_at = Column(DateTime, nullable=True)

    # 关系
    projects: list["Project"] = relationship("Project", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def has_role(self, required_role: str) -> bool:
        """检查用户角色是否满足要求"""
        role_hierarchy = {"viewer": 1, "developer": 2, "admin": 3}
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
