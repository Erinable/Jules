# 数据模型设计

**版本**: v1.0  
**日期**: 2026-06-16  

---

## 1. 数据库选择：PostgreSQL 16+

### 选择理由
- 事务支持（ACID）
- 复杂查询性能优异
- JSONB 支持灵活扩展
- 成熟的 ORM 支持（SQLAlchemy）

---

## 2. 核心数据模型

### 2.1 ER 图

```mermaid
erDiagram
    User ||--o{ Project : owns
    Project ||--o{ Task : contains
    Project ||--o{ CodeFile : contains
    Project ||--o{ QualityMetric : tracks
    Task ||--o{ AgentExecution : executes
    AgentExecution ||--o{ LLMCall : makes
    CodeFile ||--o{ CodeVersion : versions
    
    User {
        uuid id PK
        string email
        string name
        timestamp created_at
    }
    
    Project {
        uuid id PK
        uuid user_id FK
        string name
        string type
        json config
        string status
        timestamp created_at
    }
    
    Task {
        uuid id PK
        uuid project_id FK
        string title
        text description
        string status
        int priority
        timestamp created_at
    }
    
    AgentExecution {
        uuid id PK
        uuid task_id FK
        string agent_type
        json state
        string status
        timestamp started_at
        timestamp completed_at
    }
    
    CodeFile {
        uuid id PK
        uuid project_id FK
        string path
        text content
        string hash
        timestamp updated_at
    }
    
    CodeVersion {
        uuid id PK
        uuid file_id FK
        text content
        string commit_hash
        timestamp created_at
    }
    
    QualityMetric {
        uuid id PK
        uuid project_id FK
        float avg_complexity
        float maintainability_index
        int security_issues
        timestamp measured_at
    }
```

### 2.2 SQLAlchemy 模型定义

```python
from sqlalchemy import Column, String, Integer, Float, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(200), nullable=False)
    type = Column(String(50))  # web/cli/data
    config = Column(JSON)
    status = Column(String(50))  # pending/in_progress/completed/failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    code_files = relationship("CodeFile", back_populates="project")
    quality_metrics = relationship("QualityMetric", back_populates="project")

class CodeFile(Base):
    __tablename__ = "code_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    path = Column(String(500), nullable=False)
    content = Column(Text)
    hash = Column(String(64))  # SHA256
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="code_files")
    versions = relationship("CodeVersion", back_populates="file")

class QualityMetric(Base):
    __tablename__ = "quality_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    avg_complexity = Column(Float)
    maintainability_index = Column(Float)
    security_issues = Column(Integer)
    test_coverage = Column(Float)
    measured_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="quality_metrics")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="tasks")
    executions = relationship("AgentExecution", back_populates="task")

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    agent_type = Column(String(50), nullable=False)
    state = Column(JSON)
    status = Column(String(50), default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    task = relationship("Task", back_populates="executions")
    llm_calls = relationship("LLMCall", back_populates="execution")

class CodeVersion(Base):
    __tablename__ = "code_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("code_files.id"))
    content = Column(Text)
    version_number = Column(Integer, nullable=False)
    commit_hash = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file = relationship("CodeFile", back_populates="versions")

class LLMCall(Base):
    __tablename__ = "llm_calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("agent_executions.id"))
    model = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    execution = relationship("AgentExecution", back_populates="llm_calls")
```

---

## 3. Redis 缓存设计

### 3.1 缓存键设计

| 用途 | 键模式 | TTL | 数据结构 |
|------|--------|-----|---------|
| 会话 | `session:{user_id}` | 24h | Hash |
| 任务状态 | `task:{task_id}` | 1h | Hash |
| 质量结果缓存 | `quality:{code_hash}` | 7d | String (JSON) |
| 实时进度 | `progress:{project_id}` | 1h | String (JSON) |
| 任务队列 | `queue:agent_tasks` | - | List |

### 3.2 发布/订阅

```python
# 实时状态更新
redis_client.publish(f"project:{project_id}:status", json.dumps({
    "status": "in_progress",
    "current_agent": "coder",
    "progress": 60
}))
```

