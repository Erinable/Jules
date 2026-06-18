# Python 项目类型特征分析

## 概述

本文档分析三种主要 Python 项目类型的架构特征、技术栈模式和最佳实践，为通用框架设计提供依据。

---

## 1. Web 应用

### 1.1 典型文件结构

#### FastAPI 项目结构

```
fastapi-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── dependencies.py      # 依赖注入
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── users.py
│   │   │   │   └── items.py
│   │   │   └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── db/
│       ├── __init__.py
│       ├── base.py
│       └── session.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
├── alembic/                 # 数据库迁移
├── .env.example
├── requirements.txt
└── pyproject.toml
```

#### Flask 项目结构

```
flask-app/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── templates/
│   ├── static/
│   └── blueprints/
│       ├── auth/
│       └── main/
├── tests/
├── migrations/              # Flask-Migrate
├── config.py
└── run.py
```

#### Django 项目结构

```
django-project/
├── project_name/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── api/
├── static/
├── media/
├── templates/
└── manage.py
```

### 1.2 常用依赖

#### 核心框架

- **FastAPI**: `fastapi`, `uvicorn`, `pydantic`
- **Flask**: `flask`, `flask-sqlalchemy`, `flask-migrate`
- **Django**: `django`, `djangorestframework`, `django-cors-headers`

#### 数据库 & ORM

- **ORM**: `sqlalchemy`, `alembic`, `tortoise-orm`
- **数据库驱动**: `psycopg2-binary` (PostgreSQL), `pymysql` (MySQL)
- **连接池**: `asyncpg` (异步 PostgreSQL)

#### 认证 & 安全

- `python-jose[cryptography]`, `passlib[bcrypt]`
- `python-multipart` (文件上传)
- `pyjwt`

#### 中间件 & 工具

- `python-dotenv` (环境变量)
- `loguru` (日志)
- `httpx` (HTTP 客户端)
- `celery` (异步任务)
- `redis` (缓存)

### 1.3 测试策略

#### 测试框架

- **单元测试**: `pytest`, `pytest-asyncio`, `pytest-cov`
- **集成测试**: `pytest-django`, `flask-testing`
- **E2E 测试**: `playwright`, `selenium`

#### 测试模式

```python
# FastAPI 测试示例
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post("/api/v1/users/", json={"email": "test@example.com"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

#### 覆盖率目标

- 单元测试: 80%+
- 集成测试: 关键业务流程
- E2E 测试: 核心用户路径

### 1.4 部署方式

#### 容器化部署

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 部署选项

- **ASGI 服务器**: Uvicorn, Gunicorn + Uvicorn workers
- **WSGI 服务器**: Gunicorn, uWSGI
- **容器编排**: Docker Compose, Kubernetes
- **云平台**: AWS (ECS, Lambda), GCP (Cloud Run), Azure

#### 配置管理

- 环境变量 + `.env` 文件
- 分层配置: `config/base.py`, `config/production.py`
- 密钥管理: AWS Secrets Manager, HashiCorp Vault

---

## 2. CLI 工具

### 2.1 典型文件结构

#### Click/Typer 项目结构

```
cli-tool/
├── cli_tool/
│   ├── __init__.py
│   ├── cli.py               # 主入口
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── config.py
│   │   └── run.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── utils.py
│   └── models/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

### 2.2 常用依赖

#### CLI 框架

- **Click**: 成熟稳定，装饰器风格
- **Typer**: 基于类型注解，现代化
- **argparse**: 标准库，适合简单场景

#### 配置管理

- `pydantic` (配置验证)
- `pydantic-settings` (环境变量)
- `toml`, `pyyaml` (配置文件)
- `python-dotenv`

#### 输出 & 交互

- `rich` (美化输出、进度条)
- `colorama` (跨平台颜色)
- `questionary` (交互式提示)
- `tabulate` (表格输出)

#### 其他工具

- `pathlib` (路径处理)
- `loguru` (日志)
- `requests` (HTTP)

### 2.3 测试策略

#### 测试工具

- `pytest`
- `click.testing.CliRunner` (Click)
- `typer.testing.CliRunner` (Typer)

#### 测试示例

```python
from click.testing import CliRunner
from cli_tool.cli import cli

def test_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['init', '--name', 'test'])
        assert result.exit_code == 0
        assert 'initialized' in result.output.lower()
```

#### 测试覆盖

- 命令解析正确性
- 错误处理
- 边界条件
- 配置文件读写

### 2.4 部署方式

#### 打包分发

