# Jules Backend

FastAPI backend application for the Jules AI Code Generation Platform.

## 项目简介

Jules 后端是一个基于 FastAPI 的现代 Python Web 服务，提供完整的 RESTful API 和 Multi-Agent 协作系统，用于 AI 代码生成、质量分析和任务管理。

## 技术栈

- **语言**: Python 3.11+
- **Web 框架**: FastAPI 0.115+
- **数据库 ORM**: SQLAlchemy 2.0+
- **数据库**: PostgreSQL 16
- **数据迁移**: Alembic 1.13+
- **Agent 框架**: LangGraph 0.2+ / LangChain 0.3+
- **异步支持**: asyncio, asyncpg
- **测试框架**: pytest 8.0+
- **代码质量工具**:
  - Linting: Ruff
  - Type Checking: mypy
  - Security: Bandit
  - Complexity: Radon

## 项目结构

```
backend/
├── alembic/                    # 数据库迁移脚本
│   ├── versions/              # 迁移版本文件
│   └── env.py                 # Alembic 配置
├── app/                        # FastAPI 应用主目录
│   ├── main.py                # 应用入口点
│   ├── api/                   # API 路由层
│   │   └── v1/               # API v1 版本
│   │       ├── users.py      # 用户管理 API
│   │       ├── tasks.py      # 任务管理 API
│   │       ├── agents.py     # Agent 配置 API
│   │       ├── executions.py # 执行记录 API
│   │       ├── code_files.py # 代码文件 API
│   │       ├── quality.py    # 质量指标 API
│   │       └── health.py     # 健康检查 API
│   ├── agent/                 # Agent 系统（详见 app/agent/README.md）
│   │   ├── scheduler.py      # Agent 调度器
│   │   ├── executor.py       # 执行引擎
│   │   ├── llm_client.py     # LLM 客户端
│   │   ├── code_analyzer.py  # 代码分析器
│   │   ├── worker.py         # 后台 Worker
│   │   └── prompts/          # Prompt 模板
│   ├── models/                # SQLAlchemy 数据模型
│   │   ├── user.py           # User 模型
│   │   ├── task.py           # Task 模型
│   │   ├── agent.py          # Agent 模型
│   │   ├── agent_execution.py # AgentExecution 模型
│   │   ├── llm_call.py       # LLMCall 模型
│   │   ├── code_file.py      # CodeFile 模型
│   │   ├── code_version.py   # CodeVersion 模型
│   │   ├── quality_metric.py # QualityMetric 模型
│   │   └── health_check.py   # HealthCheck 模型
│   ├── repositories/          # Repository 层（数据访问）
│   │   ├── user_repository.py
│   │   ├── task_repository.py
│   │   ├── agent_execution_repository.py
│   │   ├── code_file_repository.py
│   │   ├── code_version_repository.py
│   │   └── quality_metric_repository.py
│   ├── schemas/               # Pydantic 模式（请求/响应）
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── agent.py
│   │   ├── execution.py
│   │   ├── code_file.py
│   │   ├── quality.py
│   │   └── health.py
│   ├── database/              # 数据库配置
│   │   ├── base.py           # Base 模型
│   │   ├── session.py        # 会话管理
│   │   └── migrations.py     # 迁移工具
│   └── dependencies/          # FastAPI 依赖项
│       ├── database.py       # 数据库依赖
│       └── auth.py           # 认证依赖（未来）
├── tests/                      # 测试目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── e2e/                  # 端到端测试
├── scripts/                    # 工具脚本
│   ├── seed_data.py          # 数据填充
│   └── init_db.py            # 数据库初始化
├── config/                     # 配置文件
├── pyproject.toml             # Poetry 依赖配置
├── alembic.ini                # Alembic 配置
└── Dockerfile                 # Docker 镜像定义

## 安装和运行

### 前置要求

- Python 3.11+
- PostgreSQL 16
- Poetry 1.7+（或 pip）

### 1. 安装依赖

使用 Poetry（推荐）：

```bash
cd backend
poetry install
```

或使用 pip：

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（参考根目录的 `.env.example`）：

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/jules

# OpenAI API（可选）
OPENAI_API_KEY=sk-xxx

# Anthropic API（推荐）
ANTHROPIC_API_KEY=sk-ant-xxx

# LangSmith（可选，用于追踪）
LANGSMITH_API_KEY=xxx
LANGSMITH_PROJECT=jules

# 应用配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000

# Agent 配置
AGENT_MODE=mock  # 或 real（真实 API 调用）
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
poetry run alembic upgrade head

# 或使用 Docker
docker-compose exec backend alembic upgrade head
```