---

## 4. 数据访问层（Repository 模式）

```python
from typing import Optional, List
from sqlalchemy.orm import Session

class ProjectRepository:
    """项目仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: uuid.UUID, name: str, project_type: str) -> Project:
        project = Project(
            user_id=user_id,
            name=name,
            type=project_type,
            status="pending"
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def list_by_user(self, user_id: uuid.UUID, limit: int = 10) -> List[Project]:
        return self.db.query(Project)\
            .filter(Project.user_id == user_id)\
            .order_by(Project.created_at.desc())\
            .limit(limit)\
            .all()

class UserRepository:
    """用户仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, name: str) -> User:
        user = User(email=email, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def update(self, user_id: uuid.UUID, name: str) -> bool:
        """更新用户信息（数据库操作）
        
        返回：操作是否成功
        注意：此方法修改数据库状态，调用方应重新查询获取最新对象
        """
        result = self.db.query(User).filter(User.id == user_id).update({"name": name})
        self.db.commit()
        return result > 0

class TaskRepository:
    """任务仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, project_id: uuid.UUID, title: str, description: str) -> Task:
        task = Task(project_id=project_id, title=title, description=description, status="pending", priority=0)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_by_project(self, project_id: uuid.UUID) -> List[Task]:
        return self.db.query(Task)\
            .filter(Task.project_id == project_id)\
            .order_by(Task.created_at.desc())\
            .all()
    
    def get_by_status(self, project_id: uuid.UUID, status: str) -> List[Task]:
        return self.db.query(Task)\
            .filter(Task.project_id == project_id, Task.status == status)\
            .order_by(Task.priority.desc(), Task.created_at.asc())\
            .all()
    
    def update_status(self, task_id: uuid.UUID, status: str) -> bool:
        """更新任务状态（数据库操作）
        
        返回：操作是否成功
        注意：此方法修改数据库状态，调用方应重新查询获取最新对象
        """
        result = self.db.query(Task).filter(Task.id == task_id).update({"status": status})
        self.db.commit()
        return result > 0

class AgentExecutionRepository:
    """Agent 执行仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, task_id: uuid.UUID, agent_type: str, state: dict) -> AgentExecution:
        execution = AgentExecution(
            task_id=task_id,
            agent_type=agent_type,
            state=state,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_by_id(self, execution_id: uuid.UUID) -> Optional[AgentExecution]:
        return self.db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
    
    def get_by_task(self, task_id: uuid.UUID) -> List[AgentExecution]:
        return self.db.query(AgentExecution)\
            .filter(AgentExecution.task_id == task_id)\
            .order_by(AgentExecution.started_at.desc())\
            .all()
    
    def update_status(self, execution_id: uuid.UUID, status: str, state: dict = None) -> bool:
        """更新执行状态（数据库操作）
        
        返回：操作是否成功
        注意：此方法修改数据库状态，调用方应重新查询获取最新对象
        """
        update_data = {"status": status}
        if state:
            update_data["state"] = state
        if status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow()
        
        result = self.db.query(AgentExecution).filter(AgentExecution.id == execution_id).update(update_data)
        self.db.commit()
        return result > 0

class CodeFileRepository:
    """代码文件仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, project_id: uuid.UUID, path: str, content: str, file_hash: str) -> CodeFile:
        code_file = CodeFile(
            project_id=project_id,
            path=path,
            content=content,
            hash=file_hash
        )
        self.db.add(code_file)
        self.db.commit()
        self.db.refresh(code_file)
        return code_file
    
    def get_by_id(self, file_id: uuid.UUID) -> Optional[CodeFile]:
        return self.db.query(CodeFile).filter(CodeFile.id == file_id).first()
    
    def get_by_path(self, project_id: uuid.UUID, path: str) -> Optional[CodeFile]:
        return self.db.query(CodeFile)\
            .filter(CodeFile.project_id == project_id, CodeFile.path == path)\
            .first()
    
    def list_by_project(self, project_id: uuid.UUID) -> List[CodeFile]:
        return self.db.query(CodeFile)\
            .filter(CodeFile.project_id == project_id)\
            .order_by(CodeFile.path)\
            .all()
    
    def update_content(self, file_id: uuid.UUID, content: str, file_hash: str) -> bool:
        """更新文件内容（数据库操作）
        
        返回：操作是否成功
        注意：此方法修改数据库状态，调用方应重新查询获取最新对象
        """
        result = self.db.query(CodeFile).filter(CodeFile.id == file_id).update({
            "content": content,
            "hash": file_hash,
            "updated_at": datetime.utcnow()
        })
        self.db.commit()
        return result > 0

class QualityMetricRepository:
    """质量指标仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, project_id: uuid.UUID, avg_complexity: float, 
               maintainability_index: float, security_issues: int, 
               test_coverage: float) -> QualityMetric:
        metric = QualityMetric(
            project_id=project_id,
            avg_complexity=avg_complexity,
            maintainability_index=maintainability_index,
            security_issues=security_issues,
            test_coverage=test_coverage
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric
    
    def get_latest(self, project_id: uuid.UUID) -> Optional[QualityMetric]:
        return self.db.query(QualityMetric)\
            .filter(QualityMetric.project_id == project_id)\
            .order_by(QualityMetric.measured_at.desc())\
            .first()
    
    def get_history(self, project_id: uuid.UUID, limit: int = 10) -> List[QualityMetric]:
        return self.db.query(QualityMetric)\
            .filter(QualityMetric.project_id == project_id)\
            .order_by(QualityMetric.measured_at.desc())\
            .limit(limit)\
            .all()

class CodeVersionRepository:
    """代码版本仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, file_id: uuid.UUID, content: str, version_number: int, commit_hash: str = None) -> CodeVersion:
        """创建代码版本记录"""
        version = CodeVersion(
            file_id=file_id,
            content=content,
            version_number=version_number,
            commit_hash=commit_hash
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def get_by_id(self, version_id: uuid.UUID) -> Optional[CodeVersion]:
        """根据 ID 获取版本"""
        return self.db.query(CodeVersion).filter(CodeVersion.id == version_id).first()
    
    def get_latest(self, file_id: uuid.UUID) -> Optional[CodeVersion]:
        """获取文件的最新版本"""
        return self.db.query(CodeVersion)\
            .filter(CodeVersion.file_id == file_id)\
            .order_by(CodeVersion.version_number.desc())\
            .first()
    
    def get_history(self, file_id: uuid.UUID, limit: int = 10) -> List[CodeVersion]:
        """获取文件的版本历史"""
        return self.db.query(CodeVersion)\
            .filter(CodeVersion.file_id == file_id)\
            .order_by(CodeVersion.version_number.desc())\
            .limit(limit)\
            .all()
    
    def get_by_version_number(self, file_id: uuid.UUID, version_number: int) -> Optional[CodeVersion]:
        """根据版本号获取特定版本"""
        return self.db.query(CodeVersion)\
            .filter(CodeVersion.file_id == file_id, CodeVersion.version_number == version_number)\
            .first()
```

