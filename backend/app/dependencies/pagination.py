"""
Pagination dependencies for list endpoints
"""

from typing import Annotated

from fastapi import Query


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=100, description="Number of items to return")] = 10,
    offset: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
) -> dict[str, int]:
    """
    Pagination parameters dependency

    Args:
        limit: Maximum number of items to return (1-100, default 10)
        offset: Number of items to skip (default 0)

    Returns:
        dict with limit and offset values

    Example:
        @app.get("/users")
        def get_users(pagination: dict = Depends(get_pagination)):
            limit = pagination["limit"]
            offset = pagination["offset"]
            return db.query(User).limit(limit).offset(offset).all()
    """
    return {"limit": limit, "offset": offset}
