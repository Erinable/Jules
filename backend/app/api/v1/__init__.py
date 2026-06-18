"""
API v1 router initialization
"""

from fastapi import APIRouter

from app.api.v1 import (
    agents,
    auth,
    code_files,
    executions,
    health,
    progress,
    quality,
    tasks,
    users,
    websocket,
)

api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(agents.router)
api_router.include_router(executions.router)
api_router.include_router(code_files.router)
api_router.include_router(quality.router)
api_router.include_router(health.router)
api_router.include_router(progress.router)
api_router.include_router(websocket.router)

__all__ = ["api_router"]
