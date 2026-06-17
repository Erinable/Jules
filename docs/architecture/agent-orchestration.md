# Agent 编排架构

**版本**: v1.0  
**日期**: 2026-06-16  
**关联文档**: system-architecture.md  

---

## 1. Agent 角色定义

### 1.1 核心 Agent

```mermaid
graph LR
    Researcher[🔍 Researcher<br/>技术调研]
    Planner[📋 Planner<br/>架构设计]
    Coder[💻 Coder<br/>代码生成]
    Reviewer[👀 Reviewer<br/>代码审查]
    Tester[🧪 Tester<br/>测试生成]
    Optimizer[⚡ Optimizer<br/>重构优化]
    
    Researcher -->|调研报告| Planner
    Planner -->|架构设计| Coder
    Coder -->|代码| Reviewer
    Reviewer -->|审查结果| Tester
    Reviewer -->|需修复| Coder
    Tester -->|测试| Optimizer
    Optimizer -->|优化建议| Coder
```

### 1.2 Agent 职责矩阵

| Agent | 主要职责 | 输入 | 输出 | LLM 模型 |
|-------|---------|------|------|----------|
| **Researcher** | 竞品调研<br/>技术选型<br/>需求分析 | 用户需求<br/>关键词 | 调研报告<br/>技术建议 | Haiku 3.5 |
| **Planner** | 架构设计<br/>任务分解<br/>技术选型 | 调研报告<br/>需求文档 | 架构设计<br/>任务列表 | Opus 4.7 |
| **Coder** | 代码生成<br/>增量编辑<br/>Bug 修复 | 架构设计<br/>任务描述 | Python 代码<br/>测试代码 | Sonnet 4.6 |
| **Reviewer** | 代码审查<br/>质量检查<br/>安全扫描 | 生成的代码 | 审查报告<br/>问题列表 | Haiku 3.5 |
| **Tester** | 单元测试<br/>集成测试<br/>测试验证 | 代码 + 规格 | 测试代码<br/>测试报告 | Haiku 3.5 |
| **Optimizer** | 代码重构<br/>性能优化<br/>复杂度降低 | 代码 + 质量指标 | 优化建议<br/>重构代码 | Sonnet 4.6 |

---

## 2. LangGraph 状态机设计

### 2.1 状态定义

```python
from typing import TypedDict, List, Optional
from enum import Enum

class WorkflowState(TypedDict):
    """工作流全局状态"""
    # 用户输入
    user_requirement: str
    project_type: str  # web/cli/data
    
    # Agent 输出
    research_report: Optional[str]
    architecture_design: Optional[str]
    generated_code: Optional[dict]  # {file_path: code}
    review_result: Optional[dict]
    test_code: Optional[dict]
    quality_metrics: Optional[dict]
    
    # 控制流
    current_agent: str
    iteration_count: int
    max_iterations: int
    errors: List[str]
    
    # 质量门禁
    quality_passed: bool
    complexity_score: float
    maintainability_index: float
```

### 2.2 状态机图

```mermaid
stateDiagram-v2
    [*] --> Researcher: 用户提交需求
    
    Researcher --> Planner: 调研完成
    Planner --> Coder: 架构设计完成
    
    Coder --> QualityGate: 代码生成完成
    
    QualityGate --> Reviewer: 质量检查通过
    QualityGate --> Coder: 质量检查失败<br/>(重新生成)
    
    Reviewer --> Tester: 代码审查通过
    Reviewer --> Coder: 发现问题<br/>(修复代码)
    
    Tester --> Optimizer: 测试通过
    Tester --> Coder: 测试失败<br/>(修复代码)
    
    Optimizer --> [*]: 优化完成
    Optimizer --> Coder: 需要重构
    
    note right of QualityGate
        静态分析门禁:
        - Ruff Lint
        - mypy Type Check
        - Bandit Security
        - Radon Complexity
    end note
```

### 2.3 LangGraph 实现

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 创建状态图
workflow = StateGraph(WorkflowState)

# 添加节点
workflow.add_node("researcher", researcher_agent)
workflow.add_node("planner", planner_agent)
workflow.add_node("coder", coder_agent)
workflow.add_node("quality_gate", quality_gate_check)
workflow.add_node("reviewer", reviewer_agent)
workflow.add_node("tester", tester_agent)
workflow.add_node("optimizer", optimizer_agent)

# 设置入口
workflow.set_entry_point("researcher")

