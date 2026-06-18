"""
JWT Token Handler

JWT Token 生成、解析、验证
"""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings

TokenType = Literal["access", "refresh"]


class TokenError(Exception):
    """Token 相关错误"""


class TokenExpiredError(TokenError):
    """Token 已过期"""


class TokenInvalidError(TokenError):
    """Token 无效"""


def create_token(
    user_id: UUID,
    token_type: TokenType = "access",
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, datetime]:
    """
    创建 JWT Token

    Args:
        user_id: 用户 ID（写入 sub claim）
        token_type: Token 类型（access/refresh）
        extra_claims: 额外的 claim（如 role）

    Returns:
        tuple[str, datetime]: (encoded_jwt, expires_at)
    """
    now = datetime.now(UTC)
    delta = (
        settings.access_token_expire_delta
        if token_type == "access"
        else settings.refresh_token_expire_delta
    )
    expire = now + delta

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "issued_at": now.timestamp(),
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded, expire


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """
    解析并验证 JWT Token

    Args:
        token: JWT Token 字符串
        expected_type: 期望的 Token 类型（可选）

    Returns:
        dict[str, Any]: Token payload

    Raises:
        TokenExpiredError: Token 已过期
        TokenInvalidError: Token 无效或类型不匹配
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token has expired") from exc
    except JWTError as exc:
        raise TokenInvalidError(f"Invalid token: {exc}") from exc

    if expected_type and payload.get("type") != expected_type:
        raise TokenInvalidError(
            f"Expected token type '{expected_type}', got '{payload.get('type')}'"
        )

    return payload


def create_access_token(user_id: UUID, role: str) -> tuple[str, datetime]:
    """创建 Access Token（含 role claim）"""
    return create_token(
        user_id,
        token_type="access",
        extra_claims={"role": role},
    )


def create_refresh_token(user_id: UUID) -> tuple[str, datetime]:
    """创建 Refresh Token"""
    return create_token(user_id, token_type="refresh")