---

## 5. 数据库优化建议

### 5.1 索引策略

```sql
-- 用户查询索引
CREATE INDEX idx_users_email ON users(email);

-- 项目查询索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- 任务查询索引
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC, created_at ASC);
CREATE UNIQUE INDEX idx_tasks_project_created ON tasks(project_id, created_at);

-- Agent 执行索引
CREATE INDEX idx_agent_executions_task_id ON agent_executions(task_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_started_at ON agent_executions(started_at DESC);

-- 代码文件索引
CREATE INDEX idx_code_files_project_id ON code_files(project_id);
CREATE UNIQUE INDEX idx_code_files_project_path ON code_files(project_id, path);
CREATE INDEX idx_code_files_hash ON code_files(hash);

-- 质量指标索引
CREATE INDEX idx_quality_metrics_project_id ON quality_metrics(project_id);
CREATE INDEX idx_quality_metrics_measured_at ON quality_metrics(measured_at DESC);

-- 代码版本索引
CREATE INDEX idx_code_versions_file_id ON code_versions(file_id);
CREATE INDEX idx_code_versions_file_version ON code_versions(file_id, version_number DESC);
CREATE INDEX idx_code_versions_commit_hash ON code_versions(commit_hash);
```

### 5.2 分区策略

对于大量历史数据，可以考虑按时间分区：

