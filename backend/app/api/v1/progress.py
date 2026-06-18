"""
Progress Tracking API Routes (Sprint 3).

REST API endpoints for agent execution progress tracking.
Based on docs/design/progress-tracking-api.md.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import AdminUser, CurrentUser, DeveloperUser
from app.dependencies.database import get_db
from app.repositories.progress_repository import ProgressRepository
from app.schemas.agent_progress import AgentStep, RunStatus, StepState
from app.schemas.progress_api import (
    CancelRequest,
    ControlResponse,
    PaginatedLogsResponse,
    PaginatedProgressResponse,
    PauseRequest,
    ProgressResponse,
    ProgressSummary,
    RetryRequest,
    StartRequest,
    TransitionsResponse,
)

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_progress_repo(db: Session = Depends(get_db)) -> ProgressRepository:
    """Dependency to get ProgressRepository instance."""
    return ProgressRepository(db)


def _build_progress_response(progress_record) -> ProgressResponse:
    """Convert ExecutionProgress ORM model to ProgressResponse schema."""
    steps = [StepState(**step) for step in progress_record.steps_json]
    return ProgressResponse(
        run_id=progress_record.run_id,
        user_id=progress_record.user_id,
        status=RunStatus(progress_record.status),
        current_step=AgentStep(progress_record.current_step)
        if progress_record.current_step
        else None,
        overall_percentage=progress_record.overall_percentage,
        eta_seconds=progress_record.eta_seconds,
        started_at=progress_record.started_at,
        updated_at=progress_record.updated_at,
        completed_at=progress_record.completed_at,
        steps=steps,
        total_duration_ms=progress_record.total_duration_ms,
        retry_count=progress_record.retry_count,
    )


def _check_ownership(progress_record, current_user) -> None:
    """
    Check if current user owns the progress record.
    Admin can access any record; others only their own.

    Raises:
        HTTPException: 403 if permission denied
    """
    if current_user.role != "admin" and progress_record.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own execution progress",
        )


# ── 4.1 GET /progress/{run_id} ───────────────────────────────────────────


@router.get(
    "/{run_id}",
    response_model=ProgressResponse,
    summary="Get execution progress",
    description="Retrieve detailed progress snapshot for a specific run",
)
def get_progress(
    run_id: str,
    current_user: CurrentUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ProgressResponse:
    """
    Get single execution progress by run_id.

    - **Viewer+**: Can view own progress
    - **Admin**: Can view any progress
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)
    return _build_progress_response(progress)


# ── 4.2 GET /progress/{run_id}/logs ──────────────────────────────────────


@router.get(
    "/{run_id}/logs",
    response_model=PaginatedLogsResponse,
    summary="Get execution logs",
    description="Retrieve paginated logs with optional filtering by step/level",
)
def get_logs(
    run_id: str,
    current_user: CurrentUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
    step: Annotated[AgentStep | None, Query(description="Filter by step")] = None,
    level: Annotated[
        str | None, Query(description="Filter by level (info/warn/error/debug)")
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "asc",
) -> PaginatedLogsResponse:
    """
    Get logs for a specific run with pagination and filtering.

    - **Viewer+**: Can view own logs
    - **Admin**: Can view any logs
    """
    # Check ownership
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )
    _check_ownership(progress, current_user)

    # Get logs
    logs, total = repo.get_logs(
        run_id=run_id,
        step=step.value if step else None,
        level=level,
        page=page,
        limit=limit,
        order=order,
    )

    return PaginatedLogsResponse(
        items=[
            {
                "id": log.id,
                "run_id": log.run_id,
                "step": AgentStep(log.step),
                "level": log.level,
                "message": log.message,
                "sequence_num": log.sequence_num,
                "timestamp": log.timestamp,
                "metadata": log.metadata_json or {},
            }
            for log in logs
        ],
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


# ── 4.3 GET /progress/{run_id}/transitions ──────────────────────────────


@router.get(
    "/{run_id}/transitions",
    response_model=TransitionsResponse,
    summary="Get state transitions",
    description="Retrieve all state transitions for a run (for replay/debugging)",
)
def get_transitions(
    run_id: str,
    current_user: CurrentUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
    start_time: Annotated[datetime | None, Query(description="Filter from timestamp")] = None,
    end_time: Annotated[datetime | None, Query(description="Filter until timestamp")] = None,
) -> TransitionsResponse:
    """
    Get state transition history for a run.

    - **Viewer+**: Can view own transitions
    - **Admin**: Can view any transitions
    """
    # Check ownership
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )
    _check_ownership(progress, current_user)

    # Get transitions
    transitions = repo.get_transitions(run_id=run_id, start_time=start_time, end_time=end_time)

    return TransitionsResponse(
        items=[
            {
                "id": trans.id,
                "run_id": trans.run_id,
                "from_status": trans.from_status,
                "to_status": trans.to_status,
                "step": AgentStep(trans.step) if trans.step else None,
                "timestamp": trans.timestamp,
                "metadata": trans.metadata_json or {},
            }
            for trans in transitions
        ],
        total=len(transitions),
    )


