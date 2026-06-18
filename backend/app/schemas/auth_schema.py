"""
Authentication Schemas

认证相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.config import settings

Role = Literal["admin", "developer", "viewer"]


class RegisterRequest(BaseModel):
    """注册请求"""

    email: EmailStr = Field(..., description="用户邮箱")
    name: str = Field(..., min_length=1, max_length=100, description="用户名")
    password: str = Field(
        ...,
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=settings.PASSWORD_MAX_LENGTH,
        description="密码",
    )
    role: Role = Field("viewer", description="用户角色")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "StrongP@ss1",
                "role": "viewer",
            }
        }
    )


class LoginRequest(BaseModel):
    """登录请求"""

    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="密码")

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "user@example.com", "password": "StrongP@ss1"}}
    )


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access Token 有效期（秒）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


class RefreshRequest(BaseModel):
    """刷新 Token 请求"""

    refresh_token: str = Field(..., description="Refresh Token")


class LogoutRequest(BaseModel):
    """登出请求"""

    refresh_token: str | None = Field(None, description="Refresh Token to revoke")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(
        ...,
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=settings.PASSWORD_MAX_LENGTH,
        description="新密码",
    )


class UserAuthResponse(BaseModel):
    """用户信息响应（含认证字段）"""

    id: UUID
    email: EmailStr
    name: str
    role: Role
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
