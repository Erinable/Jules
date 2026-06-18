"""
Agent Repository

Agent 仓储层，提供 Agent 数据访问方法
"""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent import Agent


class AgentRepository:
    """Agent 仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化 Agent 仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(self, name: str, description: str, config: dict[str, Any]) -> Agent:
        """
        创建新的 Agent

        Args:
            name: Agent 名称
            description: Agent 描述
            config: Agent 配置

        Returns:
            Agent: 创建的 Agent 对象
        """
        agent = Agent(name=name, description=description, config=config, is_active="true")
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_by_id(self, agent_id: uuid.UUID) -> Agent | None:
        """
        根据 ID 获取 Agent

        Args:
            agent_id: Agent ID

        Returns:
            Optional[Agent]: Agent 对象，不存在则返回 None
        """
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def get_by_name(self, name: str) -> Agent | None:
        """
        根据名称获取 Agent

        Args:
            name: Agent 名称

        Returns:
            Optional[Agent]: Agent 对象，不存在则返回 None
        """
        return self.db.query(Agent).filter(Agent.name == name).first()

    def get_all_active(self) -> list[Agent]:
        """
        获取所有活跃的 Agent

        Returns:
            list[Agent]: 活跃的 Agent 列表
        """
        return self.db.query(Agent).filter(Agent.is_active == "true").order_by(Agent.name).all()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Agent]:
        """
        获取所有 Agent（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[Agent]: Agent 列表
        """
        return self.db.query(Agent).order_by(Agent.name).limit(limit).offset(offset).all()

    def update(
        self,
        agent_id: uuid.UUID,
        description: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> bool:
        """
        更新 Agent 信息（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            agent_id: Agent ID
            description: 新的描述（可选）
            config: 新的配置（可选）

        Returns:
            bool: 操作是否成功
        """
        update_data: dict = {}
        if description is not None:
            update_data["description"] = description
        if config is not None:
            update_data["config"] = config

        if not update_data:
            return False

        result = self.db.query(Agent).filter(Agent.id == agent_id).update(update_data)
        self.db.commit()
        return result > 0

    def delete(self, agent_id: uuid.UUID) -> bool:
        """
        删除 Agent

        Args:
            agent_id: Agent ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(Agent).filter(Agent.id == agent_id).delete()
        self.db.commit()
        return result > 0
