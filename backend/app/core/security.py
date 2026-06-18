"""
Password Hashing Utility

使用 bcrypt 进行密码哈希和验证
"""

from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(password: str) -> str:
    """
    生成密码哈希

    Args:
        password: 原始密码

    Returns:
        str: 密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 待验证的密码
        hashed_password: 数据库中的密码哈希

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度

    Args:
        password: 密码字符串

    Returns:
        tuple[bool, str]: (是否通过, 错误信息)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return (
            False,
            f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters",
        )

    if len(password) > settings.PASSWORD_MAX_LENGTH:
        return (
            False,
            f"Password must be at most {settings.PASSWORD_MAX_LENGTH} characters",
        )

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, ""
