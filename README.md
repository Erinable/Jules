# ============================================

# Jules - AI 代码生成平台

# ============================================

## 项目简介

Jules 是一个专注于**生产级代码质量**的 AI 代码生成平台，通过 Multi-Agent 协作和内置质量门禁，确保生成代码的可维护性和安全性。

### 核心特性

- ✅ **质量优先**：内置静态分析（Ruff/mypy/Bandit）+ 复杂度门禁（CC<10, MI>20）
- ✅ **可迭代性**：增量编辑 + Git 集成 + 变更追踪
- ✅ **Multi-Agent 协作**：Researcher → Planner → Coder → Reviewer → Tester
- ✅ **实时可视化**：React Flow 工作流展示 + 质量仪表板
- ✅ **成本透明**：实时 Token 统计 + 智能模型选择

---

## 技术栈

### 后端

- **语言**：Python 3.11+
- **框架**：FastAPI 0.115+
- **Agent 编排**：LangGraph 0.2+ / LangChain 0.3+
- **数据库**：PostgreSQL 16
- **缓存**：Redis 7
- **任务队列**：Celery 5.4+

### 前端

- **框架**：Next.js 15 + React 18
- **UI 组件**：shadcn/ui + Tailwind CSS 3.4+
- **状态管理**：Zustand 4.5+
- **可视化**：React Flow 12+

### 代码质量工具

- **Linting**：Ruff
- **Type Checking**：mypy
- **Security**：Bandit
- **Complexity**：Radon + Complexipy

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git 2.40+
- (可选) Node.js 18+ / Python 3.11+ (本地开发)

### 1. 克隆仓库

```bash
git clone https://github.com/your-org/jules.git
cd jules
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要的 API 密钥
# 必填项：
# - ANTHROPIC_API_KEY（Claude API）
# - OPENAI_API_KEY（可选，如需使用 GPT）
# - LANGSMITH_API_KEY（可选，用于 Agent 追踪）
nano .env
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **前端界面**：<http://localhost:3000>
- **后端 API**：<http://localhost:8000>
- **API 文档**：<http://localhost:8000/docs>
- **ReDoc 文档**：<http://localhost:8000/redoc>

### 5. 初始化数据库

```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# (可选) 加载测试数据
docker-compose exec backend python scripts/seed_data.py
```

---

## 开发指南

### 项目结构

```
jules/
├── docker-compose.yml          # Docker Compose 配置
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略文件
├── README.md                  # 项目说明文档
├── docs/                      # 文档目录
│   ├── architecture/          # 架构设计文档
│   └── tech-stack.md         # 技术选型文档
├── frontend/                  # 前端项目
│   ├── Dockerfile            # 前端 Dockerfile
│   ├── package.json          # npm 依赖
│   ├── next.config.js        # Next.js 配置
│   ├── tsconfig.json         # TypeScript 配置
│   ├── tailwind.config.js    # Tailwind CSS 配置
│   ├── app/                  # Next.js App Router
│   ├── components/           # React 组件
│   ├── lib/                  # 工具函数
│   └── public/               # 静态资源
├── backend/                   # 后端项目
│   ├── Dockerfile            # 后端 Dockerfile
│   ├── pyproject.toml        # Poetry 依赖配置
│   ├── poetry.lock           # Poetry 锁文件
│   ├── alembic/              # 数据库迁移
│   ├── app/                  # FastAPI 应用
│   │   ├── main.py          # 应用入口
│   │   ├── api/             # API 路由
│   │   ├── agents/          # LangGraph Agents
│   │   ├── core/            # 核心配置
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 模式
│   │   ├── services/        # 业务逻辑
│   │   ├── tasks/           # Celery 任务
│   │   └── utils/           # 工具函数
│   ├── tests/                # 测试
│   ├── scripts/              # 脚本工具
│   └── config/               # 配置文件
└── .github/                   # GitHub 配置
    └── workflows/            # CI/CD 工作流
```

### 本地开发

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test

# 类型检查
npm run type-check

# 代码格式化
npm run format
```

#### 后端开发

```bash
cd backend

# 安装依赖（使用 Poetry）
poetry install

# 激活虚拟环境
poetry shell

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码质量检查
ruff check .
mypy .
bandit -r app/

# 代码格式化
ruff format .
```

### 常用命令

```bash
# 重启特定服务
docker-compose restart backend

# 查看特定服务日志
docker-compose logs -f frontend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险操作）
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache

# 查看资源使用情况
docker stats
```

---

## 测试

### 运行测试

```bash
# 后端测试
docker-compose exec backend pytest

# 前端测试
docker-compose exec frontend npm test

# 生成测试覆盖率报告
docker-compose exec backend pytest --cov=app --cov-report=html
docker-compose exec frontend npm run test:coverage
```

### 代码质量检查

```bash
# 后端质量检查
docker-compose exec backend ruff check .
docker-compose exec backend mypy .
docker-compose exec backend bandit -r app/
docker-compose exec backend radon cc app/ -a

# 前端质量检查
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
```

---

## 部署

### 生产环境部署

1. **准备生产配置**

```bash
# 创建生产环境变量文件
cp .env.example .env.production

# 修改以下关键配置：
# - ENVIRONMENT=production
# - DEBUG=false
# - SECRET_KEY=<强密码>
# - DATABASE_URL=<生产数据库连接>
# - CORS_ORIGINS=<生产域名>
```

2. **构建生产镜像**

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 推送到镜像仓库
docker tag jules-backend:latest your-registry/jules-backend:v1.0.0
docker push your-registry/jules-backend:v1.0.0
```

3. **部署到服务器**

详见 [docs/architecture/deployment.md](docs/architecture/deployment.md)

---

## 监控和日志

### 日志查看

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 检查数据库连接
docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"

# 检查 Redis 连接
docker-compose exec redis redis-cli ping
```

---

## 故障排查

### 常见问题

**1. 端口冲突**

```bash
# 检查端口占用
lsof -i :3000
lsof -i :8000
lsof -i :5432

# 修改 docker-compose.yml 中的端口映射
```

**2. 数据库连接失败**

```bash
# 检查 PostgreSQL 是否启动
docker-compose ps postgres

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 重启 PostgreSQL
docker-compose restart postgres
```

**3. 前端无法连接后端**

```bash
# 检查网络配置
docker network inspect jules-network

# 检查环境变量
docker-compose exec frontend env | grep API_URL
```

**4. Celery Worker 未启动**

```bash
# 查看 Worker 日志
docker-compose logs celery-worker

# 重启 Worker
docker-compose restart celery-worker
```

---

## 贡献指南

### 提交代码

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- **项目主页**：<https://github.com/your-org/jules>
- **问题反馈**：<https://github.com/your-org/jules/issues>
- **文档**：<https://jules-ai.dev/docs>
- **邮箱**：<team@jules-ai.dev>

---

## 致谢

感谢以下开源项目：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代 Python Web 框架
- [Next.js](https://github.com/vercel/next.js) - React 全栈框架
- [shadcn/ui](https://ui.shadcn.com/) - 精美的 UI 组件库