```sql
-- 按月分区的质量指标表
CREATE TABLE quality_metrics_2026_01 PARTITION OF quality_metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE quality_metrics_2026_02 PARTITION OF quality_metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

### 5.3 查询优化

**使用 EXPLAIN ANALYZE**：
```sql
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE project_id = 'xxx' AND status = 'pending'
ORDER BY priority DESC, created_at ASC;
```

**使用连接池**：
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # 连接健康检查
)
```

**批量插入优化**：
```python
def bulk_create_tasks(tasks_data: List[dict]):
    """批量创建任务"""
    tasks = [Task(**data) for data in tasks_data]
    db.bulk_save_objects(tasks)
    db.commit()
```

### 5.4 数据归档策略

**归档旧数据**：
```python
def archive_old_metrics(days: int = 90):
    """归档 90 天前的质量指标数据"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    old_metrics = db.query(QualityMetric)\
        .filter(QualityMetric.measured_at < cutoff_date)\
        .all()
    
    # 导出到归档表或文件
    for metric in old_metrics:
        archive_metric(metric)
    
    # 删除原数据
    db.query(QualityMetric)\
        .filter(QualityMetric.measured_at < cutoff_date)\
        .delete()
    db.commit()
```

### 5.5 监控与维护

**定期 VACUUM**：
```sql
-- 自动 VACUUM 配置
ALTER TABLE tasks SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE agent_executions SET (autovacuum_vacuum_scale_factor = 0.1);
```

**慢查询监控**：
```sql
-- 开启慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1秒以上的查询
ALTER SYSTEM SET log_statement = 'all';
```

**连接池监控**：
```python
from prometheus_client import Gauge

db_pool_size = Gauge('db_pool_size', 'Database connection pool size')
db_pool_overflow = Gauge('db_pool_overflow', 'Database connection pool overflow')

def monitor_pool():
    pool = engine.pool
    db_pool_size.set(pool.size())
    db_pool_overflow.set(pool.overflow())
```

### 5.6 数据迁移策略（Alembic）

**Alembic 初始化**：
```bash
# 安装 Alembic
pip install alembic

# 初始化 Alembic（在项目根目录）
alembic init alembic

# 配置 alembic.ini 中的数据库连接
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

**版本管理流程**：

1. **生成迁移脚本**（模型变更后）：
```bash
alembic revision --autogenerate -m "add code_version table"
```

2. **审查生成的迁移脚本**（确保正确性）：
   - 检查 `upgrade()` 函数：创建表、添加字段、修改索引
   - 检查 `downgrade()` 函数：回滚逻辑
   - 手动调整自动生成的脚本（如有必要）

3. **应用迁移**：
```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision_id>

# 升级一个版本
alembic upgrade +1
```

4. **回滚迁移**：
```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>

