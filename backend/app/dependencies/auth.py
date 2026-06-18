"""
Authentication Dependencies

认证授权的 FastAPI 依赖注入
"""

from datetime import UTC, datetime
from typing import Annotated

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt_handler import (
    TokenExpiredError,
    TokenInvalidError,
    decode_token,
)
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# OAuth2 password flow（Swagger UI 使用）
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_redis() -> redis.Redis:
    """
    获取 Redis 客户端

    如果 Redis 不可用，返回 None（允许应用降级运行）
    """
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        return client
    except Exception:
        # Redis 不可用时返回 None，调用方需要处理
        return None


def is_token_blacklisted(token: str) -> bool:
    """
    检查 Token 是否在黑名单中（已登出）

    Returns:
        bool: True 表示在黑名单中（无效），False 表示有效
    """
    redis_client = get_redis()
    if not redis_client:
        # Redis 不可用时，不应用黑名单（降级模式）
        return False

    try:
        return redis_client.exists(f"blacklist:{token}") > 0
    except Exception:
        return False


def blacklist_token(token: str, expire_seconds: int) -> None:
    """
    将 Token 加入黑名单

    Args:
        token: 要拉黑的 Token
        expire_seconds: 过期时间（秒）
    """
    redis_client = get_redis()
    if not redis_client:
        return

    try:
        redis_client.setex(f"blacklist:{token}", expire_seconds, "1")
    except Exception:
        pass


def revoke_user_tokens(user_id: str, expire_seconds: int) -> None:
    """
    Revoke already-issued tokens for a user.

    The marker is checked against the token iat claim. This lets logout
    invalidate refresh tokens even when the client does not send the refresh
    token in the logout request.
    """
    redis_client = get_redis()
    if not redis_client:
        return

    try:
        redis_client.setex(
            f"blacklist:user:{user_id}:revoked_after",
            expire_seconds,
            str(datetime.now(UTC).timestamp()),
        )
    except Exception:
        pass


def is_user_token_revoked(user_id: str, token_iat: object) -> bool:
    """
    Check whether a token was issued before the user's revocation marker.

    The marker stores the logout timestamp. Existing tokens with an iat at or
    before that timestamp are revoked; tokens issued by a later login remain
    valid.
    """
    if token_iat is None:
        return True

    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        revoked_after_raw = redis_client.get(f"blacklist:user:{user_id}:revoked_after")
        if not revoked_after_raw:
            return False

        revoked_after = float(revoked_after_raw)
        if isinstance(token_iat, int | float):
            issued_at = float(token_iat)
        elif isinstance(token_iat, datetime):
            issued_at = token_iat.timestamp()
        else:
            issued_at = float(str(token_iat))

        return issued_at <= revoked_after
    except (TypeError, ValueError):
        return True
    except Exception:
        return False


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前认证用户

    Raises:
        HTTPException: 401 如果 Token 无效/过期/已登出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    # 检查黑名单
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token, expected_type="access")
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    if is_user_token_revoked(user_id_str, payload.get("issued_at", payload.get("iat"))):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepository(db)
    try:
        import uuid as uuid_lib

        user_id = uuid_lib.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = repo.get_by_id(user_id)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_role(required_role: str):
    """
    角色权限校验依赖

    使用基于层级的访问控制：
    - admin (3) 可以访问所有功能
    - developer (2) 可以访问 developer 和 viewer 功能
    - viewer (1) 只能访问 viewer 功能

    Args:
        required_role: 需要的最低角色

    Returns:
        依赖函数，返回当前用户

    Raises:
        HTTPException: 403 如果权限不足
    """

    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return current_user

    return role_checker


# 便捷依赖
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
DeveloperUser = Annotated[User, Depends(require_role("developer"))]
