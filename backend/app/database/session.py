"""
Database Session Management

会话管理和上下文管理器
"""
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal


@contextmanager
def transaction_scope() -> Generator[Session, None, None]:
    """
    提供事务作用域的上下文管理器

    自动处理提交和回滚

    Yields:
        Session: 数据库会话

    Raises:
        Exception: 事务执行过程中的任何异常
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    """
    获取新的数据库会话

    注意：调用方负责关闭会话

    Returns:
        Session: 数据库会话
    """
    return SessionLocal()
