"""
Database Connection Configuration

数据库连接和引擎配置
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

# 从环境变量获取数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://jules:jules_password@localhost:5432/jules_db"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_pre_ping=True,  # 连接健康检查
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),  # 1小时回收连接
    echo=os.getenv("ENVIRONMENT") == "development",  # 开发环境显示 SQL
)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    用于依赖注入，自动管理会话生命周期

    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
