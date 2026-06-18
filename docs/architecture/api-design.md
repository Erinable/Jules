# API 设计

**版本**: v1.0
**日期**: 2026-06-16

---

## 1. API 架构

### 1.1 API 分层

```
/api/v1/
├── /auth          # 认证授权
├── /projects      # 项目管理
├── /tasks         # 任务管理
├── /code          # 代码操作
├── /quality       # 质量检查
├── /agents        # Agent 工作流
└── /stream        # SSE 流式接口
```

---

## 2. RESTful API 端点

### 2.1 项目管理

#### 创建项目

```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "User Management API",
  "type": "web",
  "requirement": "创建用户 CRUD API，使用 FastAPI + SQLAlchemy"
}

Response 201:
{
  "id": "uuid",
  "name": "User Management API",
  "type": "web",
  "status": "pending",
  "created_at": "2026-06-16T10:00:00Z"
}
```

#### 获取项目列表

```http
GET /api/v1/projects?limit=10&offset=0

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "name": "Project Name",
      "type": "web",
      "status": "completed",
      "created_at": "2026-06-16T10:00:00Z"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

#### 获取项目详情

```http
GET /api/v1/projects/{project_id}

Response 200:
{
  "id": "uuid",
  "name": "User Management API",
  "type": "web",
  "status": "completed",
  "config": {...},
  "quality_metrics": {
    "avg_complexity": 5.2,
    "maintainability_index": 78.5,
    "test_coverage": 85.0
  },
  "files": [
    {"path": "app/main.py", "lines": 150},
    {"path": "app/models.py", "lines": 80}
  ]
}
```

### 2.2 代码生成

#### 启动代码生成

```http
POST /api/v1/projects/{project_id}/generate
Content-Type: application/json

{
  "task": "添加用户权限管理功能"
}

Response 202:
{
  "task_id": "uuid",
  "status": "pending",
  "message": "任务已加入队列"
}
```

### 2.3 质量检查

#### 执行质量检查

```http
POST /api/v1/quality/check
Content-Type: application/json

{
  "project_id": "uuid",
  "files": {
    "app/main.py": "code content..."
  }
}

Response 200:
{
  "passed": false,
  "issues": [
    {
      "tool": "ruff",
      "severity": "high",
      "file": "app/main.py",
      "line": 42,
      "message": "Line too long (120 > 88 characters)",
      "rule_id": "E501"
    }
  ],
  "metrics": {
    "avg_complexity": 8.5,
    "maintainability_index": 65.2
  }
}
```

### 2.4 Agent 工作流

#### 获取工作流状态

```http
GET /api/v1/agents/workflow/{task_id}

Response 200:
{
  "task_id": "uuid",
  "status": "in_progress",
  "current_agent": "coder",
  "progress": 60,
  "agents": [
    {"name": "researcher", "status": "completed", "duration": 15.2},
    {"name": "planner", "status": "completed", "duration": 22.5},
    {"name": "coder", "status": "in_progress", "duration": null}
  ]
}
```

---

## 3. Server-Sent Events (SSE)

### 3.1 实时代码生成进度

```http
GET /api/v1/stream/generate/{project_id}
Accept: text/event-stream

Response:
event: agent_start
data: {"agent": "researcher", "timestamp": "2026-06-16T10:00:00Z"}

event: agent_progress
data: {"agent": "researcher", "progress": 50, "message": "正在分析需求..."}

event: agent_complete
data: {"agent": "researcher", "duration": 15.2, "output": "..."}

event: code_generated
data: {"file": "app/main.py", "lines": 150}

event: quality_check
data: {"passed": true, "metrics": {...}}

event: complete
data: {"status": "success", "total_duration": 125.5}
```

### 3.2 FastAPI 实现

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.get("/api/v1/stream/generate/{project_id}")
async def stream_generate(project_id: str):
    async def event_generator():
        # 订阅 Redis 发布/订阅
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"project:{project_id}:events")

        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                yield f"data: {data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## 4. WebSocket API

### 4.1 实时聊天

```javascript
// 前端代码
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat/{project_id}')

// 发送消息
ws.send(JSON.stringify({
  type: 'user_message',
  content: '帮我添加用户登录功能'
}))

// 接收消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log(data.content)  // AI 响应
}
```

### 4.2 FastAPI WebSocket 实现

```python
from fastapi import WebSocket

@app.websocket("/api/v1/ws/chat/{project_id}")
async def chat_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()

    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_json()

            # 调用 LLM
            response = await call_llm(data["content"])

            # 发送响应
            await websocket.send_json({
                "type": "ai_response",
                "content": response
            })
    except WebSocketDisconnect:
        print(f"Client disconnected: {project_id}")
```

---

## 5. 错误处理

### 5.1 错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "name",
        "message": "项目名称不能为空"
      }
    ]
  }
}
```

### 5.2 HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|-------|------|---------|
| 200 | 成功 | GET 请求成功 |
| 201 | 已创建 | POST 创建资源成功 |
| 202 | 已接受 | 异步任务已加入队列 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未授权 | Token 无效或过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 422 | 实体错误 | 业务逻辑验证失败 |
| 500 | 服务器错误 | 内部错误 |

---

## 6. 认证授权

### 6.1 JWT 认证

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}

Response 200:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 6.2 请求头

```http
GET /api/v1/projects
Authorization: Bearer eyJ...
```

### 6.3 FastAPI 依赖注入

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return get_user_by_id(user_id)

@app.get("/api/v1/projects")
def list_projects(current_user: User = Depends(get_current_user)):
    return get_user_projects(current_user.id)
```

---

## 7. API 文档

### 7.1 自动生成（OpenAPI）

FastAPI 自动生成 OpenAPI 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 7.2 文档配置

```python
app = FastAPI(
    title="AI Code Generator API",
    version="1.0.0",
    description="AI 驱动的代码生成平台 API",
    openapi_tags=[
        {"name": "projects", "description": "项目管理"},
        {"name": "quality", "description": "代码质量检查"},
        {"name": "agents", "description": "Agent 工作流"}
    ]
)
```

---

## 8. 速率限制

### 8.1 限流策略

| 端点类型 | 限制 |
|---------|------|
| 认证 API | 5 次/分钟 |
| 查询 API | 100 次/分钟 |
| 代码生成 | 10 次/小时 |
| SSE 连接 | 5 个并发 |

### 8.2 实现

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(redis_client)

@app.post("/api/v1/projects/{project_id}/generate", dependencies=[Depends(RateLimiter(times=10, hours=1))])
async def generate_code(project_id: str):
    ...
```

---

## 9. API 版本管理

### 9.1 URL 版本

```
/api/v1/projects  # 当前版本
/api/v2/projects  # 未来版本
```

### 9.2 版本弃用

```python
@app.get("/api/v1/old-endpoint", deprecated=True)
async def old_endpoint():
    """此端点已弃用，请使用 /api/v2/new-endpoint"""
    ...
```
