"""
Task Repository

任务仓储层，提供任务数据访问方法
"""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    """任务仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化任务仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(
        self, project_id: uuid.UUID, title: str, description: str, priority: int = 0
    ) -> Task:
        """
        创建新任务

        Args:
            project_id: 项目 ID
            title: 任务标题
            description: 任务描述
            priority: 优先级（默认 0）

        Returns:
            Task: 创建的任务对象
        """
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            status="pending",
            priority=priority,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        """
        根据 ID 获取任务

        Args:
            task_id: 任务 ID

        Returns:
            Optional[Task]: 任务对象，不存在则返回 None
        """
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_project(self, project_id: uuid.UUID) -> list[Task]:
        """
        获取项目的所有任务

        Args:
            project_id: 项目 ID

        Returns:
            list[Task]: 任务列表
        """
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
            .all()
        )

    def get_by_status(self, project_id: uuid.UUID, status: str) -> list[Task]:
        """
        获取项目中指定状态的任务

        Args:
            project_id: 项目 ID
            status: 任务状态

        Returns:
            list[Task]: 任务列表
        """
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.status == status)
            .order_by(Task.priority.desc(), Task.created_at.asc())
            .all()
        )

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Task]:
        """
        获取所有任务（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[Task]: 任务列表
        """
        return (
            self.db.query(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset).all()
        )

    def update_status(self, task_id: uuid.UUID, status: str) -> bool:
        """
        更新任务状态（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            task_id: 任务 ID
            status: 新状态

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(Task).filter(Task.id == task_id).update({"status": status})
        self.db.commit()
        return result > 0

    def update(
        self,
        task_id: uuid.UUID,
        title: str | None = None,
        description: str | None = None,
        priority: int | None = None,
    ) -> bool:
        """
        更新任务字段（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            task_id: 任务 ID
            title: 新标题（可选）
            description: 新描述（可选）
            priority: 新优先级（可选）

        Returns:
            bool: 操作是否成功
        """
        update_data: dict[str, Any] = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            update_data["priority"] = priority

        if not update_data:
            return False

        result = self.db.query(Task).filter(Task.id == task_id).update(update_data)
        self.db.commit()
        return result > 0

    def delete(self, task_id: uuid.UUID) -> bool:
        """
        删除任务

        Args:
            task_id: 任务 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(Task).filter(Task.id == task_id).delete()
        self.db.commit()
        return result > 0
