# Jules API v1 Documentation

完整的 RESTful API 文档，涵盖所有端点的详细说明、请求/响应示例和错误处理。

## 目录

- [API 概览](#api-概览)
- [认证和授权](#认证和授权)
- [通用参数](#通用参数)
- [错误码说明](#错误码说明)
- [API 端点](#api-端点)
  - [用户管理 (Users)](#用户管理-users)
  - [任务管理 (Tasks)](#任务管理-tasks)
  - [Agent 配置 (Agents)](#agent-配置-agents)
  - [执行记录 (Executions)](#执行记录-executions)
  - [代码文件 (Code Files)](#代码文件-code-files)
  - [质量指标 (Quality Metrics)](#质量指标-quality-metrics)
  - [健康检查 (Health)](#健康检查-health)

---

## API 概览

**Base URL**: `http://localhost:8000/api/v1`

**支持的格式**: JSON

**API 版本**: v1

**交互式文档**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 请求头

所有请求必须包含：

```http
Content-Type: application/json
Accept: application/json
```

---

## 认证和授权

> **注意**: 当前版本暂未实现认证系统。未来将支持 JWT Token 认证。

**计划中的认证方式**:

```http
Authorization: Bearer <jwt_token>
```

---

## 通用参数

### 分页参数

适用于所有 `GET` 列表端点：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `skip` | integer | 0 | 跳过的记录数 |
| `limit` | integer | 100 | 返回的最大记录数 |

**示例**:

```http
GET /api/v1/users/?skip=0&limit=10
```

### 过滤参数

部分端点支持过滤（具体参数见各端点说明）：

```http
GET /api/v1/tasks/?status=pending&priority_min=5
```

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 204 | 请求成功，无返回内容 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "detail": "Error message here"
}
```

**422 验证错误示例**:

```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "email"],
      "msg": "Input should be a valid string",
      "input": 123
    }
  ]
}
```

---

## API 端点

### 用户管理 (Users)

#### 1. 获取用户列表

```http
GET /api/v1/users/
```

**查询参数**:
- `skip` (integer, 可选): 跳过的记录数，默认 0
- `limit` (integer, 可选): 返回的最大记录数，默认 100

**响应 200**:

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "created_at": "2026-06-17T00:00:00Z",
    "updated_at": "2026-06-17T00:00:00Z"
  }
]
```

---

#### 2. 创建用户

```http
POST /api/v1/users/
```

**请求体**:

```json
{
  "email": "newuser@example.com",
  "username": "new_user"
}
```

**响应 201**:

```json
{
  "id": 2,
  "email": "newuser@example.com",
  "username": "new_user",
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T00:00:00Z"
}
```

**错误 422** (邮箱已存在):

```json
{
  "detail": "Email already registered"
}
```

---

#### 3. 获取用户详情

```http
GET /api/v1/users/{user_id}
```

**路径参数**:
- `user_id` (integer, 必需): 用户ID

**响应 200**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T00:00:00Z"
}
```

**错误 404**:

```json
{
  "detail": "User not found"
}
```

---

#### 4. 更新用户

```http
PUT /api/v1/users/{user_id}
```

**请求体**:

```json
{
  "email": "updated@example.com",
  "username": "updated_user"
}
```

**响应 200**:

```json
{
  "id": 1,
  "email": "updated@example.com",
  "username": "updated_user",
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T01:00:00Z"
}
```

---

#### 5. 删除用户

```http
DELETE /api/v1/users/{user_id}
```

**响应 204**: 无内容

**错误 404**:

```json
{
  "detail": "User not found"
}
```

---

### 任务管理 (Tasks)

#### 1. 获取任务列表

```http
GET /api/v1/tasks/
```

**查询参数**:
- `skip` (integer, 可选): 跳过的记录数，默认 0
- `limit` (integer, 可选): 返回的最大记录数，默认 100
- `status` (string, 可选): 任务状态筛选 (`pending`, `in_progress`, `completed`, `failed`)

**响应 200**:

```json
[
  {
    "id": 1,
    "title": "Generate user authentication module",
    "description": "Create a complete user auth system with JWT",
    "status": "pending",
    "priority": 8,
    "assigned_to": 1,
    "created_at": "2026-06-17T00:00:00Z",
    "updated_at": "2026-06-17T00:00:00Z"
  }
]
```

---

#### 2. 创建任务

```http
POST /api/v1/tasks/
```

**请求体**:

```json
{
  "title": "Generate API documentation",
  "description": "Auto-generate OpenAPI docs from FastAPI endpoints",
  "priority": 7,
  "assigned_to": 1
}
```

**字段说明**:
- `title` (string, 必需): 任务标题（1-200字符）
- `description` (string, 可选): 任务描述
- `priority` (integer, 必需): 优先级（0-10）
- `assigned_to` (integer, 可选): 分配给的用户ID

**响应 201**:

```json
{
  "id": 2,
  "title": "Generate API documentation",
  "description": "Auto-generate OpenAPI docs from FastAPI endpoints",
  "status": "pending",
  "priority": 7,
  "assigned_to": 1,
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T00:00:00Z"
}
```

---

#### 3. 获取任务详情

```http
GET /api/v1/tasks/{task_id}
```

**响应 200**:

```json
{
  "id": 1,
  "title": "Generate user authentication module",
  "description": "Create a complete user auth system with JWT",
  "status": "in_progress",
  "priority": 8,
  "assigned_to": 1,
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T01:00:00Z",
  "started_at": "2026-06-17T00:30:00Z",
  "completed_at": null
}
```

---

#### 4. 更新任务

```http
PUT /api/v1/tasks/{task_id}
```

**请求体**:

```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "priority": 9,
  "assigned_to": 2
}
```

**响应 200**: 返回更新后的任务对象

---

#### 5. 更新任务状态

```http
PATCH /api/v1/tasks/{task_id}/status
```

**请求体**:

```json
{
  "status": "completed"
}
```

**可用状态**:
- `pending`: 待处理
- `in_progress`: 进行中
- `completed`: 已完成
- `failed`: 失败

**响应 200**:

```json
{
  "id": 1,
  "status": "completed",
  "completed_at": "2026-06-17T02:00:00Z"
}
```

---

#### 6. 删除任务

```http
DELETE /api/v1/tasks/{task_id}
```

**响应 204**: 无内容

---

### Agent 配置 (Agents)

#### 1. 获取 Agent 列表

```http
GET /api/v1/agents/
```

**查询参数**:
- `skip` (integer, 可选)
- `limit` (integer, 可选)

**响应 200**:

```json
[
  {
    "id": 1,
    "name": "CodeGeneratorAgent",
    "type": "code_generator",
    "config": {
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.7,
      "max_tokens": 4096
    },
    "is_active": true,
    "created_at": "2026-06-17T00:00:00Z",
    "updated_at": "2026-06-17T00:00:00Z"
  }
]
```

---

#### 2. 创建 Agent

```http
POST /api/v1/agents/
```

**请求体**:

```json
{
  "name": "CodeReviewerAgent",
  "type": "code_reviewer",
  "config": {
    "model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 2048,
    "focus_areas": ["security", "performance", "readability"]
  },
  "is_active": true
}
```

**字段说明**:
- `name` (string, 必需): Agent 名称
- `type` (string, 必需): Agent 类型 (`code_generator`, `code_reviewer`, `code_analyzer`, `tester`)
- `config` (object, 必需): Agent 配置（JSON 格式）
- `is_active` (boolean, 可选): 是否激活，默认 true

**响应 201**: 返回创建的 Agent 对象

---

#### 3. 获取 Agent 详情

```http
GET /api/v1/agents/{agent_id}
```

**响应 200**: 返回 Agent 对象

---

#### 4. 更新 Agent

```http
PUT /api/v1/agents/{agent_id}
```

**请求体**: 同创建 Agent

**响应 200**: 返回更新后的 Agent 对象

---

#### 5. 删除 Agent

```http
DELETE /api/v1/agents/{agent_id}
```

**响应 204**: 无内容

---

#### 6. 执行 Agent 任务

```http
POST /api/v1/agents/execute
```

**请求体**:

```json
{
  "agent_id": 1,
  "task_id": 5,
  "input_data": {
    "prompt": "Generate a REST API for user management",
    "language": "python",
    "framework": "fastapi"
  }
}
```

**响应 201**:

```json
{
  "execution_id": 10,
  "agent_id": 1,
  "task_id": 5,
  "status": "running",
  "started_at": "2026-06-17T03:00:00Z",
  "message": "Agent execution started successfully"
}
```

---

### 执行记录 (Executions)

#### 1. 获取执行记录列表

```http
GET /api/v1/executions/
```

**查询参数**:
- `skip` (integer, 可选)
- `limit` (integer, 可选)
- `task_id` (integer, 可选): 按任务ID过滤
- `status` (string, 可选): 按状态过滤

**响应 200**:

```json
[
  {
    "id": 1,
    "agent_id": 1,
    "task_id": 5,
    "status": "completed",
    "input_data": {...},
    "output_data": {...},
    "started_at": "2026-06-17T03:00:00Z",
    "completed_at": "2026-06-17T03:05:30Z",
    "execution_time_seconds": 330.5
  }
]
```

---

#### 2. 创建执行记录

```http
POST /api/v1/executions/
```

**请求体**:

```json
{
  "agent_id": 1,
  "task_id": 5,
  "input_data": {
    "prompt": "Generate user authentication",
    "context": {}
  }
}
```

**响应 201**: 返回创建的执行记录

---

#### 3. 获取执行详情

```http
GET /api/v1/executions/{execution_id}
```

**响应 200**: 返回执行记录详情，包含完整的 input/output 数据

---

#### 4. 更新执行状态

```http
PATCH /api/v1/executions/{execution_id}/status
```

**请求体**:

```json
{
  "status": "completed",
  "output_data": {
    "generated_code": "...",
    "metrics": {...}
  }
}
```

**可用状态**:
- `pending`: 待执行
- `running`: 执行中
- `completed`: 已完成
- `failed`: 失败

**响应 200**: 返回更新后的执行记录

---

#### 5. 删除执行记录

```http
DELETE /api/v1/executions/{execution_id}
```

**响应 204**: 无内容

---

### 代码文件 (Code Files)

#### 1. 获取代码文件列表

```http
GET /api/v1/code-files/
```

**查询参数**:
- `skip` (integer, 可选)
- `limit` (integer, 可选)
- `project_id` (integer, 可选): 按项目ID过滤

**响应 200**:

```json
[
  {
    "id": 1,
    "project_id": 1,
    "file_path": "app/main.py",
    "content": "from fastapi import FastAPI\n...",
    "file_hash": "abc123def456",
    "language": "python",
    "created_at": "2026-06-17T00:00:00Z",
    "updated_at": "2026-06-17T01:00:00Z"
  }
]
```

---

#### 2. 创建代码文件

```http
POST /api/v1/code-files/
```

**请求体**:

```json
{
  "project_id": 1,
  "file_path": "app/models/user.py",
  "content": "from sqlalchemy import Column, Integer, String\n...",
  "language": "python"
}
```

**响应 201**: 返回创建的代码文件对象

---

#### 3. 获取代码文件详情

```http
GET /api/v1/code-files/{file_id}
```

**响应 200**: 返回完整的代码文件对象

---

#### 4. 更新代码文件

```http
PUT /api/v1/code-files/{file_id}
```

**请求体**:

```json
{
  "content": "updated file content...",
  "language": "python"
}
```

**响应 200**: 返回更新后的代码文件

---

#### 5. 删除代码文件

```http
DELETE /api/v1/code-files/{file_id}
```

**响应 204**: 无内容

---

#### 6. 获取文件版本历史

```http
GET /api/v1/code-files/{file_id}/versions
```

**响应 200**:

```json
[
  {
    "id": 1,
    "code_file_id": 1,
    "version_number": 2,
    "content": "previous version content...",
    "file_hash": "old_hash_123",
    "created_at": "2026-06-17T00:00:00Z",
    "created_by": 1
  }
]
```

---

### 质量指标 (Quality Metrics)

#### 1. 获取质量指标列表

```http
GET /api/v1/quality/
```

**查询参数**:
- `skip` (integer, 可选)
- `limit` (integer, 可选)

**响应 200**:

```json
[
  {
    "id": 1,
    "project_id": 1,
    "avg_complexity": 5.2,
    "maintainability_index": 75.8,
    "test_coverage": 85.5,
    "security_issues": 0,
    "code_smells": 3,
    "measured_at": "2026-06-17T03:00:00Z"
  }
]
```

---

#### 2. 创建质量指标

```http
POST /api/v1/quality/
```

**请求体**:

```json
{
  "project_id": 1,
  "avg_complexity": 6.1,
  "maintainability_index": 72.3,
  "test_coverage": 88.0,
  "security_issues": 1,
  "code_smells": 5
}
```

**响应 201**: 返回创建的质量指标对象

---

#### 3. 获取最新质量指标

```http
GET /api/v1/quality/latest
```

**查询参数**:
- `project_id` (integer, 可选): 按项目ID过滤

**响应 200**: 返回最新的质量指标对象

---

#### 4. 删除质量指标

```http
DELETE /api/v1/quality/{metric_id}
```

**响应 204**: 无内容

---

### 健康检查 (Health)

#### 1. 系统健康状态

```http
GET /health
```

**响应 200**:

```json
{
  "status": "healthy",
  "timestamp": "2026-06-17T03:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

**响应 503** (不健康):

```json
{
  "status": "unhealthy",
  "timestamp": "2026-06-17T03:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "error",
    "redis": "ok"
  }
}
```

---

#### 2. 就绪状态（Readiness）

```http
GET /health/ready
```

检查系统是否准备好接受流量（数据库连接等）。

**响应 200**: 系统就绪

**响应 503**: 系统未就绪

---

#### 3. 存活状态（Liveness）

```http
GET /health/live
```

检查应用是否存活（用于容器健康检查）。

**响应 200**: 应用存活

**响应 503**: 应用需要重启

---

## 使用示例

### cURL 示例

```bash
# 获取用户列表
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Content-Type: application/json"

# 创建任务
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New task",
    "description": "Task description",
    "priority": 8,
    "assigned_to": 1
  }'

# 执行 Agent
curl -X POST "http://localhost:8000/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "task_id": 5,
    "input_data": {
      "prompt": "Generate code",
      "language": "python"
    }
  }'
```

### Python 示例

```python
import httpx

# 创建异步客户端
async with httpx.AsyncClient() as client:
    # 获取任务列表
    response = await client.get(
        "http://localhost:8000/api/v1/tasks/",
        params={"skip": 0, "limit": 10}
    )
    tasks = response.json()
    
    # 创建新任务
    response = await client.post(
        "http://localhost:8000/api/v1/tasks/",
        json={
            "title": "Generate auth module",
            "priority": 8,
            "assigned_to": 1
        }
    )
    new_task = response.json()
    
    # 执行 Agent
    response = await client.post(
        "http://localhost:8000/api/v1/agents/execute",
        json={
            "agent_id": 1,
            "task_id": new_task["id"],
            "input_data": {"prompt": "Generate code"}
        }
    )
```

### JavaScript/TypeScript 示例

```typescript
// 使用 Axios
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 获取任务列表
const tasks = await apiClient.get('/tasks/', {
  params: { skip: 0, limit: 10 }
});

// 创建任务
const newTask = await apiClient.post('/tasks/', {
  title: 'Generate auth module',
  priority: 8,
  assigned_to: 1,
});

// 执行 Agent
const execution = await apiClient.post('/agents/execute', {
  agent_id: 1,
  task_id: newTask.data.id,
  input_data: { prompt: 'Generate code' },
});
```

---

## 速率限制

> **注意**: 当前版本暂未实现速率限制。未来版本将添加。

**计划中的速率限制**:
- 每分钟 60 次请求（未认证用户）
- 每分钟 600 次请求（认证用户）

---

## 版本控制

API 版本通过 URL 路径指定：`/api/v1/`

**废弃策略**:
- 新版本发布后，旧版本至少维护 6 个月
- 废弃通知将在响应头中包含 `Deprecation` 和 `Sunset` 字段

---

## 变更日志

### v1.0.0 (2026-06-17)

- 初始版本发布
- 包含 7 个主要模块（Users, Tasks, Agents, Executions, Code Files, Quality, Health）
- 39 个 API 端点
- 完整的 CRUD 操作

---

## 支持和反馈

- **问题反馈**: https://github.com/your-org/jules/issues
- **API 文档**: http://localhost:8000/docs
- **邮箱**: api-support@jules-ai.dev

---

**最后更新**: 2026-06-17