# 回滚所有迁移
alembic downgrade base
```

**迁移脚本示例**：
```python
"""add code_version table

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-06-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'code_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('file_id', UUID(as_uuid=True), sa.ForeignKey('code_files.id'), nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('version_number', sa.Integer, nullable=False),
        sa.Column('commit_hash', sa.String(64)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    op.create_index('idx_code_version_file', 'code_versions', ['file_id', 'version_number'])

def downgrade():
    op.drop_index('idx_code_version_file', 'code_versions')
    op.drop_table('code_versions')
```

**迁移最佳实践**：

- ✅ **原子性**：每次模型变更创建一个独立迁移
- ✅ **可逆性**：迁移脚本必须包含 upgrade 和 downgrade 逻辑
- ✅ **测试优先**：生产环境迁移前先在测试环境验证
- ✅ **备份优先**：执行生产迁移前必须备份数据库
- ✅ **文档化**：在迁移脚本注释中记录变更原因和影响范围
- ✅ **版本控制**：迁移脚本纳入 Git 版本控制
- ✅ **顺序执行**：团队成员按顺序应用迁移，避免冲突

**生产环境迁移检查清单**：
```bash
# 1. 备份数据库
pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 查看待应用的迁移
alembic current
alembic history

# 3. 在只读副本上测试迁移
alembic upgrade head --sql > migration.sql  # 生成 SQL 预览

# 4. 应用迁移
alembic upgrade head

# 5. 验证结果
psql -d dbname -c "\d code_versions"  # 检查表结构
```

**常见迁移场景**：

```python
# 添加字段（带默认值）
def upgrade():
    op.add_column('tasks', sa.Column('assignee_id', UUID, nullable=True))

# 删除字段
def upgrade():
    op.drop_column('tasks', 'old_field')

# 重命名字段
def upgrade():
    op.alter_column('tasks', 'old_name', new_column_name='new_name')

# 修改字段类型
def upgrade():
    op.alter_column('tasks', 'priority', type_=sa.SmallInteger)

# 添加索引
def upgrade():
    op.create_index('idx_tasks_status', 'tasks', ['status'])

# 数据迁移
def upgrade():
    connection = op.get_bind()
    connection.execute(
        "UPDATE tasks SET status = 'pending' WHERE status IS NULL"
    )
```

---

## 6. 数据一致性保证

### 6.1 事务管理

```python
from contextlib import contextmanager

@contextmanager
def transaction_scope():
    """提供事务作用域"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# 使用示例
with transaction_scope() as session:
    project_repo = ProjectRepository(session)
    task_repo = TaskRepository(session)
    
    project = project_repo.create(user_id, "New Project", "web")
    task_repo.create(project.id, "Initial Task", "Setup project")
```

### 6.2 乐观锁

```python
class Project(Base):
    __tablename__ = "projects"
    
    # ... 其他字段
    version = Column(Integer, default=1, nullable=False)
    
    def update_with_version(self, **kwargs):
        """使用版本号更新，防止并发冲突"""
        current_version = self.version
        self.version += 1
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # 检查版本号是否匹配
        result = db.query(Project)\
            .filter(Project.id == self.id, Project.version == current_version)\
            .update({**kwargs, "version": self.version})
        
        if result == 0:
            raise ConcurrentUpdateError("Project was modified by another process")
        
        db.commit()
```

---

## 7. 总结

本文档定义了 Jules 项目的完整数据模型，包括：

1. ✅ **核心实体模型**：User、Project、Task、AgentExecution、CodeFile、CodeVersion、QualityMetric、LLMCall
2. ✅ **数据访问层**：完整的 Repository 实现（6 个核心 Repository），遵循不可变性原则
3. ✅ **缓存设计**：Redis 缓存策略和发布/订阅机制
4. ✅ **性能优化**：索引、分区、连接池、批量操作
5. ✅ **数据迁移**：Alembic 完整迁移策略和最佳实践
6. ✅ **数据一致性**：事务管理、乐观锁机制
7. ✅ **监控与维护**：慢查询监控、连接池监控、数据归档

**Repository 清单**：
- `ProjectRepository` - 项目管理
- `UserRepository` - 用户管理（update 方法返回 bool）
- `TaskRepository` - 任务管理（update_status 方法返回 bool）
- `AgentExecutionRepository` - Agent 执行记录（update_status 方法返回 bool）
- `CodeFileRepository` - 代码文件管理（update_content 方法返回 bool）
- `CodeVersionRepository` - 代码版本历史管理
- `QualityMetricRepository` - 质量指标跟踪

**下一步行动**：
- 使用 Alembic 创建初始迁移脚本
- 编写单元测试覆盖所有 Repository 方法（目标 80%+ 覆盖率）
- 配置生产环境的数据库连接池和监控
- 实施数据归档策略
```
