"""
Authentication API Routes

认证授权相关的 API 端点：
- POST /auth/register - 用户注册
- POST /auth/login - 用户登录
- POST /auth/refresh - 刷新 Token
- POST /auth/logout - 登出
- GET  /auth/me - 获取当前用户信息
- PUT  /auth/password - 修改密码
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt_handler import (
    TokenExpiredError,
    TokenInvalidError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.security import (
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.dependencies.auth import (
    CurrentUser,
    blacklist_token,
    get_redis,
    is_token_blacklisted,
    is_user_token_revoked,
    oauth2_scheme,
    revoke_user_tokens,
)
from app.dependencies.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserAuthResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _rate_limit_key(request: Request, identifier: str) -> str:
    """生成 Rate Limit 的 Redis Key（使用 IP + 标识符）"""
    client_ip = request.client.host if request.client else "unknown"
    return f"rate_limit:login:{client_ip}:{identifier}"


def _check_rate_limit(request: Request, identifier: str) -> None:
    """
    检查登录尝试频率限制

    Args:
        identifier: 通常是邮箱（用于登录）
                    或 IP（用于其他场景）

    Raises:
        HTTPException: 429 如果超过限制
    """
    redis_client = get_redis()
    if not redis_client:
        return  # Redis 不可用时跳过限流

    key = _rate_limit_key(request, identifier)
    try:
        attempts = redis_client.incr(key)
        if attempts == 1:
            redis_client.expire(key, 60)  # 1 分钟窗口

        if attempts > settings.LOGIN_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": "60"},
            )
    except HTTPException:
        raise
    except Exception:
        # Redis 错误时降级处理，不阻断请求
        pass


@router.post(
    "/register",
    response_model=UserAuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserAuthResponse:
    """
    注册新用户

    - 公开注册只能创建 viewer 用户
    - 管理员创建高权限用户应通过受保护的用户管理端点完成
    """
    repo = UserRepository(db)

    if repo.get_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    valid, msg = validate_password_strength(payload.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    if payload.role != "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration can only create viewer users",
        )

    password_hash = hash_password(payload.password)
    user = repo.create(
        email=payload.email,
        name=payload.name,
        password_hash=password_hash,
        role="viewer",
    )
    return UserAuthResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    用户登录

    - 验证邮箱和密码
    - 应用 Rate Limiting（IP+邮箱）
    - 返回 Access Token 和 Refresh Token
    """
    # Rate limit check
    _check_rate_limit(request, payload.email)

    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)

    # 防止枚举攻击：无论用户存在与否，都使用相同时间
    password_valid = False
    if user and user.password_hash:
        password_valid = verify_password(payload.password, user.password_hash)

    if not user or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact admin.",
        )

    # 更新最后登录时间
    repo.update_last_login(user.id)

    # 生成 Tokens
    access_token, _ = create_access_token(user.id, user.role)
    refresh_token, _ = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    使用 Refresh Token 获取新的 Access Token
    """
    token = payload.refresh_token

    # 检查黑名单
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    try:
        token_payload = decode_token(token, expected_type="refresh")
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    import uuid as uuid_lib

    try:
        user_id = uuid_lib.UUID(token_payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if is_user_token_revoked(
        str(user_id), token_payload.get("issued_at", token_payload.get("iat"))
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # 生成新的 Access Token
    access_token, _ = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=access_token,
        refresh_token=token,  # 保持原 refresh token
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: CurrentUser,
    token: Annotated[str, Depends(oauth2_scheme)],
    payload: Annotated[LogoutRequest | None, Body()] = None,
) -> MessageResponse:
    """
    用户登出

    - 将当前 Access Token 加入黑名单
    - 前端应同时清除 Refresh Token
    """
    blacklist_token(
        token,
        expire_seconds=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )
    revoke_user_tokens(
        str(current_user.id),
        expire_seconds=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
    )
    if payload and payload.refresh_token:
        blacklist_token(
            payload.refresh_token,
            expire_seconds=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
        )
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserAuthResponse)
def get_me(current_user: CurrentUser) -> UserAuthResponse:
    """获取当前登录用户信息"""
    return UserAuthResponse.model_validate(current_user)


@router.put("/password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    修改密码

    - 需要验证当前密码
    - 应用密码强度校验
    """
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not set for this account",
        )

    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from current password",
        )

    valid, msg = validate_password_strength(payload.new_password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    repo = UserRepository(db)
    new_hash = hash_password(payload.new_password)
    repo.update_password(current_user.id, new_hash)

    return MessageResponse(message="Password updated successfully")
