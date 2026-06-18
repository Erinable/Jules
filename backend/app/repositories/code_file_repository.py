"""
CodeFile Repository

代码文件仓储层，提供代码文件数据访问方法
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.code_file import CodeFile


class CodeFileRepository:
    """代码文件仓储"""

    def __init__(self, db: Session) -> None:
        """
        初始化代码文件仓储

        Args:
            db: 数据库会话
        """
        self.db = db

    def create(self, project_id: uuid.UUID, path: str, content: str, file_hash: str) -> CodeFile:
        """
        创建新的代码文件

        Args:
            project_id: 项目 ID
            path: 文件路径
            content: 文件内容
            file_hash: 文件哈希值

        Returns:
            CodeFile: 创建的代码文件对象
        """
        code_file = CodeFile(project_id=project_id, path=path, content=content, hash=file_hash)
        self.db.add(code_file)
        self.db.commit()
        self.db.refresh(code_file)
        return code_file

    def get_by_id(self, file_id: uuid.UUID) -> CodeFile | None:
        """
        根据 ID 获取代码文件

        Args:
            file_id: 文件 ID

        Returns:
            Optional[CodeFile]: 代码文件对象，不存在则返回 None
        """
        return self.db.query(CodeFile).filter(CodeFile.id == file_id).first()

    def get_by_path(self, project_id: uuid.UUID, path: str) -> CodeFile | None:
        """
        根据路径获取代码文件

        Args:
            project_id: 项目 ID
            path: 文件路径

        Returns:
            Optional[CodeFile]: 代码文件对象，不存在则返回 None
        """
        return (
            self.db.query(CodeFile)
            .filter(CodeFile.project_id == project_id, CodeFile.path == path)
            .first()
        )

    def list_by_project(self, project_id: uuid.UUID) -> list[CodeFile]:
        """
        获取项目的所有代码文件

        Args:
            project_id: 项目 ID

        Returns:
            list[CodeFile]: 代码文件列表
        """
        return (
            self.db.query(CodeFile)
            .filter(CodeFile.project_id == project_id)
            .order_by(CodeFile.path)
            .all()
        )

    def get_all(self, limit: int = 100, offset: int = 0) -> list[CodeFile]:
        """
        获取所有代码文件（分页）

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[CodeFile]: 代码文件列表
        """
        return (
            self.db.query(CodeFile)
            .order_by(CodeFile.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_content(self, file_id: uuid.UUID, content: str, file_hash: str) -> bool:
        """
        更新文件内容（数据库操作）

        注意：此方法修改数据库状态，调用方应重新查询获取最新对象

        Args:
            file_id: 文件 ID
            content: 新内容
            file_hash: 新哈希值

        Returns:
            bool: 操作是否成功
        """
        result = (
            self.db.query(CodeFile)
            .filter(CodeFile.id == file_id)
            .update({"content": content, "hash": file_hash, "updated_at": datetime.utcnow()})
        )
        self.db.commit()
        return result > 0

    def delete(self, file_id: uuid.UUID) -> bool:
        """
        删除代码文件

        Args:
            file_id: 文件 ID

        Returns:
            bool: 操作是否成功
        """
        result = self.db.query(CodeFile).filter(CodeFile.id == file_id).delete()
        self.db.commit()
        return result > 0
