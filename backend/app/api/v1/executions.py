"""
Agent Execution API routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.schemas.execution_schema import ExecutionCreate, ExecutionResponse, ExecutionStatusUpdate

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_execution(
    execution: ExecutionCreate, db: Session = Depends(get_db)
) -> ExecutionResponse:
    """
    Create a new agent execution

    Args:
        execution: Execution creation data
        db: Database session

    Returns:
        Created execution
    """
    repo = AgentExecutionRepository(db)
    created = repo.create(
        task_id=execution.task_id,
        agent_type=execution.agent_type,
        state=execution.state,
    )
    return ExecutionResponse.model_validate(created)


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: UUID, db: Session = Depends(get_db)) -> ExecutionResponse:
    """
    Get execution by ID

    Args:
        execution_id: Execution unique identifier
        db: Database session

    Returns:
        Execution data

    Raises:
        HTTPException: 404 if execution not found
    """
    repo = AgentExecutionRepository(db)
    execution = repo.get_by_id(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )
    return ExecutionResponse.model_validate(execution)


@router.get("/", response_model=list[ExecutionResponse])
def list_executions(
    pagination: dict = Depends(get_pagination), db: Session = Depends(get_db)
) -> list[ExecutionResponse]:
    """
    List all executions with pagination

    Args:
        pagination: Pagination parameters (limit, offset)
        db: Database session

    Returns:
        List of executions
    """
    repo = AgentExecutionRepository(db)
    executions = repo.get_all(limit=pagination["limit"], offset=pagination["offset"])
    return [ExecutionResponse.model_validate(execution) for execution in executions]


@router.put("/{execution_id}/status", response_model=ExecutionResponse)
def update_execution_status(
    execution_id: UUID, status_update: ExecutionStatusUpdate, db: Session = Depends(get_db)
) -> ExecutionResponse:
    """
    Update execution status

    Args:
        execution_id: Execution unique identifier
        status_update: Status update data
        db: Database session

    Returns:
        Updated execution

    Raises:
        HTTPException: 404 if execution not found
    """
    repo = AgentExecutionRepository(db)

    # Check if execution exists
    existing = repo.get_by_id(execution_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    # Update status
    success = repo.update_status(
        execution_id,
        status=status_update.status,
        state=status_update.state,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update execution status",
        )

    # Fetch updated execution
    updated = repo.get_by_id(execution_id)
    return ExecutionResponse.model_validate(updated)


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(execution_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete execution

    Args:
        execution_id: Execution unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if execution not found
    """
    repo = AgentExecutionRepository(db)
    success = repo.delete(execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )
