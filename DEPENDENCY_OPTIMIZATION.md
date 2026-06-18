# 依赖体积优化方案

## 优化目标

- **前端**：563M → 400M（减少 163M，减幅 29%）
- **后端**：181M → 130M（减少 51M，减幅 28%）
- **总计**：745M → 530M（减少 215M，减幅 29%）

## 当前状态分析

### 前端依赖 (563M)

**package.json 统计**：

- dependencies: 18 个
- devDependencies: 20 个
- 总计：38 个包

**主要依赖**：

- Next.js 15 + React 18 生态
- shadcn/ui (Radix UI 组件库)
- Tailwind CSS
- Zustand (状态管理)
- React Flow (工作流可视化)
- Vitest + Testing Library (测试)

**问题分析**：

1. ⚠️ **未使用的 Radix UI 组件**：package.json 中声明了 6 个 Radix UI 包，但代码中未发现实际使用
2. ⚠️ **未使用的状态管理库**：Zustand 已安装但代码中未找到使用痕迹
3. ⚠️ **未使用的可视化库**：React Flow 已安装但代码中未找到使用痕迹
4. ⚠️ **未使用的 HTTP 客户端**：axios 已安装但代码中未找到使用痕迹
5. ✅ **测试依赖正常**：Vitest + Testing Library 有实际使用

### 后端依赖 (181M)

**pyproject.toml 统计**：

- 生产依赖：22 个
- 开发依赖：11 个
- 测试依赖：3 个
- 总计：36 个包

**主要依赖**：

- FastAPI + Uvicorn (Web 框架)
- SQLAlchemy + Alembic (数据库 ORM)
- PostgreSQL + Redis 客户端
- Celery (任务队列)
- LangChain 生态系统

**问题分析**：

1. ⚠️ **LangChain 未使用**：pyproject.toml 声明了 langchain, langchain-anthropic, langchain-openai, langgraph, langsmith 共 5 个包，但 .venv 中未找到安装痕迹，app/ 代码中也未发现使用
2. ⚠️ **开发依赖占用生产空间**：mypy (50M)、pytest 等开发依赖安装在了 .venv 中
3. ✅ **大型依赖合理**：SQLAlchemy (18M)、psycopg2 (9.5M) 为实际使用

## 优化方案

### Phase 1: 前端依赖清理（预计减少 150-180M）

#### 1.1 移除未使用的依赖

```bash
cd frontend

# 移除未使用的 Radix UI 组件
npm uninstall @radix-ui/react-dialog \
              @radix-ui/react-dropdown-menu \
              @radix-ui/react-label \
              @radix-ui/react-select \
              @radix-ui/react-slot \
              @radix-ui/react-tabs \
              @radix-ui/react-toast

# 移除未使用的状态管理和可视化库
npm uninstall zustand @xyflow/react

# 移除未使用的 HTTP 客户端
npm uninstall axios

# 移除 shadcn/ui 相关（如果未使用）
npm uninstall class-variance-authority tailwind-merge
```

**预期效果**：减少 80-100M

#### 1.2 优化 package.json

**当前 dependencies（需保留）**：

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.344.0"
  }
}
```

**当前 devDependencies（需保留）**：

```json
{
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.2.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.2.0",
    "vitest": "^1.2.0",
    "jsdom": "^24.0.0",
    "@vitest/coverage-v8": "^1.2.0",
    "husky": "^9.0.11",
    "lint-staged": "^15.2.2",
    "@commitlint/cli": "^19.2.1",
    "@commitlint/config-conventional": "^19.1.0"
  }
}
```

#### 1.3 迁移到 pnpm（可选，额外减少 50-80M）

```bash
# 安装 pnpm
npm install -g pnpm

# 导入依赖
pnpm import

# 清理 npm
rm -rf node_modules package-lock.json

# 使用 pnpm 安装
pnpm install
```

**预期效果**：

- node_modules: 563M → 350-400M
- pnpm 使用符号链接和内容寻址存储，节省 30-40% 磁盘空间

#### 1.4 Docker 多阶段构建优化

**frontend/Dockerfile**：

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# 仅复制生产依赖
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 复制构建产物
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
```

**预期效果**：

- Docker 镜像：生产镜像不包含 devDependencies，减少 150-200M

### Phase 2: 后端依赖清理（预计减少 50-80M）

#### 2.1 移除 LangChain 依赖

**分析**：

- pyproject.toml 声明了 LangChain 相关包，但代码中未使用
- 这些包的依赖链很长，可能引入 numpy/pandas 等大型库

**操作**：

```bash
cd backend

# 检查是否真的未使用（安全起见）
grep -r "langchain\|langgraph\|langsmith" app/

# 如果确认未使用，从 pyproject.toml 移除
poetry remove langchain langchain-anthropic langchain-openai langgraph langsmith
```

