"""
CodeVersion Repository

代码版本仓储层，提供代码版本数据访问方法
"""

import uuid

from sqlalchemy.orm import Session

from app.models.code_version import CodeVersion


class CodeVersionRepository:
    """代码版本仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化代码版本仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(
        self, file_id: uuid.UUID, content: str, version_number: int, commit_hash: str | None = None
    ) -> CodeVersion:
        """
        创建新的代码版本记录

        Args:
            file_id: 文件 ID
            content: 版本内容
            version_number: 版本号
            commit_hash: 提交哈希值（可选）

        Returns:
            CodeVersion: 创建的版本对象
        """
        version = CodeVersion(
            file_id=file_id, content=content, version_number=version_number, commit_hash=commit_hash
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_by_id(self, version_id: uuid.UUID) -> CodeVersion | None:
        """
        根据 ID 获取代码版本

        Args:
            version_id: 版本 ID

        Returns:
            Optional[CodeVersion]: 版本对象，不存在则返回 None
        """
        return self.db.query(CodeVersion).filter(CodeVersion.id == version_id).first()

    def get_latest(self, file_id: uuid.UUID) -> CodeVersion | None:
        """
        获取文件的最新版本

        Args:
            file_id: 文件 ID

        Returns:
            Optional[CodeVersion]: 最新版本对象，不存在则返回 None
        """
        return (
            self.db.query(CodeVersion)
            .filter(CodeVersion.file_id == file_id)
            .order_by(CodeVersion.version_number.desc())
            .first()
        )

    def get_history(self, file_id: uuid.UUID, limit: int = 10) -> list[CodeVersion]:
        """
        获取文件的版本历史

        Args:
            file_id: 文件 ID
            limit: 返回数量限制

        Returns:
            list[CodeVersion]: 版本历史列表
        """
        return (
            self.db.query(CodeVersion)
            .filter(CodeVersion.file_id == file_id)
            .order_by(CodeVersion.version_number.desc())
            .limit(limit)
            .all()
        )

    def get_by_version_number(self, file_id: uuid.UUID, version_number: int) -> CodeVersion | None:
        """
        根据版本号获取特定版本

        Args:
            file_id: 文件 ID
            version_number: 版本号

        Returns:
            Optional[CodeVersion]: 版本对象，不存在则返回 None
        """
        return (
            self.db.query(CodeVersion)
            .filter(CodeVersion.file_id == file_id, CodeVersion.version_number == version_number)
            .first()
        )

    def get_all(self, limit: int = 100, offset: int = 0) -> list[CodeVersion]:
        """
        获取所有版本记录（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[CodeVersion]: 版本列表
        """
        return (
            self.db.query(CodeVersion)
            .order_by(CodeVersion.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def delete(self, version_id: uuid.UUID) -> bool:
        """
        删除版本记录

        Args:
            version_id: 版本 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(CodeVersion).filter(CodeVersion.id == version_id).delete()
        self.db.commit()
        return result > 0
