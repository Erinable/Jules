"""
Quality Metric API routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.quality_metric_repository import QualityMetricRepository
from app.schemas.quality_schema import QualityMetricCreate, QualityMetricResponse

router = APIRouter(prefix="/quality", tags=["quality"])


@router.post("/", response_model=QualityMetricResponse, status_code=status.HTTP_201_CREATED)
def create_quality_metric(
    metric: QualityMetricCreate, db: Session = Depends(get_db)
) -> QualityMetricResponse:
    """
    Create a new quality metric

    Args:
        metric: Quality metric creation data
        db: Database session

    Returns:
        Created quality metric
    """
    repo = QualityMetricRepository(db)
    created = repo.create(
        project_id=metric.project_id,
        avg_complexity=metric.avg_complexity,
        maintainability_index=metric.maintainability_index,
        security_issues=metric.security_issues,
        test_coverage=metric.test_coverage,
    )
    return QualityMetricResponse.model_validate(created)


@router.get("/{metric_id}", response_model=QualityMetricResponse)
def get_quality_metric(metric_id: UUID, db: Session = Depends(get_db)) -> QualityMetricResponse:
    """
    Get quality metric by ID

    Args:
        metric_id: Metric unique identifier
        db: Database session

    Returns:
        Quality metric data

    Raises:
        HTTPException: 404 if metric not found
    """
    repo = QualityMetricRepository(db)
    metric = repo.get_by_id(metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality metric {metric_id} not found",
        )
    return QualityMetricResponse.model_validate(metric)


@router.get("/project/{project_id}/latest", response_model=QualityMetricResponse)
def get_latest_quality_metric(
    project_id: UUID, db: Session = Depends(get_db)
) -> QualityMetricResponse:
    """
    Get latest quality metric for a project

    Args:
        project_id: Project unique identifier
        db: Database session

    Returns:
        Latest quality metric

    Raises:
        HTTPException: 404 if no metrics found
    """
    repo = QualityMetricRepository(db)
    metric = repo.get_latest(project_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quality metrics found for project {project_id}",
        )
    return QualityMetricResponse.model_validate(metric)


@router.get("/project/{project_id}/history", response_model=list[QualityMetricResponse])
def get_quality_metric_history(
    project_id: UUID, limit: int = 10, db: Session = Depends(get_db)
) -> list[QualityMetricResponse]:
    """
    Get quality metric history for a project

    Args:
        project_id: Project unique identifier
        limit: Maximum number of metrics to return (default 10)
        db: Database session

    Returns:
        List of quality metrics in reverse chronological order
    """
    repo = QualityMetricRepository(db)
    metrics = repo.get_history(project_id, limit=limit)
    return [QualityMetricResponse.model_validate(metric) for metric in metrics]


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quality_metric(metric_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete quality metric

    Args:
        metric_id: Metric unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if metric not found
    """
    repo = QualityMetricRepository(db)
    success = repo.delete(metric_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality metric {metric_id} not found",
        )
