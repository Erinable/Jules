# Jules Agent System

完整的 Multi-Agent 协作系统，用于 AI 代码生成、分析和优化。

## 目录

- [系统架构](#系统架构)
- [核心模块](#核心模块)
- [工作流程](#工作流程)
- [使用指南](#使用指南)
- [配置说明](#配置说明)
- [Prompt 模板](#prompt-模板)
- [Mock 模式 vs 真实 API](#mock-模式-vs-真实-api)
- [故障排查](#故障排查)

---

## 系统架构

Jules Agent 系统采用模块化设计，各组件职责清晰：

```
┌─────────────────────────────────────────────────┐
│              API Layer (FastAPI)                │
│          /api/v1/agents/execute                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              Scheduler (调度器)                  │
│  - 任务队列管理                                  │
│  - 并发控制 (max 5)                             │
│  - 优先级调度                                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              Executor (执行引擎)                 │
│  - Agent 执行协调                                │
│  - 状态管理                                      │
│  - 重试机制                                      │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│  LLM Client  │   │   Analyzer   │
│  - OpenAI    │   │   - Ruff     │
│  - Anthropic │   │   - mypy     │
│  - Mock      │   │   - Bandit   │
└──────────────┘   └──────────────┘
        │                 │
        └────────┬────────┘
                 ▼
┌─────────────────────────────────────────────────┐
│              Worker (后台任务)                   │
│  - 异步代码生成                                  │
│  - 质量分析                                      │
│  - 结果持久化                                    │
└─────────────────────────────────────────────────┘
```

---

## 核心模块

### 1. Scheduler (调度器)

**文件**: `scheduler.py`

**职责**:
- 管理任务队列
- 控制并发执行（最多 5 个并发 Agent）
- 按优先级调度任务
- 监控 Agent 状态

**主要方法**:

```python
class AgentScheduler:
    async def schedule_task(self, task_id: int, priority: int) -> str:
        """调度新任务"""
        
    async def get_queue_status(self) -> dict:
        """获取队列状态"""
        
    async def cancel_task(self, task_id: int) -> bool:
        """取消任务"""
```

**使用示例**:

```python
from app.agent.scheduler import AgentScheduler

scheduler = AgentScheduler()

# 调度任务
execution_id = await scheduler.schedule_task(
    task_id=123,
    priority=8
)

# 查看队列状态
status = await scheduler.get_queue_status()
# 返回: {"pending": 3, "running": 2, "completed": 10}
```

---

### 2. Executor (执行引擎)

**文件**: `executor.py`

**职责**:
- 协调 Agent 执行流程
- 管理执行状态（pending, running, completed, failed）
- 实现重试机制（最多 3 次，指数退避）
- 记录执行日志

**主要方法**:

```python
class AgentExecutor:
    async def execute(
        self,
        task_id: int,
        prompt: str,
        context: dict
    ) -> dict:
        """执行 Agent 任务"""
        
    async def get_execution_status(self, execution_id: int) -> dict:
        """获取执行状态"""
        
    async def stop_execution(self, execution_id: int) -> bool:
        """停止执行"""
```

**执行流程**:

1. 接收任务请求
2. 初始化 LLM Client
3. 发送 Prompt 到 LLM
4. 接收生成结果
5. 运行代码分析器
6. 保存结果到数据库
7. 更新执行状态

**使用示例**:

```python
from app.agent.executor import AgentExecutor
from app.agent.llm_client import LLMClient

llm_client = LLMClient(provider="anthropic", model="claude-3-5-sonnet-20241022")
executor = AgentExecutor(llm_client=llm_client)

# 执行任务
result = await executor.execute(
    task_id=123,
    prompt="Generate a Python function to calculate factorial",
    context={
        "language": "python",
        "style": "functional",
        "include_tests": True
    }
)

# 返回:
# {
#   "execution_id": 456,
#   "status": "completed",
#   "output": {
#     "code": "def factorial(n): ...",
#     "analysis": {...},
#     "metrics": {...}
#   }
# }
```

---

### 3. LLM Client (LLM 客户端)

**文件**: `llm_client.py`

**职责**:
- 统一的 LLM 接口（支持多个 Provider）
- 支持 OpenAI、Anthropic Claude
- 自动重试和错误处理
- Token 使用统计
- Mock 模式（开发/测试用）

**支持的 Provider**:

| Provider | 模型 | 用途 |
|----------|------|------|
| OpenAI | gpt-4-turbo, gpt-4, gpt-3.5-turbo | 通用代码生成 |
| Anthropic | claude-3-5-sonnet-20241022, claude-3-opus | 高质量代码生成 |
| Mock | - | 开发和测试 |

**主要方法**:

```python
class LLMClient:
    async def generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> dict:
        """生成代码"""
        
    async def chat(
        self,
        messages: list,
        model: str = None
    ) -> dict:
        """对话式生成"""
        
    def get_token_usage(self) -> dict:
        """获取 Token 使用统计"""
```

**使用示例**:

```python
from app.agent.llm_client import LLMClient

# 使用 Anthropic Claude
llm_client = LLMClient(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)

# 生成代码
result = await llm_client.generate(
    prompt="Generate a REST API endpoint for user login",
    temperature=0.7,
    max_tokens=2000
)

# 查看 Token 使用
usage = llm_client.get_token_usage()
# 返回: {"prompt_tokens": 150, "completion_tokens": 800, "total_tokens": 950}
```

**Mock 模式**:

```python
# 使用 Mock（不调用真实 API）
llm_client = LLMClient(provider="mock")

result = await llm_client.generate(
    prompt="Generate code"
)
# 返回模拟的代码生成结果
```

---

### 4. Analyzer (代码分析器)

**文件**: `analyzer.py`

**职责**:
- 静态代码分析
- 代码质量评估
- 安全漏洞扫描
- 复杂度计算

**分析工具**:

| 工具 | 功能 | 指标 |
|------|------|------|
| Ruff | Linting | 代码规范问题 |
| mypy | Type Checking | 类型错误 |
| Bandit | Security | 安全漏洞 |
| Radon | Complexity | CC（圈复杂度）、MI（可维护性指数） |

**主要方法**:

```python
class CodeAnalyzer:
    async def analyze(
        self,
        code: str,
        language: str = "python"
    ) -> dict:
        """分析代码"""
        
    async def calculate_metrics(self, code: str) -> dict:
        """计算质量指标"""
        
    async def check_security(self, code: str) -> list:
        """安全检查"""
```

**使用示例**:

```python
from app.agent.analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# 分析代码
analysis = await analyzer.analyze(
    code="""
    def calculate(x, y):
        return x + y
    """,
    language="python"
)

# 返回:
# {
#   "linting_issues": [],
#   "type_errors": [],
#   "security_issues": [],
#   "complexity": {
#     "cyclomatic_complexity": 1,
#     "maintainability_index": 95.2
#   }
# }
```

---

### 5. Worker (后台任务)

**文件**: `worker.py`

**职责**:
- 异步执行长时间运行的任务
- 批量代码生成
- 定期质量分析
- 结果持久化

**使用 Celery**（未来版本）:

```python
from celery import Celery

app = Celery('jules', broker='redis://localhost:6379/0')

@app.task
def generate_code_async(task_id: int, prompt: str):
    """异步生成代码"""
    # 执行代码生成
    pass
```

---

## 工作流程

### 标准执行流程

```
1. 用户提交任务
   POST /api/v1/agents/execute
   
2. Scheduler 接收任务
   - 检查并发限制
   - 加入优先级队列
   
3. Executor 开始执行
   - 初始化 LLM Client
   - 加载 Prompt 模板
   
4. LLM Client 生成代码
   - 调用 OpenAI/Anthropic API
   - 流式响应（可选）
   
5. Analyzer 分析代码
   - Ruff linting
   - mypy type check
   - Bandit security scan
   - Radon complexity
   
6. 保存结果
   - 代码存储到 code_files 表
   - 质量指标存储到 quality_metrics 表
   - 执行记录存储到 agent_executions 表
   
7. 返回结果给用户
```

### Multi-Agent 协作流程（高级）

```
1. Researcher Agent
   - 收集需求和上下文
   - 搜索相关代码示例
   
2. Planner Agent
   - 生成实现计划
   - 拆分子任务
   
3. Coder Agent
   - 生成代码
   - 实现功能
   
4. Reviewer Agent
   - 代码审查
   - 提出改进建议
   
5. Tester Agent
   - 生成测试用例
   - 验证功能正确性
```

---

## 使用指南

### 基础用法

```python
from app.agent.scheduler import AgentScheduler
from app.agent.executor import AgentExecutor
from app.agent.llm_client import LLMClient

# 1. 初始化组件
llm_client = LLMClient(provider="anthropic")
executor = AgentExecutor(llm_client=llm_client)
scheduler = AgentScheduler()

# 2. 调度任务
execution_id = await scheduler.schedule_task(
    task_id=123,
    priority=8
)

# 3. 等待执行完成
status = await executor.get_execution_status(execution_id)

# 4. 获取结果
if status["status"] == "completed":
    result = status["output"]
    print(result["code"])
```

### 高级用法：自定义 Prompt

```python
from app.agent.prompts import PROMPT_TEMPLATES

# 使用自定义 Prompt 模板
custom_prompt = """
You are a senior Python developer.
Generate a {function_type} function that:
- {requirement_1}
- {requirement_2}
- Includes type hints
- Has comprehensive docstrings
- Follows PEP 8

Language: {language}
"""

result = await llm_client.generate(
    prompt=custom_prompt.format(
        function_type="async",
        requirement_1="validates user input",
        requirement_2="handles errors gracefully",
        language="python"
    )
)
```

### 流式响应

```python
async for chunk in llm_client.generate_stream(prompt="Generate code"):
    print(chunk, end="", flush=True)
```

---

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# LLM API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Agent 配置
MAX_CONCURRENT_AGENTS=5        # 最大并发数
AGENT_MODE=real                # real 或 mock
DEFAULT_LLM_MODEL=gpt-4        # 默认模型

# 超时设置
TASK_TIMEOUT_SECONDS=300       # 任务超时（秒）

# 重试设置
MAX_RETRY_ATTEMPTS=3           # 最大重试次数
RETRY_BACKOFF_SECONDS=1,5,15   # 重试延迟（秒）

# LangSmith（可选）
LANGSMITH_API_KEY=xxx
LANGSMITH_PROJECT=jules
```

### 代码配置

在 `config.py` 中修改：

```python
class AgentConfig:
    # 并发设置
    MAX_CONCURRENT_AGENTS: int = 5
    
    # 重试设置
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_SECONDS: List[int] = [1, 5, 15]
    
    # LLM 设置
    DEFAULT_LLM_MODEL: str = "gpt-4"
    MAX_TOKENS_PER_REQUEST: int = 4000
    
    # 任务设置
    TASK_TIMEOUT_SECONDS: int = 300
```

---

## Prompt 模板

### 目录结构

```
prompts/
├── __init__.py
├── code_generation.py    # 代码生成 Prompts
├── code_review.py        # 代码审查 Prompts
├── code_refactor.py      # 代码重构 Prompts
└── test_generation.py    # 测试生成 Prompts
```

### 示例：代码生成 Prompt

```python
CODE_GENERATION_PROMPT = """
You are an expert {language} developer.

Task: {task_description}

Requirements:
- Follow best practices and coding standards
- Include comprehensive error handling
- Add type hints (if applicable)
- Write clear docstrings
- Ensure code is production-ready

Context:
{context}

Generate clean, maintainable code:
"""
```

### 使用 Prompt 模板

```python
from app.agent.prompts.code_generation import CODE_GENERATION_PROMPT

prompt = CODE_GENERATION_PROMPT.format(
    language="Python",
    task_description="Create a user authentication function",
    context="FastAPI application with JWT tokens"
)

result = await llm_client.generate(prompt=prompt)
```

---

## Mock 模式 vs 真实 API

### Mock 模式（开发/测试）

**优点**:
- ✅ 无需 API Key
- ✅ 不消耗 Token
- ✅ 响应速度快
- ✅ 可预测的结果

**启用方式**:

```bash
# .env 文件
AGENT_MODE=mock

# 或不设置 API Key（自动启用 Mock）
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
```

**Mock 响应示例**:

```python
{
  "code": "def example():\n    return 'Mock generated code'\n",
  "explanation": "This is a mock response",
  "tokens_used": 0
}
```

---

### 真实 API 模式（生产）

**优点**:
- ✅ 真实 LLM 生成
- ✅ 高质量输出
- ✅ 支持复杂任务

**启用方式**:

```bash
# .env 文件
AGENT_MODE=real
ANTHROPIC_API_KEY=sk-ant-xxx
```

**成本控制**:

```python
# 设置 Token 限制
llm_client = LLMClient(
    provider="anthropic",
    max_tokens=2000  # 限制最大 Token 数
)

# 监控使用
usage = llm_client.get_token_usage()
print(f"Total tokens used: {usage['total_tokens']}")
```

---

## 故障排查

### 1. Agent 执行失败

**症状**: 任务状态为 `failed`

**排查步骤**:

```bash
# 1. 检查日志
docker-compose logs backend | grep agent

# 2. 验证 API Key
echo $ANTHROPIC_API_KEY

# 3. 测试 LLM 连接
poetry run python -c "
from app.agent.llm_client import LLMClient
client = LLMClient(provider='anthropic')
print(client.test_connection())
"

# 4. 切换到 Mock 模式测试
export AGENT_MODE=mock
```

---

### 2. 并发限制问题

**症状**: 任务长时间处于 `pending` 状态

**排查步骤**:

```python
# 检查队列状态
from app.agent.scheduler import AgentScheduler

scheduler = AgentScheduler()
status = await scheduler.get_queue_status()
print(status)
# 如果 running >= MAX_CONCURRENT_AGENTS，说明达到并发限制
```

**解决方案**:

```bash
# 增加并发限制
export MAX_CONCURRENT_AGENTS=10
```

---

### 3. LLM API 超时

**症状**: 请求超时，返回 504 错误

**解决方案**:

```python
# 增加超时时间
llm_client = LLMClient(
    provider="anthropic",
    timeout=60  # 60 秒超时
)

# 或减少 max_tokens
result = await llm_client.generate(
    prompt="...",
    max_tokens=1000  # 降低 Token 数
)
```

---

### 4. 代码分析器错误

**症状**: Analyzer 失败，返回分析错误

**排查步骤**:

```bash
# 手动运行分析工具
cd backend
poetry run ruff check app/
poetry run mypy app/
poetry run bandit -r app/
```

---

### 5. Token 使用过多

**症状**: API 成本过高

**优化建议**:

1. **使用更小的模型**:
   ```python
   # 从 gpt-4 切换到 gpt-3.5-turbo
   llm_client = LLMClient(model="gpt-3.5-turbo")
   ```

2. **减少 Prompt 长度**:
   ```python
   # 精简 Prompt，去除不必要的上下文
   ```

3. **启用缓存**:
   ```python
   # 相同 Prompt 使用缓存结果
   ```

4. **批量处理**:
   ```python
   # 批量生成多个函数，而不是逐个生成
   ```

---

## 性能优化

### 1. 并行执行

```python
import asyncio

# 并行执行多个任务
tasks = [
    executor.execute(task_id=1, prompt="..."),
    executor.execute(task_id=2, prompt="..."),
    executor.execute(task_id=3, prompt="...")
]

results = await asyncio.gather(*tasks)
```

### 2. 结果缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_prompt_template(template_name: str) -> str:
    # 缓存 Prompt 模板
    pass
```

### 3. 流式响应

```python
# 使用流式响应，提升用户体验
async for chunk in llm_client.generate_stream(prompt):
    yield chunk
```

---

## 测试

### 单元测试

```bash
# 测试 LLM Client
poetry run pytest tests/unit/agent/test_llm_client.py

# 测试 Executor
poetry run pytest tests/unit/agent/test_executor.py

# 测试 Analyzer
poetry run pytest tests/unit/agent/test_analyzer.py
```

### 集成测试

```bash
# 端到端测试
poetry run pytest tests/integration/agent/test_agent_execution.py
```

---

## 未来计划

- [ ] 支持更多 LLM Provider（Google PaLM、Cohere）
- [ ] 实现 Multi-Agent 协作（Researcher → Planner → Coder → Reviewer → Tester）
- [ ] 添加 Agent 记忆系统（长期上下文）
- [ ] 支持自定义 Agent 插件
- [ ] 实现 Agent 监控面板
- [ ] 添加 A/B 测试（不同模型/Prompt）
- [ ] 支持 Fine-tuning 自定义模型

---

## 许可证

MIT License - 详见根目录 [LICENSE](../../../LICENSE) 文件

---

**最后更新**: 2026-06-17
