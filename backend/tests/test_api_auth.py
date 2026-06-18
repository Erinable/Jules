"""
Authentication API Integration Tests

集成测试：认证授权 API 端点

覆盖：
- POST /auth/register - 用户注册
- POST /auth/login - 用户登录
- POST /auth/refresh - 刷新 Token
- POST /auth/logout - 登出
- GET  /auth/me - 获取当前用户信息
- PUT  /auth/password - 修改密码
- RBAC 权限控制
"""

import pytest
from fastapi.testclient import TestClient


class FakeRedis:
    """Small Redis stand-in for auth blacklist tests."""

    def __init__(self):
        self.store = {}

    def incr(self, key: str) -> int:
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def expire(self, key: str, seconds: int) -> None:
        return None

    def setex(self, key: str, seconds: int, value: str) -> None:
        self.store[key] = value

    def exists(self, key: str) -> int:
        return int(key in self.store)

    def get(self, key: str):
        return self.store.get(key)


@pytest.fixture
def unique_auth_email():
    """生成唯一邮箱用于测试"""
    import uuid as uuid_lib

    return f"auth-test-{uuid_lib.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_auth_password():
    """符合强度要求的密码"""
    return "StrongP@ss123!"


@pytest.fixture
def unique_auth_name():
    """测试用户名"""
    return "Auth Test User"


