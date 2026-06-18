"""
AgentExecution Entity Model

Agent 执行实体模型
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.llm_call import LLMCall
    from app.models.task import Task


class AgentExecution(Base):
    """Agent 执行实体"""

    __tablename__ = "agent_executions"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)  # researcher/planner/coder/reviewer/tester
    state = Column(JSON)  # Agent 执行状态（JSON 格式）
    status = Column(
        String(50), default="running", nullable=False, index=True
    )  # running/completed/failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime)
    output = Column(String(1000))  # Execution output/result
    error_message = Column(String(1000))  # Error message if failed

    # 关系
    task: "Task" = relationship("Task", back_populates="executions")
    llm_calls: list["LLMCall"] = relationship(
        "LLMCall", back_populates="execution", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AgentExecution(id={self.id}, agent_type='{self.agent_type}', status='{self.status}')>"
