"""
FastAPI dependencies
"""
from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination

__all__ = ["get_db", "get_pagination"]