# 添加边（顺序流）
workflow.add_edge("researcher", "planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "quality_gate")

# 添加条件边（质量门禁）
workflow.add_conditional_edges(
    "quality_gate",
    lambda state: "reviewer" if state["quality_passed"] else "coder",
    {
        "reviewer": "reviewer",
        "coder": "coder"
    }
)

# 添加条件边（代码审查）
workflow.add_conditional_edges(
    "reviewer",
    lambda state: "tester" if not state["review_result"]["has_issues"] else "coder",
    {
        "tester": "tester",
        "coder": "coder"
    }
)

# 添加条件边（测试）
workflow.add_conditional_edges(
    "tester",
    lambda state: "optimizer" if state["review_result"]["tests_passed"] else "coder",
    {
        "optimizer": "optimizer",
        "coder": "coder"
    }
)

# 添加条件边（优化器）
workflow.add_conditional_edges(
    "optimizer",
    lambda state: END if state["iteration_count"] >= state["max_iterations"] else "coder",
    {
        END: END,
        "coder": "coder"
    }
)

# 编译工作流（启用检查点）
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

---

## 3. Agent 实现细节

### 3.1 Researcher Agent

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class ResearcherAgent:
    """技术调研 Agent"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",  # 成本低，速度快
            temperature=0.3
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个技术调研专家。
任务：分析用户需求，调研相关技术栈和最佳实践。

输出格式：
1. 需求分析
2. 技术选型建议
3. 竞品分析
4. 风险评估
"""),
            ("user", "{requirement}")
        ])
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """执行调研"""
        chain = self.prompt | self.llm
        result = chain.invoke({"requirement": state["user_requirement"]})
        
        state["research_report"] = result.content
        state["current_agent"] = "researcher"
        return state
```

### 3.2 Planner Agent

```python
class PlannerAgent:
    """架构设计 Agent"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-opus-4-7",  # 深度推理
            temperature=0.5
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个软件架构师。
任务：基于调研报告，设计系统架构和任务分解。

输出格式：
1. 架构设计（分层架构、模块划分）
2. 技术栈选择
3. 任务列表（优先级排序）
4. 文件结构
"""),
            ("user", "调研报告：\n{research_report}\n\n需求：{requirement}")
        ])
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        chain = self.prompt | self.llm
        result = chain.invoke({
            "research_report": state["research_report"],
            "requirement": state["user_requirement"]
        })
        
        state["architecture_design"] = result.content
        state["current_agent"] = "planner"
        return state
```

### 3.3 Coder Agent

```python
class CoderAgent:
    """代码生成 Agent"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",  # 平衡性能和成本
            temperature=0.2
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个 Python 高级工程师。
任务：根据架构设计生成生产级代码。

代码要求：
1. 遵循 PEP 8 规范
2. 添加类型注解（mypy 兼容）
3. 编写 docstring
4. 圈复杂度 < 10
5. 可维护性指数 > 20
6. 无安全漏洞

输出格式：JSON
{
  "files": {
    "file_path": "code_content"
  }
}
"""),
            ("user", "架构设计：\n{architecture}\n\n{additional_context}")
        ])
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        additional_context = ""
        if state.get("review_result"):
            additional_context = f"需要修复的问题：\n{state['review_result']['issues']}"
        
        chain = self.prompt | self.llm
        result = chain.invoke({
            "architecture": state["architecture_design"],
            "additional_context": additional_context
        })
        
        # 解析 JSON
        import json
        code_files = json.loads(result.content)
        
        state["generated_code"] = code_files["files"]
        state["current_agent"] = "coder"
        state["iteration_count"] += 1
        return state
```

### 3.4 Reviewer Agent

```python
class ReviewerAgent:
    """代码审查 Agent"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.1
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个代码审查专家。
任务：审查代码质量、可读性、安全性。

审查维度：
1. 代码风格（PEP 8）
2. 类型注解完整性
3. 错误处理
4. 安全漏洞
5. 性能问题
6. 可维护性

输出格式：JSON
{
  "has_issues": true/false,
  "issues": [
    {"severity": "high/medium/low", "file": "...", "line": 10, "description": "..."}
  ],
  "suggestions": ["..."]
}
"""),
            ("user", "代码：\n{code}\n\n质量指标：\n{metrics}")
        ])
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        code_str = "\n\n".join([
            f"# {path}\n{content}" 
            for path, content in state["generated_code"].items()
        ])
        
        chain = self.prompt | self.llm
        result = chain.invoke({
            "code": code_str,
            "metrics": json.dumps(state["quality_metrics"])
        })
        
        state["review_result"] = json.loads(result.content)
        state["current_agent"] = "reviewer"
        return state
```

---

## 4. 通信机制

### 4.1 Agent 间消息传递

```python
from typing import Protocol

class Message(TypedDict):
    """Agent 消息"""
    sender: str
    receiver: str
    type: str  # request/response/notification
    content: dict
    timestamp: str

