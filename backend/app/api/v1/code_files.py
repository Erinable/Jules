"""
Code File API routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.code_file_repository import CodeFileRepository
from app.schemas.code_file_schema import CodeFileCreate, CodeFileResponse, CodeFileUpdate

router = APIRouter(prefix="/code-files", tags=["code-files"])


@router.post("/", response_model=CodeFileResponse, status_code=status.HTTP_201_CREATED)
def create_code_file(file: CodeFileCreate, db: Session = Depends(get_db)) -> CodeFileResponse:
    """
    Create a new code file

    Args:
        file: Code file creation data
        db: Database session

    Returns:
        Created code file

    Raises:
        HTTPException: 400 if file path already exists in project
    """
    repo = CodeFileRepository(db)

    # Check if file path already exists in project
    existing = repo.get_by_path(file.project_id, file.path)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {file.path} already exists in project",
        )

    created = repo.create(
        project_id=file.project_id,
        path=file.path,
        content=file.content,
        file_hash=file.file_hash,
    )
    return CodeFileResponse.model_validate(created)


@router.get("/{file_id}", response_model=CodeFileResponse)
def get_code_file(file_id: UUID, db: Session = Depends(get_db)) -> CodeFileResponse:
    """
    Get code file by ID

    Args:
        file_id: File unique identifier
        db: Database session

    Returns:
        Code file data

    Raises:
        HTTPException: 404 if file not found
    """
    repo = CodeFileRepository(db)
    file = repo.get_by_id(file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found",
        )
    return CodeFileResponse.model_validate(file)


@router.get("/project/{project_id}", response_model=list[CodeFileResponse])
def list_project_files(project_id: UUID, db: Session = Depends(get_db)) -> list[CodeFileResponse]:
    """
    List all files in a project

    Args:
        project_id: Project unique identifier
        db: Database session

    Returns:
        List of code files
    """
    repo = CodeFileRepository(db)
    files = repo.list_by_project(project_id)
    return [CodeFileResponse.model_validate(file) for file in files]


@router.put("/{file_id}", response_model=CodeFileResponse)
def update_code_file(
    file_id: UUID, file: CodeFileUpdate, db: Session = Depends(get_db)
) -> CodeFileResponse:
    """
    Update code file content

    Args:
        file_id: File unique identifier
        file: File update data
        db: Database session

    Returns:
        Updated code file

    Raises:
        HTTPException: 404 if file not found
    """
    repo = CodeFileRepository(db)

    # Check if file exists
    existing = repo.get_by_id(file_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found",
        )

    # Update file content
    success = repo.update_content(
        file_id,
        content=file.content,
        file_hash=file.file_hash,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file",
        )

    # Fetch updated file
    updated = repo.get_by_id(file_id)
    return CodeFileResponse.model_validate(updated)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_code_file(file_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Delete code file

    Args:
        file_id: File unique identifier
        db: Database session

    Raises:
        HTTPException: 404 if file not found
    """
    repo = CodeFileRepository(db)
    success = repo.delete(file_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found",
        )