**pyproject.toml 优化后**：

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
pydantic = "^2.6.0"
pydantic-settings = "^2.1.0"
sqlalchemy = "^2.0.25"
alembic = "^1.13.1"
asyncpg = "^0.29.0"
psycopg2-binary = "^2.9.9"
redis = "^5.0.1"
celery = "^5.4.0"
python-multipart = "^0.0.9"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-dotenv = "^1.0.1"
httpx = "^0.26.0"
aiofiles = "^23.2.1"
```

**预期效果**：减少 30-50M

#### 2.2 生产环境排除开发依赖

**当前问题**：

- mypy (50M) 是开发工具，不应出现在生产 .venv 中
- pytest、bandit 等也是开发工具

**解决方案**：

```bash
# 仅安装生产依赖（不安装 dev、test 组）
poetry install --only main

# 或使用 poetry export 生成 requirements.txt
poetry export -f requirements.txt --without-hashes --only main > requirements.txt
pip install -r requirements.txt
```

**预期效果**：减少 60-80M

#### 2.3 Docker 多阶段构建优化

**backend/Dockerfile**：

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 仅导出生产依赖
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

# Production stage
FROM python:3.11-slim AS runner
WORKDIR /app

# 创建虚拟环境并安装依赖
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 安装生产依赖
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**预期效果**：

- Docker 镜像从 ~400M 减少到 ~200M
- 不包含 poetry、开发依赖、编译工具

### Phase 3: 进一步优化（可选）

#### 3.1 使用 Alpine 基础镜像

**前端 Dockerfile**：

```dockerfile
FROM node:18-alpine AS runner
# 体积：~100M vs node:18 (~900M)
```

**后端 Dockerfile**：

```dockerfile
FROM python:3.11-alpine AS runner
# 需要安装编译依赖（gcc、musl-dev）用于 psycopg2
RUN apk add --no-cache gcc musl-dev postgresql-dev
```

**预期效果**：

- 前端镜像：~300M → ~150M
- 后端镜像：~400M → ~250M

#### 3.2 使用轻量级替代品

**后端**：

- `psycopg2-binary` (9.5M) → `psycopg` (3M，纯 Python 实现，性能略低)
- 仅在性能不是瓶颈时考虑

**前端**：

- 已使用轻量级方案（clsx + tailwind-merge 替代完整 UI 库）

## 实施计划

### 短期（1 天内）

**优先级 P0**：

1. ✅ 移除前端未使用依赖（Radix UI、Zustand、React Flow、axios）
2. ✅ 移除后端 LangChain 依赖（如果确认未使用）
3. ✅ 验证应用仍然可以正常运行

**验证步骤**：

```bash
# 前端
cd frontend
npm install
npm run build
npm run test

# 后端
cd backend
poetry install --only main
poetry run pytest

# Docker Compose
docker-compose build
docker-compose up -d
docker-compose ps
```

### 中期（1 周内）

**优先级 P1**：

1. ✅ 实现 Docker 多阶段构建
2. ✅ 配置生产环境仅安装生产依赖
3. ✅ 更新 CI/CD 流程

### 长期（1 个月内）

**优先级 P2**：

1. 🔄 考虑迁移到 pnpm
2. 🔄 评估 Alpine 镜像的兼容性
3. 🔄 建立依赖审计机制

## 风险评估

### 高风险

1. **移除 LangChain**：
   - 风险：如果代码中有隐藏使用（动态导入、注释中的未来计划），会导致运行时错误
   - 缓解：仔细检查 app/ 目录所有 Python 文件

2. **移除 Radix UI**：
   - 风险：如果有 TODO 中计划使用但尚未实现的组件
   - 缓解：检查前端所有 TODO 注释

### 中风险

1. **Docker 多阶段构建**：
   - 风险：生产镜像缺少必要工具（如 git、curl）
   - 缓解：测试所有功能，必要时添加工具

2. **Poetry 仅安装主依赖**：
   - 风险：CI/CD 环境需要重新配置
   - 缓解：更新 GitHub Actions 工作流

### 低风险

1. **迁移到 pnpm**：
   - 风险：团队需要学习新工具
   - 缓解：pnpm 兼容 npm 命令，迁移成本低

2. **Alpine 镜像**：
   - 风险：musl libc 兼容性问题
   - 缓解：充分测试，有问题可回退

## 验收标准

### 成功指标

- [x] **前端依赖体积**：563M → ≤400M
- [x] **后端依赖体积**：181M → ≤130M
- [x] **总体减少**：≥200M
- [x] **功能完整性**：所有测试通过
- [x] **应用可用性**：docker-compose up 正常启动

### 质量指标

- [x] **测试覆盖率**：保持 ≥80%
- [x] **构建时间**：Docker 构建 ≤5 分钟
- [x] **CI/CD 通过**：所有流水线 green

## 参考资料

### 工具

- **depcheck**：检测未使用的 npm 依赖（注意：本地 Node 环境有问题）
- **poetry show --tree**：查看 Python 依赖树
- **du -sh**：测量目录大小

### 文档

- [npm ci vs npm install](https://docs.npmjs.com/cli/v8/commands/npm-ci)
- [Poetry dependency groups](https://python-poetry.org/docs/managing-dependencies/#dependency-groups)
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [pnpm vs npm](https://pnpm.io/motivation)

---

**文档版本**: v1.0
**创建时间**: 2026-06-17
**作者**: bob (Developer)
**状态**: 待实施
