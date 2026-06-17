"""
User Repository

用户仓储层，提供用户数据访问方法
"""
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """用户仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化用户仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(self, email: str, name: str) -> User:
        """
        创建新用户

        Args:
            email: 用户邮箱
            name: 用户名称

        Returns:
            User: 创建的用户对象
        """
        user = User(email=email, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        根据 ID 获取用户

        Args:
            user_id: 用户 ID

        Returns:
            Optional[User]: 用户对象，不存在则返回 None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 用户邮箱

        Returns:
            Optional[User]: 用户对象，不存在则返回 None
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        获取所有用户（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[User]: 用户列表
        """
        return self.db.query(User).order_by(User.created_at.desc()).limit(limit).offset(offset).all()

    def update(self, user_id: uuid.UUID, name: str) -> bool:
        """
        更新用户信息（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            user_id: 用户 ID
            name: 新的用户名称

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(User).filter(User.id == user_id).update({"name": name})
        self.db.commit()
        return result > 0

    def delete(self, user_id: uuid.UUID) -> bool:
        """
        删除用户

        Args:
            user_id: 用户 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(User).filter(User.id == user_id).delete()
        self.db.commit()
        return result > 0