class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self.subscribers: dict[str, list[callable]] = {}
    
    def subscribe(self, agent_name: str, handler: callable):
        """订阅消息"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(handler)
    
    def publish(self, message: Message):
        """发布消息"""
        receiver = message["receiver"]
        if receiver in self.subscribers:
            for handler in self.subscribers[receiver]:
                handler(message)
```

### 4.2 状态持久化

```python
from langgraph.checkpoint.postgres import PostgresSaver

# 使用 PostgreSQL 作为检查点存储
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/langgraph"
)

app = workflow.compile(checkpointer=checkpointer)

# 执行工作流（带恢复能力）
config = {"configurable": {"thread_id": "project-123"}}
for output in app.stream(initial_state, config):
    print(output)
```

---

## 5. 任务队列

### 5.1 Celery 集成

```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def run_agent_workflow(project_id: str, requirement: str):
    """异步执行 Agent 工作流"""
    initial_state = WorkflowState(
        user_requirement=requirement,
        project_type="web",
        iteration_count=0,
        max_iterations=3,
        quality_passed=False
    )
    
    config = {"configurable": {"thread_id": project_id}}
    result = app.invoke(initial_state, config)
    
    return result
```

### 5.2 任务监控

```python
from celery.result import AsyncResult

def get_task_status(task_id: str):
    """获取任务状态"""
    result = AsyncResult(task_id, app=celery_app)
    return {
        "state": result.state,  # PENDING/STARTED/SUCCESS/FAILURE
        "info": result.info
    }
```

---

## 6. LangSmith 监控集成

### 6.1 追踪配置

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "ai-code-generator"
```

### 6.2 自定义追踪

```python
from langsmith import traceable

@traceable(run_type="agent", name="researcher")
def researcher_agent(state: WorkflowState) -> WorkflowState:
    # Agent 逻辑
    return state
```

---

## 7. 错误处理与重试

### 7.1 异常处理

```python
class AgentExecutionError(Exception):
    """Agent 执行错误"""
    pass

def safe_agent_call(agent_func):
    """Agent 调用装饰器"""
    def wrapper(state: WorkflowState) -> WorkflowState:
        try:
            return agent_func(state)
        except Exception as e:
            state["errors"].append({
                "agent": state["current_agent"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            # 标记失败，触发重试或终止
            state["quality_passed"] = False
            return state
    return wrapper
```

### 7.2 重试策略

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_llm_with_retry(prompt: str, llm):
    """LLM 调用重试"""
    return llm.invoke(prompt)
```

---

## 8. 性能优化

### 8.1 并行执行

```python
# 对于独立的 Agent 任务，可以并行执行
from concurrent.futures import ThreadPoolExecutor

def parallel_analysis(code: str):
    """并行执行多个分析工具"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(run_ruff, code): "ruff",
            executor.submit(run_mypy, code): "mypy",
            executor.submit(run_bandit, code): "bandit",
            executor.submit(run_radon, code): "radon"
        }
        
        results = {}
        for future in as_completed(futures):
            tool_name = futures[future]
            results[tool_name] = future.result()
        
        return results
```

### 8.2 缓存策略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_research(requirement_hash: str):
    """缓存调研结果"""
    # 如果需求相似，复用调研结果
    pass

def compute_requirement_hash(requirement: str) -> str:
    """计算需求哈希"""
    return hashlib.sha256(requirement.encode()).hexdigest()
```

---

## 9. 工作流示例

### 9.1 简单 FastAPI 项目生成

```python
initial_state = WorkflowState(
    user_requirement="创建一个用户管理 API，支持 CRUD 操作，使用 FastAPI + SQLAlchemy",
    project_type="web",
    iteration_count=0,
    max_iterations=3,
    quality_passed=False,
    errors=[]
)

config = {"configurable": {"thread_id": "fastapi-user-api"}}
result = app.invoke(initial_state, config)

print(f"生成的文件：{result['generated_code'].keys()}")
print(f"质量指标：{result['quality_metrics']}")
```

### 9.2 带恢复的执行

```python
# 第一次执行（可能中断）
config = {"configurable": {"thread_id": "project-456"}}
app.invoke(initial_state, config)

# 从检查点恢复
state_snapshot = app.get_state(config)
print(f"上次执行到：{state_snapshot.values['current_agent']}")

# 继续执行
result = app.invoke(None, config)  # None 表示从检查点恢复
```

---

## 10. 关键决策（ADR）

### ADR-006: 选择显式状态机而非隐式编排

**决策**：使用 LangGraph 显式定义状态转换

**理由**：
1. 可追溯性：每个状态转换有明确记录
2. 可调试性：容易定位问题节点
3. 可扩展性：新增 Agent 只需添加节点和边

**影响**：
- 需要编写更多样板代码
- 状态定义需要仔细设计
- 灵活性高，可处理复杂场景

### ADR-007: 质量门禁作为独立节点

**决策**：质量检查作为 LangGraph 独立节点，而非 Reviewer Agent 内部逻辑

**理由**：
1. 分离关注点：静态分析与人工审查解耦
2. 快速失败：避免调用 LLM 审查低质量代码
3. 成本控制：静态分析成本低

**影响**：
- 状态机更复杂（多一个节点）
- 用户体验更好（实时质量反馈）

### ADR-008: 使用 Haiku 而非 Sonnet 做审查

**决策**：Reviewer/Tester Agent 使用 Haiku 3.5

**理由**：
1. 成本低（Haiku 便宜 10 倍）
2. 速度快（响应时间 < 1s）
3. 能力足够（审查不需要深度推理）

**影响**：
- 审查深度可能不如 Opus
- 通过静态分析补充
- 总体成本大幅降低


