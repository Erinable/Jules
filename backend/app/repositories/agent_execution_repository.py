"""
AgentExecution Repository

Agent 执行仓储层，提供 Agent 执行数据访问方法
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecution


class AgentExecutionRepository:
    """Agent 执行仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化 Agent 执行仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(
        self, task_id: uuid.UUID, agent_type: str, state: dict[str, Any] | None = None
    ) -> AgentExecution:
        """
        创建新的 Agent 执行记录

        Args:
            task_id: 任务 ID
            agent_type: Agent 类型
            state: 执行状态（可选）

        Returns:
            AgentExecution: 创建的执行对象
        """
        execution = AgentExecution(
            task_id=task_id,
            agent_type=agent_type,
            state=state or {},
            status="running",
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_by_id(self, execution_id: uuid.UUID) -> AgentExecution | None:
        """
        根据 ID 获取 Agent 执行记录

        Args:
            execution_id: 执行 ID

        Returns:
            Optional[AgentExecution]: 执行对象，不存在则返回 None
        """
        return self.db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()

    def get_by_task(self, task_id: uuid.UUID) -> list[AgentExecution]:
        """
        获取任务的所有执行记录

        Args:
            task_id: 任务 ID

        Returns:
            list[AgentExecution]: 执行记录列表
        """
        return (
            self.db.query(AgentExecution)
            .filter(AgentExecution.task_id == task_id)
            .order_by(AgentExecution.started_at.desc())
            .all()
        )

    def get_all(self, limit: int = 100, offset: int = 0) -> list[AgentExecution]:
        """
        获取所有执行记录（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[AgentExecution]: 执行记录列表
        """
        return (
            self.db.query(AgentExecution)
            .order_by(AgentExecution.started_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_status(
        self, execution_id: uuid.UUID, status: str, state: dict[str, Any] | None = None
    ) -> bool:
        """
        更新执行状态（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            execution_id: 执行 ID
            status: 新状态
            state: 可选的新状态数据

        Returns:
            bool: 操作是否成功
        """
        update_data: dict = {"status": status}
        if state is not None:
            update_data["state"] = state
        if status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow()

        result = (
            self.db.query(AgentExecution)
            .filter(AgentExecution.id == execution_id)
            .update(update_data)
        )
        self.db.commit()
        return result > 0

    def delete(self, execution_id: uuid.UUID) -> bool:
        """
        删除执行记录

        Args:
            execution_id: 执行 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(AgentExecution).filter(AgentExecution.id == execution_id).delete()
        self.db.commit()
        return result > 0
