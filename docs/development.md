# Jules 开发指南

面向开发者的完整开发指南，涵盖环境搭建、编码规范、测试流程和常见问题。

## 目录

- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [Git 工作流](#git-工作流)
- [测试编写指南](#测试编写指南)
- [Pull Request 流程](#pull-request-流程)
- [常见问题解答](#常见问题解答)

---

## 开发环境搭建

### 前置要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.40+
- **Node.js**: 18+ (本地前端开发)
- **Python**: 3.11+ (本地后端开发)
- **Poetry**: 1.7+ (Python 依赖管理)

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/jules.git
cd jules

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入必要的 API Key

# 3. 启动 Docker 服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head

# 5. 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 本地开发（不使用 Docker）

#### 后端开发

```bash
cd backend

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 启动数据库（Docker）
docker-compose up -d postgres redis

# 运行迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

---

## 代码规范

### Python 代码规范

遵循 [PEP 8](https://peps.python.org/pep-0008/) 和 [PEP 484](https://peps.python.org/pep-0484/)（类型注解）

#### 命名规范

```python
# 变量和函数：snake_case
user_name = "John"
def get_user_by_id(user_id: int) -> User:
    pass

# 类：PascalCase
class UserRepository:
    pass

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
API_BASE_URL = "https://api.example.com"

# 私有方法：_前缀
def _internal_helper():
    pass
```

#### 类型注解

```python
from typing import List, Optional, Dict, Any

# 函数类型注解
def create_user(
    email: str,
    username: str,
    is_active: bool = True
) -> User:
    """创建新用户"""
    pass

# 变量类型注解
users: List[User] = []
config: Dict[str, Any] = {}
optional_value: Optional[str] = None
```

#### Docstring 规范

使用 Google 风格的 docstring：

```python
def execute_agent_task(
    task_id: int,
    prompt: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """执行 Agent 任务

    Args:
        task_id: 任务ID
        prompt: 输入 Prompt
        context: 上下文信息

    Returns:
        包含执行结果的字典

    Raises:
        ValueError: 如果 task_id 无效
        ExecutionError: 如果执行失败
    """
    pass
```

#### 代码检查工具

```bash
# Ruff (Linting + Formatting)
poetry run ruff check .
poetry run ruff format .

# mypy (Type Checking)
poetry run mypy app/

# Bandit (Security)
poetry run bandit -r app/

# Radon (Complexity)
poetry run radon cc app/ -a -nb
poetry run radon mi app/ -s
```

---

### TypeScript/JavaScript 代码规范

#### 命名规范

```typescript
// 变量和函数：camelCase
const userName = "John";
function getUserById(userId: number): User {
  return {} as User;
}

// 类和接口：PascalCase
class UserService {}
interface UserData

// 常量：UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = "https://api.example.com";

// 布尔值：is/has/should 前缀
const isActive = true;
const hasPermission = false;
const shouldUpdate = true;
```

#### 类型定义

```typescript
// 使用接口定义数据结构
interface User {
  id: number;
  email: string;
  username: string;
  createdAt: Date;
}

// 使用类型别名
type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

// 泛型
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json());
}
```

#### 代码检查工具

```bash
# ESLint
npm run lint

# TypeScript Type Checking
npm run type-check

# Prettier
npm run format
```

---

## Git 工作流

### 分支命名

```bash
# 功能开发
feature/user-authentication
feature/agent-execution

# Bug 修复
fix/database-connection-error
fix/api-timeout

# 重构
refactor/simplify-executor
refactor/remove-dead-code

# 文档
docs/update-api-documentation
docs/add-deployment-guide
```

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```bash
# 格式
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具
- `perf`: 性能优化

**示例**:

```bash
feat(agent): add support for Anthropic Claude API

- Implement LLMClient for Claude
- Add configuration options
- Update documentation

Closes #123
```

```bash
fix(api): resolve database connection timeout

The connection pool was exhausted under high load.
Increased pool_size from 10 to 20.

Fixes #456
```

### 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: add new feature"

# 3. 推送到远程
git push origin feature/new-feature

# 4. 创建 Pull Request
gh pr create --title "Add new feature" --body "Description"

# 5. 代码审查和合并
# 审查通过后，使用 Squash and Merge
```

---

## 测试编写指南

### 测试覆盖率要求

- **最低覆盖率**: 80%
- **关键模块**: 90%+（models, repositories, api）

### 后端测试（pytest）

#### 单元测试

```python
# tests/unit/test_user_repository.py
import pytest
from app.repositories.user_repository import UserRepository
from app.models.user import User

@pytest.fixture
async def user_repository():
    """创建 UserRepository 实例"""
    return UserRepository()

async def test_create_user(user_repository):
    """测试创建用户"""
    # Arrange
    email = "test@example.com"
    username = "testuser"

    # Act
    user = await user_repository.create(email=email, username=username)

    # Assert
    assert user.id is not None
    assert user.email == email
    assert user.username == username
```

#### 集成测试

```python
# tests/integration/test_api_users.py
from httpx import AsyncClient
from app.main import app

async def test_create_user_api():
    """测试用户创建 API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/",
            json={"email": "new@example.com", "username": "newuser"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
```

#### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试文件
poetry run pytest tests/unit/test_user_repository.py

# 生成覆盖率报告
poetry run pytest --cov=app --cov-report=html --cov-report=term

# 查看 HTML 报告
open htmlcov/index.html
```

---

### 前端测试（Vitest + React Testing Library）

#### 组件测试

```typescript
// app/users/__tests__/page.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import UsersPage from '../page';

test('loads and displays users', async () => {
  render(<UsersPage />);

  await waitFor(() => {
    expect(screen.getByText(/Users/i)).toBeInTheDocument();
  });
});

test('creates a new user', async () => {
  const { getByLabelText, getByText } = render(<UsersPage />);

  // Fill form
  fireEvent.change(getByLabelText(/Email/i), {
    target: { value: 'test@example.com' }
  });

  // Submit
  fireEvent.click(getByText(/Create/i));

  // Verify
  await waitFor(() => {
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });
});
```

#### 运行测试

```bash
# 运行所有测试
npm test

# 观察模式
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

---

## Pull Request 流程

### 1. 创建 Pull Request

```bash
# 使用 GitHub CLI
gh pr create \
  --title "feat: add user authentication" \
  --body "Implements JWT-based authentication. Closes #123" \
  --assignee @me \
  --label enhancement
```

### 2. PR 检查清单

在提交 PR 前，确保：

- [ ] 代码遵循项目规范（Ruff/ESLint 通过）
- [ ] 所有测试通过（pytest/npm test）
- [ ] 测试覆盖率 ≥ 80%
- [ ] 更新了相关文档
- [ ] 提交信息遵循 Conventional Commits
- [ ] 没有合并冲突
- [ ] CI/CD 通过

### 3. 代码审查

**审查者关注点**:

- 代码质量和可读性
- 测试覆盖率
- 安全问题（SQL 注入、XSS、硬编码密钥）
- 性能问题（N+1 查询、大循环）
- 错误处理

**审查意见分类**:

- 🔴 **Blocker**: 必须修复才能合并
- 🟡 **Suggestion**: 建议修改
- 🟢 **Nitpick**: 可选改进

### 4. 合并策略

- **Squash and Merge**: 默认策略，保持提交历史简洁
- **Rebase and Merge**: 保留所有提交历史
- **Merge Commit**: 保留分支结构

---

## 常见问题解答

### 后端问题

#### Q1: 数据库连接失败

```bash
# 检查 PostgreSQL 是否启动
docker-compose ps postgres

# 查看日志
docker-compose logs postgres

# 测试连接
poetry run python -c "from app.database.session import engine; engine.connect()"
```

#### Q2: Alembic 迁移失败

```bash
# 查看当前版本
poetry run alembic current

# 回滚到基线
poetry run alembic downgrade base

# 重新升级
poetry run alembic upgrade head
```

#### Q3: Import 错误

```bash
# 重新安装依赖
poetry install

# 检查 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

---

### 前端问题

#### Q1: API 连接失败

```bash
# 检查后端是否启动
curl http://localhost:8000/health

# 检查环境变量
cat frontend/.env.local
# 确保 NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### Q2: 类型错误

```bash
# 运行类型检查
npm run type-check

# 重新生成类型
npm run generate-types
```

#### Q3: 构建失败

```bash
# 清理缓存
rm -rf .next node_modules
npm install
npm run build
```

---

### Docker 问题

#### Q1: 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs <service-name>

# 重启服务
docker-compose restart <service-name>
```

#### Q2: 端口冲突

```bash
# 检查端口占用
lsof -i :3000
lsof -i :8000

# 修改 docker-compose.yml 中的端口映射
```

#### Q3: 磁盘空间不足

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理所有未使用的对象
docker system prune -a --volumes
```

---

## 开发工具推荐

### IDE/编辑器

- **VS Code**: 推荐插件
  - Python (Microsoft)
  - Pylance
  - ESLint
  - Prettier
  - GitLens

- **PyCharm**: 专业 Python IDE
- **WebStorm**: 专业前端 IDE

### Chrome 扩展

- React Developer Tools
- Redux DevTools
- JSONView

### 终端工具

- **httpie**: HTTP 客户端 (`http GET localhost:8000/api/v1/users/`)
- **jq**: JSON 处理 (`curl ... | jq .`)
- **gh**: GitHub CLI

---

## 性能分析

### 后端性能分析

```python
# 使用 cProfile
poetry run python -m cProfile -o profile.stats app/main.py

# 分析结果
poetry run python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

### 前端性能分析

```bash
# Lighthouse 分析
npm run build
npm run start
# 在 Chrome DevTools 中运行 Lighthouse
```

---

## 许可证

MIT License - 详见根目录 [LICENSE](../LICENSE) 文件

---

**最后更新**: 2026-06-17