- **PyPI**: `poetry publish`, `twine upload`
- **可执行文件**: `PyInstaller`, `cx_Freeze`
- **系统包**: `fpm` (deb, rpm)

#### 安装方式

```bash
# pip 安装
pip install cli-tool

# pipx 安装（隔离环境）
pipx install cli-tool

# 开发模式
pip install -e .
```

#### 配置文件位置

- Linux/macOS: `~/.config/cli-tool/config.yaml`
- Windows: `%APPDATA%\cli-tool\config.yaml`
- 使用 `platformdirs` 库自动处理跨平台路径

---

## 3. 数据分析脚本

### 3.1 典型文件结构

```
data-analysis-project/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_analysis.ipynb
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── engineering.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── predictor.py
│   └── visualization/
│       ├── __init__.py
│       └── plots.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── tests/
├── reports/
├── requirements.txt
└── README.md
```

### 3.2 常用依赖

#### 数据处理

- `pandas` (数据框操作)
- `numpy` (数值计算)
- `polars` (高性能替代 pandas)
- `dask` (大数据并行处理)

#### 可视化

- `matplotlib` (基础绘图)
- `seaborn` (统计可视化)
- `plotly` (交互式图表)
- `altair` (声明式可视化)

#### 机器学习

- `scikit-learn` (经典 ML)
- `xgboost`, `lightgbm` (梯度提升)
- `statsmodels` (统计建模)

#### Notebook 工具

- `jupyter`, `jupyterlab`
- `ipywidgets` (交互式组件)
- `papermill` (Notebook 自动化)

#### 数据管道

- `prefect`, `dagster` (工作流编排)
- `great_expectations` (数据质量)

### 3.3 测试策略

#### 测试框架

- `pytest`
- `pytest-dataframe` (DataFrame 断言)
- `hypothesis` (基于属性的测试)

#### 测试示例

```python
import pandas as pd
from src.data.preprocessor import clean_data

def test_clean_data_removes_nulls():
    df = pd.DataFrame({'a': [1, 2, None], 'b': [4, None, 6]})
    result = clean_data(df)
    assert result.isnull().sum().sum() == 0
```

#### 测试覆盖

- 数据加载和验证
- 预处理逻辑
- 特征工程函数
- 模型输入/输出格式

### 3.4 部署方式

#### Notebook 部署

- **Voilà**: 将 Notebook 转为 Web 应用
- **Streamlit**: 快速构建数据应用
- **Dash**: Plotly 生态的仪表盘框架

#### 自动化执行

```bash
# Papermill 执行 Notebook
papermill input.ipynb output.ipynb -p param1 value1

# 定时任务
cron: 0 2 * * * papermill analysis.ipynb results/$(date +\%Y\%m\%d).ipynb
```

#### 容器化

```dockerfile
FROM jupyter/scipy-notebook:latest
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY notebooks/ /home/jovyan/work/
```

---

## 4. 通用抽象层设计建议

### 4.1 共性分析

所有三种项目类型都需要：

1. **配置管理**
   - 环境变量加载
   - 多环境配置（dev/staging/prod）
   - 配置验证

2. **日志系统**
   - 结构化日志
   - 日志级别控制
   - 日志输出目标（文件/控制台）

3. **错误处理**
   - 统一异常基类
   - 错误码定义
   - 友好的错误消息

4. **测试框架**
   - pytest 基础设施
   - 测试 fixture
   - 覆盖率报告

### 4.2 通用抽象层架构

```
common-framework/
├── config/
│   ├── __init__.py
│   ├── base.py              # BaseConfig 类
│   └── loader.py            # 配置加载器
├── logging/
│   ├── __init__.py
│   └── logger.py            # 统一日志接口
├── errors/
│   ├── __init__.py
│   └── exceptions.py        # 自定义异常
├── testing/
│   ├── __init__.py
│   └── fixtures.py          # 通用测试 fixture
└── utils/
    ├── __init__.py
    ├── path.py              # 路径处理
    └── validation.py        # 数据验证
```

### 4.3 项目类型特化层

#### Web 应用特化

```python
from common_framework.config import BaseConfig

class WebConfig(BaseConfig):
    database_url: str
    cors_origins: list[str]
    secret_key: str
```

#### CLI 工具特化

```python
from common_framework.config import BaseConfig

class CLIConfig(BaseConfig):
    config_dir: Path
    log_level: str
    output_format: str  # json, yaml, table
```

#### 数据分析特化

```python
from common_framework.config import BaseConfig

class DataConfig(BaseConfig):
    data_dir: Path
    cache_enabled: bool
    parallel_workers: int
```