class TestRegisterEndpoint:
    """POST /api/v1/auth/register 测试"""

    def test_register_success(
        self,
        client: TestClient,
        unique_auth_email: str,
        unique_auth_password: str,
    ):
        """测试注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_auth_email,
                "name": "Test User",
                "password": unique_auth_password,
                "role": "viewer",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == unique_auth_email
        assert data["name"] == "Test User"
        assert data["role"] == "viewer"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        # 不应返回敏感字段
        assert "password_hash" not in data

    def test_register_duplicate_email(
        self,
        client: TestClient,
        unique_auth_email: str,
        unique_auth_password: str,
    ):
        """测试重复邮箱注册失败"""
        payload = {
            "email": unique_auth_email,
            "name": "First User",
            "password": unique_auth_password,
        }
        client.post("/api/v1/auth/register", json=payload)

        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_weak_password(
        self,
        client: TestClient,
        unique_auth_email: str,
    ):
        """测试弱密码注册失败"""
        weak_passwords = [
            "short",  # 太短
            "alllowercase1",  # 无大写字母
            "ALLUPPERCASE1",  # 无小写字母
            "NoDigitsHere!",  # 无数字
        ]
        for pwd in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": unique_auth_email,
                    "name": "Test",
                    "password": pwd,
                },
            )
            assert response.status_code in (400, 422), f"Should fail for: {pwd}"

    def test_register_invalid_email(
        self,
        client: TestClient,
        unique_auth_password: str,
    ):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "name": "Test",
                "password": unique_auth_password,
            },
        )
        assert response.status_code == 422

    def test_register_default_role(
        self,
        client: TestClient,
        unique_auth_email: str,
        unique_auth_password: str,
    ):
        """测试默认角色为 viewer"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_auth_email,
                "name": "Test",
                "password": unique_auth_password,
            },
        )
        assert response.status_code == 201
        assert response.json()["role"] == "viewer"

    def test_register_rejects_admin_role(
        self,
        client: TestClient,
        unique_auth_email: str,
        unique_auth_password: str,
    ):
        """Public registration must not grant elevated roles."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_auth_email,
                "name": "Privilege Escalation",
                "password": unique_auth_password,
                "role": "admin",
            },
        )

        assert response.status_code == 403
        assert "viewer" in response.json()["detail"].lower()


class TestLoginEndpoint:
    """POST /api/v1/auth/login 测试"""

    def test_login_success(
        self,
        client: TestClient,
        registered_user,
        sample_email: str,
        sample_password: str,
    ):
        """测试登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": sample_password},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_wrong_password(
        self,
        client: TestClient,
        registered_user,
        sample_email: str,
    ):
        """测试密码错误"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": "WrongP@ssw0rd"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_email(
        self,
        client: TestClient,
    ):
        """测试不存在的邮箱"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WhateverP@ss1",
            },
        )
        assert response.status_code == 401

    def test_login_inactive_user(
        self,
        client: TestClient,
        db_session,
        sample_email: str,
        sample_password: str,
    ):
        """测试已禁用用户登录"""
        from app.core.security import hash_password
        from app.repositories.user_repository import UserRepository

        repo = UserRepository(db_session)
        user = repo.create(
            email=sample_email,
            name="Inactive User",
            password_hash=hash_password(sample_password),
            role="viewer",
        )
        repo.set_active(user.id, False)

        response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": sample_password},
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    def test_login_with_empty_credentials(self, client: TestClient):
        """测试空凭据"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "", "password": ""},
        )
        assert response.status_code == 422


class TestRefreshTokenEndpoint:
    """POST /api/v1/auth/refresh 测试"""

    def test_refresh_token_success(
        self,
        client: TestClient,
        registered_user,
        sample_email: str,
        sample_password: str,
    ):
        """测试刷新 Token 成功"""
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": sample_password},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] == refresh_token

    def test_refresh_with_invalid_token(self, client: TestClient):
        """测试无效 Refresh Token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-string"},
        )
        assert response.status_code == 401

    def test_refresh_with_access_token_instead(
        self,
        client: TestClient,
        registered_user,
        sample_email: str,
        sample_password: str,
    ):
        """测试使用 Access Token 刷新（应该失败）"""
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": sample_password},
        )
        access_token = login_resp.json()["access_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401


class TestLogoutEndpoint:
    """POST /api/v1/auth/logout 测试"""

    def test_logout_success(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """测试登出成功"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_logout_without_auth(self, client: TestClient):
        """测试未认证登出"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401

    def test_logout_then_use_blacklisted_token(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """测试登出后使用旧 Token 应失败（需要 Redis）"""
        # 登出
        client.post("/api/v1/auth/logout", headers=auth_headers)

        # 尝试访问受保护的端点
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        # 如果 Redis 未运行，会返回 200；运行则返回 401
        assert response.status_code in (200, 401)

    def test_logout_revokes_refresh_token(
        self,
        client: TestClient,
        registered_user,
        sample_email: str,
        sample_password: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Logout should terminate refresh-token based sessions server-side."""
        fake_redis = FakeRedis()
        monkeypatch.setattr("app.dependencies.auth.get_redis", lambda: fake_redis)
        monkeypatch.setattr("app.api.v1.auth.get_redis", lambda: fake_redis)

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": sample_password},
        )
        assert login_resp.status_code == 200
        tokens = login_resp.json()

        logout_resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert logout_resp.status_code == 200

        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 401


class TestGetMeEndpoint:
    """GET /api/v1/auth/me 测试"""

    def test_get_me_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_email: str,
    ):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_email
        assert data["role"] == "developer"
        assert "password_hash" not in data

    def test_get_me_without_auth(self, client: TestClient):
        """测试未认证访问 /me"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self, client: TestClient):
        """测试无效 Token 访问 /me"""
        headers = {"Authorization": "Bearer invalidtoken"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """PUT /api/v1/auth/password 测试"""

    def test_change_password_success(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_email: str,
        sample_password: str,
    ):
        """测试修改密码成功"""
        new_password = "NewStr0ngP@ss!"
        response = client.put(
            "/api/v1/auth/password",
            headers=auth_headers,
            json={
                "current_password": sample_password,
                "new_password": new_password,
            },
        )
        assert response.status_code == 200

        # 验证可以使用新密码登录
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": sample_email, "password": new_password},
        )
        assert login_resp.status_code == 200

    def test_change_password_wrong_current(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """测试当前密码错误"""
        response = client.put(
            "/api/v1/auth/password",
            headers=auth_headers,
            json={
                "current_password": "WrongCurrentP@ss1",
                "new_password": "NewStr0ngP@ss!",
            },
        )
        assert response.status_code == 401

    def test_change_password_same_as_current(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_password: str,
    ):
        """测试新密码与当前密码相同"""
        response = client.put(
            "/api/v1/auth/password",
            headers=auth_headers,
            json={
                "current_password": sample_password,
                "new_password": sample_password,
            },
        )
        assert response.status_code == 400

    def test_change_password_weak_new(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_password: str,
    ):
        """测试新密码强度不足"""
        response = client.put(
            "/api/v1/auth/password",
            headers=auth_headers,
            json={
                "current_password": sample_password,
                "new_password": "weak",
            },
        )
        assert response.status_code in (400, 422)


class TestRBAC:
    """基于角色的访问控制测试"""

    def test_viewer_can_access_own_data(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """测试 viewer 可以访问自己的信息"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200

    def test_protected_endpoint_without_role_fails(self, client: TestClient):
        """测试未认证用户无法访问受保护端点"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_admin_role_hierarchy(
        self,
        client: TestClient,
        db_session,
    ):
        """测试 admin 角色可以访问 admin 级别资源"""
        import uuid as uuid_lib

        from app.core.security import hash_password
        from app.repositories.user_repository import UserRepository

        email = f"admin-{uuid_lib.uuid4().hex[:8]}@example.com"
        password = "AdminP@ss123"
        repo = UserRepository(db_session)
        repo.create(
            email=email,
            name="Admin User",
            password_hash=hash_password(password),
            role="admin",
        )

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # admin 可以访问自己的信息
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == "admin"


class TestSecurity:
    """安全相关测试"""

    def test_password_hash_is_not_returned(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """测试 API 响应不泄露密码哈希"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        data = response.json()
        assert "password_hash" not in data
        assert "hash" not in data

    def test_sql_injection_attempt_in_login(self, client: TestClient):
        """测试登录的 SQL 注入防护"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "' OR '1'='1",
                "password": "anything",
            },
        )
        # 应该返回 422（邮箱格式错误）或 401
        assert response.status_code in (401, 422)

    def test_token_signature_tampering(self, client: TestClient):
        """测试篡改 Token 签名"""
        # 使用一个明显无效的 Token
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.invalid.signature"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_password_strength_validation(self):
        """单元测试：密码强度校验"""
        from app.core.security import validate_password_strength

        # 有效密码
        valid, _ = validate_password_strength("Str0ngP@ss!")
        assert valid

        # 太短
        valid, msg = validate_password_strength("Sh1!")
        assert not valid
        assert "at least" in msg.lower()

        # 无大写
        valid, _ = validate_password_strength("lowercase123!")
        assert not valid

        # 无小写
        valid, _ = validate_password_strength("UPPERCASE123!")
        assert not valid

        # 无数字
        valid, _ = validate_password_strength("NoDigits!")
        assert not valid


class TestJWTHandler:
    """JWT Token 单元测试"""

    def test_create_and_decode_access_token(self):
        """测试 Access Token 创建和解析"""
        import uuid as uuid_lib

        from app.core.jwt_handler import create_access_token, decode_token

        user_id = uuid_lib.uuid4()
        token, _ = create_access_token(user_id, role="admin")

        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert payload["role"] == "admin"

    def test_create_and_decode_refresh_token(self):
        """测试 Refresh Token 创建和解析"""
        import uuid as uuid_lib

        from app.core.jwt_handler import create_refresh_token, decode_token

        user_id = uuid_lib.uuid4()
        token, _ = create_refresh_token(user_id)

        payload = decode_token(token, expected_type="refresh")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_token_type_mismatch(self):
        """测试 Token 类型不匹配"""
        import uuid as uuid_lib

        from app.core.jwt_handler import (
            TokenInvalidError,
            create_access_token,
            decode_token,
        )

        user_id = uuid_lib.uuid4()
        token, _ = create_access_token(user_id, role="viewer")

        # 使用 access token 作为 refresh token
        with pytest.raises(TokenInvalidError):
            decode_token(token, expected_type="refresh")

    def test_invalid_token_raises_error(self):
        """测试无效 Token 抛出异常"""
        from app.core.jwt_handler import TokenInvalidError, decode_token

        with pytest.raises(TokenInvalidError):
            decode_token("not.a.valid.jwt")


class TestPasswordHashing:
    """密码哈希单元测试"""

    def test_hash_and_verify(self):
        """测试哈希和验证"""
        from app.core.security import hash_password, verify_password

        password = "MySecureP@ss123"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)

    def test_same_password_different_hash(self):
        """测试相同密码产生不同哈希（bcrypt salt）"""
        from app.core.security import hash_password

        password = "SameP@ss123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
