"""
Agent Entity Model

Agent 实体模型（用于存储 Agent 配置信息）
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Agent(Base):
    """Agent 实体"""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(
        String(100), nullable=False, unique=True
    )  # researcher/planner/coder/reviewer/tester
    description = Column(Text)
    config = Column(JSON)  # Agent 配置（JSON 格式）
    is_active = Column(String(10), default="true")  # true/false
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', is_active='{self.is_active}')>"