### 4.4 核心组件设计

#### 配置管理

```python
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    app_name: str
    environment: str = "development"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "APP_"
```

#### 日志系统

```python
from loguru import logger

class Logger:
    @staticmethod
    def setup(config: BaseConfig):
        logger.remove()
        logger.add(
            sys.stderr,
            level=config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        if config.log_file:
            logger.add(config.log_file, rotation="500 MB")
```

#### 错误处理

```python
class AppError(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ConfigError(AppError):
    """配置错误"""
    pass

class ValidationError(AppError):
    """验证错误"""
    pass
```

### 4.5 项目模板生成器

#### 模板结构

```python
templates = {
    "web": {
        "framework": ["fastapi", "flask", "django"],
        "database": ["sqlite", "postgresql", "mysql"],
        "auth": ["jwt", "session", "oauth2"]
    },
    "cli": {
        "framework": ["click", "typer"],
        "config_format": ["yaml", "toml", "json"]
    },
    "data": {
        "notebook": ["jupyter", "jupyterlab"],
        "viz": ["matplotlib", "plotly", "seaborn"]
    }
}
```

#### 生成器命令

```bash
# 生成 FastAPI 项目
python -m framework_gen create --type web --framework fastapi --database postgresql

# 生成 CLI 项目
python -m framework_gen create --type cli --framework typer

# 生成数据分析项目
python -m framework_gen create --type data --notebook jupyterlab
```

---

## 5. 关键差异对比

| 特性 | Web 应用 | CLI 工具 | 数据分析 |
|------|---------|---------|---------|
| **主要交互** | HTTP 请求/响应 | 命令行参数 | Notebook/脚本 |
| **状态管理** | 数据库持久化 | 配置文件 | 数据文件 |
| **并发模型** | 多线程/异步 | 单进程 | 并行计算 |
| **输出格式** | JSON/HTML | 文本/表格 | 图表/报告 |
| **部署目标** | 服务器/云 | 用户本地 | Notebook 服务器 |
| **主要依赖** | Web 框架 + ORM | CLI 框架 + 配置库 | 数据科学栈 |

---

## 6. 实施建议

### 6.1 通用框架实现步骤

1. **第一阶段：核心抽象层**
   - 配置管理（Pydantic Settings）
   - 日志系统（Loguru）
   - 错误处理（自定义异常体系）

2. **第二阶段：项目模板**
   - Web 应用模板（FastAPI + SQLAlchemy）
   - CLI 工具模板（Typer + Rich）
   - 数据分析模板（Jupyter + Pandas）

3. **第三阶段：工具链**
   - 项目生成器（Cookiecutter 或自定义）
   - 开发工具（linting, formatting, type checking）
   - CI/CD 模板（GitHub Actions）

### 6.2 技术选型建议

#### 优先使用现代工具

- **包管理**: Poetry > pip + requirements.txt
- **类型检查**: mypy, pyright
- **代码质量**: ruff (linting + formatting)
- **测试**: pytest + pytest-cov

#### 配置管理

- Pydantic Settings（类型安全 + 验证）
- python-dotenv（环境变量）
- dynaconf（多环境配置）

#### 日志

- Loguru（简单强大）
- structlog（结构化日志）

### 6.3 最佳实践

1. **不可变性原则**
   - 使用 dataclass(frozen=True) 或 Pydantic 模型
   - 避免全局状态

2. **依赖注入**
   - FastAPI: Depends()
   - 手动实现工厂模式

3. **配置分层**

   ```
   base.py         # 通用配置
   development.py  # 开发环境
   production.py   # 生产环境
   ```

4. **测试覆盖**
   - 单元测试: 80%+
   - 关键路径: 100%
   - 边界条件和错误处理

---

## 7. 总结

### 7.1 核心发现

1. **共性大于差异**: 三种项目类型都需要配置、日志、错误处理和测试
2. **框架选型趋势**: 现代化、类型安全、开发体验优先
3. **工具链标准化**: Poetry + Ruff + pytest 成为主流

### 7.2 通用框架设计原则

1. **模块化**: 核心抽象层 + 项目类型特化层
2. **可扩展**: 插件机制支持自定义扩展
3. **开箱即用**: 提供项目模板和生成器
4. **最佳实践**: 内置类型检查、测试、CI/CD 配置

### 7.3 下一步行动

1. 实现通用抽象层核心模块
2. 创建三种项目类型的模板
3. 开发项目生成器 CLI 工具
4. 编写完整文档和示例
5. 构建测试套件验证框架可用性
