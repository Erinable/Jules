# 认证系统集成指南

本文档说明如何将认证系统集成到 Jules 前端应用。

## 文件结构

```
frontend/src/
├── contexts/
│   └── AuthContext.tsx          # 认证上下文（状态管理）
├── hooks/
│   └── useAuth.ts               # 认证 Hook（便捷访问）
├── components/
│   └── ProtectedRoute.tsx       # 受保护路由组件
├── pages/
│   ├── LoginPage.tsx            # 登录页面
│   ├── RegisterPage.tsx         # 注册页面
│   └── HomePage.tsx             # 首页（示例）
└── App.tsx                      # 应用入口（需要更新）
```

## 集成步骤

### 1. 安装依赖

确保已安装以下 npm 包：

```bash
npm install react-router-dom
```

### 2. 更新 App.tsx

使用 `App.example.tsx` 作为参考，更新您的 `App.tsx`：

```tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

// 导入您的页面组件
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* 受保护路由 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />

          {/* 其他受保护路由 */}
          {/* ... */}

          {/* 404 重定向 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

### 3. 使用 useAuth Hook

在任何组件中使用认证功能：

```tsx
import { useAuth } from "@/hooks/useAuth";

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // 显示用户信息
  if (isAuthenticated) {
    return <div>欢迎, {user?.name}!</div>;
  }

  return <div>请登录</div>;
}
```

## API 集成

### 后端端点

认证系统集成以下后端 API 端点：

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `POST /api/v1/auth/logout` - 登出

### Token 存储

Token 自动存储在 `localStorage` 中：

- `access_token` - 访问令牌（有效期 30 分钟）
- `refresh_token` - 刷新令牌（有效期 7 天）
- `user` - 用户信息（JSON 字符串）

### 自动刷新

AuthContext 会在以下情况自动刷新 Token：

1. 初始化时（如果有 refresh_token）
2. 每 25 分钟自动刷新一次（Token 有效期为 30 分钟）
3. 如果刷新失败，自动登出

## 功能特性

### ✅ 已实现

- [x] 用户登录
- [x] 用户注册
- [x] Token 自动存储到 LocalStorage
- [x] 未登录用户自动重定向到 /login
- [x] Token 自动刷新（每 25 分钟）
- [x] 登出功能
- [x] 受保护路由（ProtectedRoute）
- [x] 加载状态处理
- [x] 错误处理和用户提示
- [x] 登录后重定向到原页面

### ⏳ 待实现

- [ ] 忘记密码功能
- [ ] 邮箱验证
- [ ] 双因素认证（2FA）
- [ ] 记住我功能（持久化登录）
- [ ] 密码强度指示器
- [ ] 社交登录（OAuth）

## 安全性

### Token 管理

- Access Token 有效期：30 分钟
- Refresh Token 有效期：7 天
- Token 存储在 localStorage（仅用于开发，生产环境建议使用 HttpOnly Cookie）

### 密码验证

- 最小长度：8 个字符
- 前端验证：密码确认匹配
- 后端验证：密码强度检查（后端实现）

### 速率限制

- 后端实现登录频率限制（每分钟最多 5 次尝试）
- 429 错误时显示 "请稍后重试" 提示

## 测试

### 手动测试步骤

1. **注册新用户**
   - 访问 `/register`
   - 填写表单（邮箱、姓名、密码）
   - 点击"注册"
   - 应重定向到首页

2. **登录**
   - 访问 `/login`
   - 输入注册的邮箱和密码
   - 点击"登录"
   - 应重定向到首页

3. **受保护路由**
   - 未登录时访问 `/`
   - 应自动重定向到 `/login`
   - 登录后应重定向回原页面

4. **登出**
   - 点击"退出登录"按钮
   - 应重定向到登录页面
   - Token 应从 localStorage 清除

5. **Token 刷新**
   - 保持登录状态超过 25 分钟
   - Token 应自动刷新
   - 无需重新登录

### 单元测试

待编写（使用 Jest + React Testing Library）。

## 故障排查

### 常见问题

**Q: 登录后仍显示未认证**
A: 检查 localStorage 中是否存储了 `access_token` 和 `user`。清除浏览器缓存后重试。

**Q: Token 刷新失败**
A: 确保后端 `/api/v1/auth/refresh` 端点正常工作。检查 refresh_token 是否过期（7 天）。

**Q: 跨域问题（CORS）**
A: 确保后端配置了正确的 CORS 设置，允许前端域名访问。

**Q: 登录后重定向到错误页面**
A: 检查 `useLocation` 的 `state.from` 是否正确传递。

## 生产环境注意事项

### 安全建议

1. **使用 HttpOnly Cookie 存储 Token**（而非 localStorage）
   - 防止 XSS 攻击
   - 需要后端配合

2. **启用 HTTPS**
   - 所有 API 请求必须通过 HTTPS

3. **实现 CSRF 保护**
   - 使用 CSRF Token

4. **Token 过期策略**
   - Access Token: 15-30 分钟
   - Refresh Token: 7-30 天

5. **日志审计**
   - 记录所有登录/登出事件
   - 监控异常登录行为

### 性能优化

1. **懒加载页面组件**

   ```tsx
   const LoginPage = lazy(() => import("@/pages/LoginPage"));
   ```

2. **预加载关键资源**
   - 登录页面样式
   - 认证相关脚本

3. **减少 localStorage 读写**
   - 使用内存缓存（状态管理）

## 参考资源

- [FastAPI 认证文档](https://fastapi.tiangolo.com/tutorial/security/)
- [React Router v6 文档](https://reactrouter.com/)
- [JWT 最佳实践](https://tools.ietf.org/html/rfc8725)

---

**最后更新**: 2026-06-17
**版本**: 1.0.0