### 4. 启动开发服务器

```bash
# 使用 Poetry
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或直接使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：

- **API 文档（Swagger UI）**: <http://localhost:8000/docs>
- **API 文档（ReDoc）**: <http://localhost:8000/redoc>
- **健康检查**: <http://localhost:8000/health>

## API 端点

### 用户管理（Users）

- `GET /api/v1/users/` - 获取用户列表
- `POST /api/v1/users/` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户
- `DELETE /api/v1/users/{user_id}` - 删除用户

### 任务管理（Tasks）

- `GET /api/v1/tasks/` - 获取任务列表
- `POST /api/v1/tasks/` - 创建任务
- `GET /api/v1/tasks/{task_id}` - 获取任务详情
- `PUT /api/v1/tasks/{task_id}` - 更新任务
- `PATCH /api/v1/tasks/{task_id}/status` - 更新任务状态
- `DELETE /api/v1/tasks/{task_id}` - 删除任务

### Agent 配置（Agents）

- `GET /api/v1/agents/` - 获取 Agent 列表
- `POST /api/v1/agents/` - 创建 Agent
- `GET /api/v1/agents/{agent_id}` - 获取 Agent 详情
- `PUT /api/v1/agents/{agent_id}` - 更新 Agent
- `DELETE /api/v1/agents/{agent_id}` - 删除 Agent
- `POST /api/v1/agents/execute` - 执行 Agent 任务

### 执行记录（Executions）

- `GET /api/v1/executions/` - 获取执行记录列表
- `POST /api/v1/executions/` - 创建执行记录
- `GET /api/v1/executions/{execution_id}` - 获取执行详情
- `PATCH /api/v1/executions/{execution_id}/status` - 更新执行状态
- `DELETE /api/v1/executions/{execution_id}` - 删除执行记录

### 代码文件（Code Files）

- `GET /api/v1/code-files/` - 获取代码文件列表
- `POST /api/v1/code-files/` - 创建代码文件
- `GET /api/v1/code-files/{file_id}` - 获取文件详情
- `PUT /api/v1/code-files/{file_id}` - 更新文件
- `DELETE /api/v1/code-files/{file_id}` - 删除文件
- `GET /api/v1/code-files/{file_id}/versions` - 获取文件版本历史

### 质量指标（Quality Metrics）

- `GET /api/v1/quality/` - 获取质量指标列表
- `POST /api/v1/quality/` - 创建质量指标
- `GET /api/v1/quality/latest` - 获取最新质量指标
- `DELETE /api/v1/quality/{metric_id}` - 删除质量指标

### 健康检查（Health）

- `GET /health` - 系统健康状态
- `GET /health/ready` - 就绪状态（是否可以接受流量）
- `GET /health/live` - 存活状态（是否需要重启）

详细 API 文档参见 [app/api/v1/README.md](app/api/v1/README.md)

## 测试

### 运行所有测试

```bash
poetry run pytest
```

### 运行特定测试

```bash
# 单元测试
poetry run pytest tests/unit/

# 集成测试
poetry run pytest tests/integration/

# 端到端测试
poetry run pytest tests/e2e/
```

### 生成测试覆盖率报告

```bash
poetry run pytest --cov=app --cov-report=html --cov-report=term
```

查看 HTML 报告：`open htmlcov/index.html`

### 测试覆盖率要求

- **最低覆盖率**: 80%
- **关键模块**: 90%+（models, repositories, api）

## 代码质量

### Linting（代码规范检查）

```bash
# 使用 Ruff 检查
poetry run ruff check .

# 自动修复
poetry run ruff check --fix .

# 格式化代码
poetry run ruff format .
```

### Type Checking（类型检查）

```bash
poetry run mypy app/
```

### Security Scan（安全扫描）

```bash
poetry run bandit -r app/
```

### Complexity Analysis（复杂度分析）

```bash
# Cyclomatic Complexity（CC < 10）
poetry run radon cc app/ -a

# Maintainability Index（MI > 20）
poetry run radon mi app/ -s
```

## 数据库迁移

### 创建新迁移

```bash
# 自动生成迁移（基于模型变化）
poetry run alembic revision --autogenerate -m "Add new field to User model"

# 手动创建迁移
poetry run alembic revision -m "Custom migration"
```

### 应用迁移

```bash
# 升级到最新版本
poetry run alembic upgrade head

# 升级到特定版本
poetry run alembic upgrade <revision_id>

# 降级一个版本
poetry run alembic downgrade -1

# 查看迁移历史
poetry run alembic history
```

### 回滚迁移

```bash
# 回滚到指定版本
poetry run alembic downgrade <revision_id>