# ── 4.4 GET /progress/user/{user_id} ────────────────────────────────────


@router.get(
    "/user/{user_id}",
    response_model=PaginatedProgressResponse,
    summary="List user's progress",
    description="List all execution progress for a specific user",
)
def list_user_progress(
    user_id: str,
    current_user: CurrentUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
    status_filter: Annotated[
        RunStatus | None, Query(alias="status", description="Filter by status")
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedProgressResponse:
    """
    List progress records for a specific user.

    - **Viewer+**: Can list own progress only
    - **Admin**: Can list any user's progress
    """
    # Check permission
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only list your own progress",
        )

    # Get progress list
    items, total = repo.list_progress_by_user(
        user_id=user_id,
        status=status_filter.value if status_filter else None,
        page=page,
        limit=limit,
    )

    return PaginatedProgressResponse(
        items=[
            ProgressSummary(
                run_id=item.run_id,
                user_id=item.user_id,
                status=RunStatus(item.status),
                current_step=AgentStep(item.current_step) if item.current_step else None,
                overall_percentage=item.overall_percentage,
                started_at=item.started_at,
                updated_at=item.updated_at,
                completed_at=item.completed_at,
            )
            for item in items
        ],
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


# ── 4.5 POST /progress/{run_id}/start ────────────────────────────────────


@router.post(
    "/{run_id}/start",
    response_model=ControlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start execution",
    description="Trigger agent execution start (queued → running)",
)
def start_execution(
    run_id: str,
    request: StartRequest,
    current_user: DeveloperUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ControlResponse:
    """
    Start an execution (typically moves from queued → running).

    - **Developer+**: Can start own executions
    - **Admin**: Can start any execution
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)

    # Validate state transition
    if progress.status != "queued":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start execution in status: {progress.status}",
        )

    # Update status
    repo.update_progress(run_id, status="running", updated_at=datetime.utcnow())
    repo.add_transition(run_id=run_id, from_status="queued", to_status="running")

    return ControlResponse(
        run_id=run_id,
        previous_status=RunStatus.QUEUED,
        new_status=RunStatus.RUNNING,
        message="Execution started",
        affected_step=request.initial_step,
    )


# ── 4.6 POST /progress/{run_id}/pause ────────────────────────────────────


@router.post(
    "/{run_id}/pause",
    response_model=ControlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Pause execution",
    description="Pause a running execution (will resume current step later)",
)
def pause_execution(
    run_id: str,
    request: PauseRequest,
    current_user: DeveloperUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ControlResponse:
    """
    Pause a running execution.

    - **Developer+**: Can pause own executions
    - **Admin**: Can pause any execution
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)

    # Validate state transition
    if progress.status != "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot pause execution in status: {progress.status}",
        )

    # Update status
    repo.update_progress(run_id, status="paused", updated_at=datetime.utcnow())
    repo.add_transition(
        run_id=run_id,
        from_status="running",
        to_status="paused",
        metadata={"duration_seconds": request.duration_seconds}
        if request.duration_seconds
        else None,
    )

    return ControlResponse(
        run_id=run_id,
        previous_status=RunStatus.RUNNING,
        new_status=RunStatus.PAUSED,
        message=f"Execution paused{f' for {request.duration_seconds}s' if request.duration_seconds else ''}",
        affected_step=AgentStep(progress.current_step) if progress.current_step else None,
    )


# ── 4.7 POST /progress/{run_id}/resume ───────────────────────────────────


@router.post(
    "/{run_id}/resume",
    response_model=ControlResponse,
    status_code=status.HTTP_200_OK,
    summary="Resume execution",
    description="Resume a paused execution",
)
def resume_execution(
    run_id: str,
    current_user: DeveloperUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ControlResponse:
    """
    Resume a paused execution.

    - **Developer+**: Can resume own executions
    - **Admin**: Can resume any execution
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)

    # Validate state transition
    if progress.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot resume execution in status: {progress.status}",
        )

    # Update status
    repo.update_progress(run_id, status="running", updated_at=datetime.utcnow())
    repo.add_transition(run_id=run_id, from_status="paused", to_status="running")

    return ControlResponse(
        run_id=run_id,
        previous_status=RunStatus.PAUSED,
        new_status=RunStatus.RUNNING,
        message="Execution resumed",
        affected_step=AgentStep(progress.current_step) if progress.current_step else None,
    )


# ── 4.8 POST /progress/{run_id}/cancel ───────────────────────────────────


@router.post(
    "/{run_id}/cancel",
    response_model=ControlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Cancel execution",
    description="Cancel a running or paused execution",
)
def cancel_execution(
    run_id: str,
    request: CancelRequest,
    current_user: DeveloperUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ControlResponse:
    """
    Cancel an execution.

    - **Developer+**: Can cancel own executions
    - **Admin**: Can cancel any execution
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)

    # Validate state transition (cannot cancel terminal states)
    if progress.status in ["completed", "failed", "cancelled", "timeout"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel execution in terminal status: {progress.status}",
        )

    # Update status
    previous_status = progress.status
    repo.update_progress(
        run_id, status="cancelled", updated_at=datetime.utcnow(), completed_at=datetime.utcnow()
    )
    repo.add_transition(
        run_id=run_id,
        from_status=previous_status,
        to_status="cancelled",
        metadata={"reason": request.reason, "force": request.force},
    )

    message = "Execution cancelled"
    if not request.force:
        message += " (graceful shutdown)"

    return ControlResponse(
        run_id=run_id,
        previous_status=RunStatus(previous_status),
        new_status=RunStatus.CANCELLED,
        message=message,
        affected_step=AgentStep(progress.current_step) if progress.current_step else None,
    )


# ── 4.9 POST /progress/{run_id}/retry ────────────────────────────────────


@router.post(
    "/{run_id}/retry",
    response_model=ControlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry execution",
    description="Retry a failed execution from a specific step",
)
def retry_execution(
    run_id: str,
    request: RetryRequest,
    current_user: DeveloperUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> ControlResponse:
    """
    Retry a failed execution.

    - **Developer+**: Can retry own executions
    - **Admin**: Can retry any execution
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    _check_ownership(progress, current_user)

    # Validate state (only retry failed executions)
    if progress.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot retry execution in status: {progress.status}. Only 'failed' status can be retried.",
        )

    # Update status and retry count
    repo.update_progress(
        run_id,
        status="running",
        retry_count=progress.retry_count + 1,
        updated_at=datetime.utcnow(),
    )
    repo.add_transition(
        run_id=run_id,
        from_status="failed",
        to_status="running",
        metadata={
            "from_step": request.from_step.value if request.from_step else None,
            "reset_all": request.reset_all,
        },
    )

    return ControlResponse(
        run_id=run_id,
        previous_status=RunStatus.FAILED,
        new_status=RunStatus.RUNNING,
        message=f"Execution retry initiated (attempt #{progress.retry_count + 1})",
        affected_step=request.from_step or AgentStep(progress.current_step)
        if progress.current_step
        else None,
    )


# ── 4.10 DELETE /progress/{run_id} ───────────────────────────────────────


@router.delete(
    "/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete execution progress",
    description="Delete a progress record (admin only, soft delete)",
)
def delete_progress(
    run_id: str,
    admin_user: AdminUser,
    repo: Annotated[ProgressRepository, Depends(_get_progress_repo)],
) -> None:
    """
    Delete an execution progress record (soft delete).

    - **Admin only**
    """
    progress = repo.get_progress(run_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress not found for run_id: {run_id}",
        )

    # Soft delete (actual deletion handled by ProgressRepository)
    deleted = repo.delete_progress(run_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete progress",
        )

    # No content response (204)
    return None
