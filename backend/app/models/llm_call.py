"""
LLMCall Entity Model

LLM 调用实体模型
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.agent_execution import AgentExecution


class LLMCall(Base):
    """LLM 调用实体"""

    __tablename__ = "llm_calls"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("agent_executions.id"), nullable=False, index=True)
    model = Column(String(100), nullable=False)  # claude-opus-4-7/gpt-4o
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    cost = Column(Integer)  # 成本（以美分为单位）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    execution: "AgentExecution" = relationship("AgentExecution", back_populates="llm_calls")

    def __repr__(self) -> str:
        return f"<LLMCall(id={self.id}, model='{self.model}', tokens={self.prompt_tokens + self.completion_tokens})>"