# 回滚所有迁移
poetry run alembic downgrade base
```

## Agent 系统

Jules 后端内置了完整的 Multi-Agent 系统，用于代码生成、分析和优化。

### Agent 架构

- **Scheduler**: 任务调度和编排
- **Executor**: Agent 执行引擎
- **LLM Client**: 统一的 LLM 调用接口（支持 OpenAI、Anthropic）
- **Code Analyzer**: 静态代码分析（Ruff、mypy、Bandit）
- **Worker**: 后台任务处理（Celery）

详细文档参见 [app/agent/README.md](app/agent/README.md)

### 使用示例

```python
from app.agent.executor import AgentExecutor
from app.agent.llm_client import LLMClient

# 初始化
llm_client = LLMClient(provider="anthropic", model="claude-3-5-sonnet-20241022")
executor = AgentExecutor(llm_client=llm_client)

# 执行任务
result = await executor.execute(
    task_id="123",
    prompt="Generate a Python function to calculate factorial",
    context={"language": "python", "style": "functional"}
)
```

### Mock 模式 vs 真实 API

- **Mock 模式**（`AGENT_MODE=mock`）：使用模拟响应，不消耗 API Token，适合开发和测试
- **真实 API 模式**（`AGENT_MODE=real`）：调用真实 LLM API，适合生产环境

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t jules-backend:latest .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/jules \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  jules-backend:latest
```

### Docker Compose 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 生产环境配置

生产环境部署详见 [../../docs/architecture/deployment.md](../../docs/architecture/deployment.md)

关键配置项：

- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY=<strong-random-key>`
- `DATABASE_URL=<production-db-url>`
- `CORS_ORIGINS=<production-frontend-url>`

## 故障排查

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否启动
docker-compose ps postgres

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 测试数据库连接
poetry run python -c "from app.database.session import engine; engine.connect()"
```

### 迁移失败

```bash
# 查看当前迁移状态
poetry run alembic current

# 查看迁移历史
poetry run alembic history

# 重置迁移（危险操作）
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### API 返回 500 错误

```bash
# 查看详细错误日志
docker-compose logs backend

# 检查环境变量
docker-compose exec backend env | grep DATABASE_URL

# 进入容器调试
docker-compose exec backend bash
```

### Agent 执行失败

```bash
# 检查 LLM API Key
echo $ANTHROPIC_API_KEY

# 查看 Agent 日志
docker-compose logs backend | grep agent

# 切换到 Mock 模式测试
export AGENT_MODE=mock
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/models/` 创建数据模型
2. 在 `app/schemas/` 创建 Pydantic Schema
3. 在 `app/repositories/` 创建 Repository
4. 在 `app/api/v1/` 创建路由
5. 编写测试（`tests/`）
6. 创建数据库迁移（`alembic revision --autogenerate`）

### 代码风格

遵循以下原则：

- **不可变性**: 优先使用不可变数据结构
- **类型注解**: 所有函数必须有类型注解
- **文档字符串**: 公共 API 必须有 docstring
- **错误处理**: 显式处理所有异常
- **测试**: 新代码必须有 80%+ 测试覆盖率

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: add new agent execution endpoint
fix: resolve database connection timeout
docs: update API documentation
test: add integration tests for quality metrics
refactor: simplify code analyzer logic
```

## 性能优化

### 数据库优化

- 使用索引（参见 `docs/database.md`）
- 使用异步查询（`asyncpg`）
- 启用连接池
- 使用 `EXPLAIN ANALYZE` 分析慢查询

### API 优化

- 使用分页（`skip`, `limit`）
- 启用 GZIP 压缩
- 添加响应缓存（Redis）
- 使用异步端点（`async def`）

### Agent 优化

- 使用批量 LLM 调用
- 启用 LLM 响应缓存
- 优化 Prompt 长度
- 使用流式响应

## 监控和日志

### 日志配置

日志级别：

- `DEBUG`: 详细调试信息
- `INFO`: 常规信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 健康检查

- `/health`: 整体健康状态
- `/health/ready`: 是否可以接受流量
- `/health/live`: 是否需要重启

### 性能监控

建议使用：

- **Prometheus**: 指标收集
- **Grafana**: 可视化
- **Sentry**: 错误追踪
- **LangSmith**: Agent 追踪

## 许可证

MIT License - 详见根目录 [LICENSE](../LICENSE) 文件

## 联系方式

- **项目主页**: <https://github.com/your-org/jules>
- **问题反馈**: <https://github.com/your-org/jules/issues>
- **API 文档**: <http://localhost:8000/docs>

---

**版本**: 1.0.0
**最后更新**: 2026-06-17
