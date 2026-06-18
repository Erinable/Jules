# Jules

Jules 是一个前后端一体的 AI 代码生成平台。仓库包含 FastAPI 后端、Next.js 前端、PostgreSQL、Redis、Alembic 数据库迁移、Docker Compose 本地开发环境、测试和 CI/CD 配置。

## 当前状态

- 前端：Next.js 15、React 18、TypeScript、Tailwind CSS、Axios
- 后端：Python 3.11、FastAPI、SQLAlchemy、Alembic、Poetry
- 数据层：PostgreSQL 16、Redis 7
- 异步任务：Celery worker / beat，默认通过 `workers` profile 启动
- 质量工具：pre-commit、Ruff、pytest、mypy、ESLint、Prettier、Vitest

## 快速启动

前置要求：

- Docker 20.10+
- Docker Compose v2
- Git

启动开发环境：

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

访问地址：

- 前端：<http://localhost:3000>
- 后端 API：<http://localhost:8000>
- OpenAPI 文档：<http://localhost:8000/docs>

后端容器启动时会先执行 `alembic upgrade head`，新数据库会自动迁移到最新版本。

## 常用命令

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

重启服务：

```bash
docker compose restart backend
docker compose restart frontend
```

启动可选 worker：

```bash
docker compose --profile workers up -d
```

停止服务：

```bash
docker compose down
```

## 本地开发

后端：

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 检查和测试

推荐先跑全量 pre-commit：

```bash
pre-commit run --all-files
```

后端：

```bash
cd backend
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app --ignore-missing-imports
```

前端：

```bash
cd frontend
npm run lint
npm run type-check
npm run format:check
npm test
```

## 项目结构

```text
.
├── backend/              # FastAPI 应用、模型、迁移、测试
├── frontend/             # Next.js 应用、组件、服务、测试
├── docs/                 # 架构、API、数据库、设计文档
├── .github/workflows/    # CI/CD 工作流
├── docker-compose.yml    # 本地开发环境
├── CHANGELOG.md          # 版本变更记录
├── CONTRIBUTING.md       # 贡献指南
└── README.md             # 项目入口文档
```

## 文档入口

- 后端说明：[backend/README.md](backend/README.md)
- 前端说明：[frontend/README.md](frontend/README.md)
- 架构文档：[docs/architecture/](docs/architecture/)
- WebSocket API：[docs/api/websocket.md](docs/api/websocket.md)
- 数据库说明：[docs/database.md](docs/database.md)
- 开发说明：[docs/development.md](docs/development.md)

## 注意事项

- 前端可使用 `localhost` 或 `127.0.0.1` 访问，后端 CORS 已允许这两个本地来源。
- `docker compose up -d` 默认只启动 frontend、backend、postgres、redis。
- Celery worker 和 beat 默认不启动，需要使用 `--profile workers`。
- 不要提交本地虚拟环境、依赖目录、覆盖率报告或缓存文件。
