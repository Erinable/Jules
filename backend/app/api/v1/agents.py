"""
Agent API routes
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_pagination
from app.repositories.agent_repository import AgentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.schemas.agent_schema import AgentCreate, AgentResponse, AgentUpdate
from app.agent.scheduler import scheduler
from app.agent.executor import AgentExecutor

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)) -> AgentResponse:
    """
    Create a new agent

    Args:
        agent: Agent creation data
        db: Database session

    Returns:
        Created agent

    Raises:
        HTTPException: 400 if agent name already exists
    """
    repo = AgentRepository(db)

    # Check if agent name already exists
    existing = repo.get_by_name(agent.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with name {agent.name} already exists",
        )

    created = repo.create(
        name=agent.name,
        description=agent.description or "",
        config=agent.config,
    )
    return AgentResponse.model_validate(created)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: UUID, db: Session = Depends(get_db)) -> AgentResponse:
    """
    Get agent by ID

    Args:
        agent_id: Agent unique identifier
        db: Database session

    Returns:
        Agent data

    Raises:
        HTTPException: 404 if agent not found
    """
    repo = AgentRepository(db)
    agent = repo.get_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    return AgentResponse.model_validate(agent)


@router.get("/", response_model=list[AgentResponse])
def list_agents(pagination: dict = Depends(get_pagination), db: Session = Depends(get_db)) -> list[AgentResponse]:
    """
    List all agents with pagination

    Args:
        pagination: Pagination parameters (limit, offset)
        db: Database session

    Returns:
        List of agents
    """
    repo = AgentRepository(db)
    agents = repo.get_all(limit=pagination["limit"], offset=pagination["offset"])
    return [AgentResponse.model_validate(agent) for agent in agents]


@router.get("/active/list", response_model=list[AgentResponse])
def list_active_agents(db: Session = Depends(get_db)) -> list[AgentResponse]:
    """
    List all active agents

    Args:
        db: Database session

    Returns:
        List of active agents
    """
    repo = AgentRepository(db)
    agents = repo.get_all_active()
    return [AgentResponse.model_validate(agent) for agent in agents]


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: UUID, agent: AgentUpdate, db: Session = Depends(get_db)) -> AgentResponse:
    """
    Update agent

    Args:
        agent_id: Agent unique identifier
        agent: Agent update data
        db: Database session

    Returns:
        Updated agent

    Raises:
        HTTPException: 404 if agent not found
    """
    repo = AgentRepository(db)

    # Check if agent exists
    existing = repo.get_by_id(agent_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Update agent
    success = repo.update(
        agent_id,
        description=agent.description,
        config=agent.config,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent",
        )

    # Fetch updated agent
    updated = repo.get_by_id(agent_id)
    return AgentResponse.model_validate(updated)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete agent

    Args:
        agent_id: Agent unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if agent not found
    """
    repo = AgentRepository(db)
    success = repo.delete(agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )


# New Agent execution endpoints


@router.post("/execute", status_code=status.HTTP_202_ACCEPTED)
def execute_agent_task(
    task_id: UUID,
    agent_type: str,
    priority: int = 5,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Execute an agent task.

    Args:
        task_id: Task ID to execute
        agent_type: Type of agent to use
        priority: Task priority (0-10, higher = more urgent)
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Execution status

    Raises:
        HTTPException: 404 if task not found
    """
    task_repo = TaskRepository(db)
    task = task_repo.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Submit task to scheduler
    submission_id = scheduler.submit_task(str(task_id), agent_type, priority)

    return {
        "task_id": str(task_id),
        "submission_id": submission_id,
        "status": "queued",
        "message": "Task submitted for execution"
    }


@router.get("/status/{execution_id}")
def get_execution_status(
    execution_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get execution status.

    Args:
        execution_id: Execution ID
        db: Database session

    Returns:
        Execution status

    Raises:
        HTTPException: 404 if execution not found
    """
    execution_repo = AgentExecutionRepository(db)
    execution = execution_repo.get_by_id(execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    return {
        "execution_id": str(execution.id),
        "task_id": str(execution.task_id),
        "agent_type": execution.agent_type,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "output": execution.output,
        "error_message": execution.error_message,
    }


@router.post("/retry/{execution_id}")
def retry_execution(
    execution_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Retry a failed execution.

    Args:
        execution_id: Execution ID to retry
        db: Database session

    Returns:
        Retry status

    Raises:
        HTTPException: 404 if execution not found, 400 if not failed
    """
    execution_repo = AgentExecutionRepository(db)
    execution = execution_repo.get_by_id(execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    if execution.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution is not in failed state (current: {execution.status})"
        )

    # Retry the task
    success = scheduler.retry_failed_task(str(execution.task_id))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be retried (max retries reached or not in failed state)"
        )

    return {
        "execution_id": str(execution_id),
        "task_id": str(execution.task_id),
        "status": "requeued",
        "message": "Task resubmitted for execution"
    }


@router.get("/queue")
def get_queue_status() -> dict:
    """
    Get current queue status.

    Returns:
        Queue statistics
    """
    status_data = scheduler.get_queue_status()
    running_tasks = scheduler.get_running_tasks()
    failed_tasks = scheduler.get_failed_tasks()

    return {
        "queue": status_data,
        "running_tasks": [
            {
                "task_id": task["task_id"],
                "agent_type": task["agent_type"],
                "priority": task["priority"],
                "submitted_at": task["submitted_at"].isoformat(),
            }
            for task in running_tasks
        ],
        "failed_tasks": [
            {
                "task_id": task["task_id"],
                "agent_type": task["agent_type"],
                "retry_count": task.get("retry_count", 0),
                "error": task.get("error"),
            }
            for task in failed_tasks
        ]
    }

