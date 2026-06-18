"""
Task API routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Create a new task

    Args:
        task: Task creation data
        db: Database session

    Returns:
        Created task
    """
    repo = TaskRepository(db)
    created = repo.create(
        project_id=task.project_id,
        title=task.title,
        description=task.description or "",
        priority=task.priority,
    )
    return TaskResponse.model_validate(created)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Get task by ID

    Args:
        task_id: Task unique identifier
        db: Database session

    Returns:
        Task data

    Raises:
        HTTPException: 404 if task not found
    """
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return TaskResponse.model_validate(task)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    pagination: dict = Depends(get_pagination), db: Session = Depends(get_db)
) -> list[TaskResponse]:
    """
    List all tasks with pagination

    Args:
        pagination: Pagination parameters (limit, offset)
        db: Database session

    Returns:
        List of tasks
    """
    repo = TaskRepository(db)
    tasks = repo.get_all(limit=pagination["limit"], offset=pagination["offset"])
    return [TaskResponse.model_validate(task) for task in tasks]


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task: TaskUpdate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Update task

    Args:
        task_id: Task unique identifier
        task: Task update data
        db: Database session

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task not found
    """
    repo = TaskRepository(db)

    # Check if task exists
    existing = repo.get_by_id(task_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Update task
    success = repo.update(
        task_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task",
        )

    # Fetch updated task
    updated = repo.get_by_id(task_id)
    return TaskResponse.model_validate(updated)


@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: UUID, status_update: TaskStatusUpdate, db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update task status

    Args:
        task_id: Task unique identifier
        status_update: Status update data
        db: Database session

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task not found
    """
    repo = TaskRepository(db)

    # Check if task exists
    existing = repo.get_by_id(task_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Update status
    success = repo.update_status(task_id, status=status_update.status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task status",
        )

    # Fetch updated task
    updated = repo.get_by_id(task_id)
    return TaskResponse.model_validate(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete task

    Args:
        task_id: Task unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if task not found
    """
    repo = TaskRepository(db)
    success = repo.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
