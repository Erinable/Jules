"""
Health check API routes
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> JSONResponse:
    """
    Health check endpoint

    Returns:
        JSON response with service status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "jules-backend",
            "version": "0.1.0",
        }
    )


@router.get("/ready")
async def readiness_check() -> JSONResponse:
    """
    Readiness check endpoint

    Returns:
        JSON response indicating service readiness
    """
    return JSONResponse(
        content={
            "ready": True,
            "service": "jules-backend",
        }
    )


@router.get("/live")
async def liveness_check() -> JSONResponse:
    """
    Liveness check endpoint

    Returns:
        JSON response indicating service is alive
    """
    return JSONResponse(
        content={
            "alive": True,
            "service": "jules-backend",
        }
    )
