# Jules 数据库文档

完整的数据库设计文档，包含 ER 图、表结构、索引和迁移历史。

## 目录

- [数据库概览](#数据库概览)
- [ER 图](#er-图)
- [表结构](#表结构)
- [索引设计](#索引设计)
- [性能优化](#性能优化)
- [迁移历史](#迁移历史)

---

## 数据库概览

**数据库系统**: PostgreSQL 16

**连接信息**:
```bash
Host: localhost
Port: 5432
Database: jules
User: postgres
Password: postgres
```

**环境变量**:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/jules
```

**表数量**: 9 张核心表

**关系类型**:
- 一对多关系：7 个
- 自引用关系：0 个
- 多对多关系：0 个

---

## ER 图

### 实体关系图（Entity-Relationship Diagram）

```mermaid
erDiagram
    User ||--o{ Task : "创建/分配"
    User ||--o{ Agent : "配置"
    Task ||--o{ AgentExecution : "执行"
    Agent ||--o{ AgentExecution : "执行者"
    AgentExecution ||--o{ LLMCall : "调用"
    AgentExecution ||--o{ CodeFile : "生成"
    CodeFile ||--o{ CodeVersion : "版本历史"
    CodeFile ||--o{ QualityMetric : "质量评估"
    
    User {
        int id PK
        string email UK
        string username
        timestamp created_at
        timestamp updated_at
    }
    
    Task {
        int id PK
        string title
        text description
        string status
        int priority
        int assigned_to FK
        timestamp created_at
        timestamp updated_at
        timestamp started_at
        timestamp completed_at
    }
    
    Agent {
        int id PK
        string name
        string type
        json config
        boolean is_active
        int created_by FK
        timestamp created_at
        timestamp updated_at
    }
    
    AgentExecution {
        int id PK
        int agent_id FK
        int task_id FK
        string status
        json input_data
        json output_data
        text error_message
        timestamp started_at
        timestamp completed_at
        float execution_time_seconds
    }
    
    LLMCall {
        int id PK
        int execution_id FK
        string model
        text prompt
        text response
        int prompt_tokens
        int completion_tokens
        int total_tokens
        float cost
        timestamp created_at
    }
    
    CodeFile {
        int id PK
        int project_id FK
        string file_path
        text content
        string file_hash
        string language
        int execution_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    CodeVersion {
        int id PK
        int code_file_id FK
        int version_number
        text content
        string file_hash
        int created_by FK
        timestamp created_at
    }
    
    QualityMetric {
        int id PK
        int project_id FK
        int code_file_id FK
        float avg_complexity
        float maintainability_index
        float test_coverage
        int security_issues
        int code_smells
        timestamp measured_at
    }
    
    HealthCheck {
        int id PK
        string service_name
        string status
        json details
        timestamp checked_at
    }
```

---

## 表结构

### 1. users（用户表）

**用途**: 存储系统用户信息

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 用户ID |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱地址 |
| `username` | VARCHAR(100) | NOT NULL | 用户名 |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**示例数据**:
```sql
INSERT INTO users (email, username) VALUES
('admin@jules.dev', 'admin'),
('developer@jules.dev', 'developer');
```

---

### 2. tasks（任务表）

**用途**: 存储代码生成任务

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 任务ID |
| `title` | VARCHAR(200) | NOT NULL | 任务标题 |
| `description` | TEXT | NULL | 任务描述 |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 任务状态 |
| `priority` | INTEGER | NOT NULL, CHECK (0-10) | 优先级（0-10） |
| `assigned_to` | INTEGER | FK → users(id) | 分配给的用户 |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| `started_at` | TIMESTAMP | NULL | 开始时间 |
| `completed_at` | TIMESTAMP | NULL | 完成时间 |

**状态枚举**:
- `pending`: 待处理
- `in_progress`: 进行中
- `completed`: 已完成
- `failed`: 失败

**索引**:
```sql
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**约束**:
```sql
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_assigned_to 
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE tasks ADD CONSTRAINT chk_tasks_priority 
    CHECK (priority >= 0 AND priority <= 10);
```

---

### 3. agents（Agent 配置表）

**用途**: 存储 Agent 配置信息

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Agent ID |
| `name` | VARCHAR(100) | NOT NULL | Agent 名称 |
| `type` | VARCHAR(50) | NOT NULL | Agent 类型 |
| `config` | JSONB | NOT NULL | Agent 配置（JSON） |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否激活 |
| `created_by` | INTEGER | FK → users(id) | 创建者 |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**类型枚举**:
- `code_generator`: 代码生成器
- `code_reviewer`: 代码审查器
- `code_analyzer`: 代码分析器
- `tester`: 测试生成器

**索引**:
```sql
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_is_active ON agents(is_active);
CREATE INDEX idx_agents_created_by ON agents(created_by);
```

**JSON 配置示例**:
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0.7,
  "max_tokens": 4096,
  "system_prompt": "You are a senior Python developer...",
  "tools": ["ruff", "mypy", "bandit"]
}
```

---

### 4. agent_executions（执行记录表）

**用途**: 记录 Agent 执行历史

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 执行ID |
| `agent_id` | INTEGER | FK → agents(id), NOT NULL | Agent ID |
| `task_id` | INTEGER | FK → tasks(id), NOT NULL | 任务ID |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 执行状态 |
| `input_data` | JSONB | NULL | 输入数据 |
| `output_data` | JSONB | NULL | 输出数据 |
| `error_message` | TEXT | NULL | 错误信息 |
| `started_at` | TIMESTAMP | NULL | 开始时间 |
| `completed_at` | TIMESTAMP | NULL | 完成时间 |
| `execution_time_seconds` | FLOAT | NULL | 执行时长（秒） |

**状态枚举**:
- `pending`: 待执行
- `running`: 执行中
- `completed`: 已完成
- `failed`: 失败

**索引**:
```sql
CREATE INDEX idx_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX idx_executions_task_id ON agent_executions(task_id);
CREATE INDEX idx_executions_status ON agent_executions(status);
CREATE INDEX idx_executions_started_at ON agent_executions(started_at DESC);
```

**约束**:
```sql
ALTER TABLE agent_executions ADD CONSTRAINT fk_executions_agent_id
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE;

ALTER TABLE agent_executions ADD CONSTRAINT fk_executions_task_id
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;
```

---

### 5. llm_calls（LLM 调用记录表）

**用途**: 记录 LLM API 调用详情和成本

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 调用ID |
| `execution_id` | INTEGER | FK → agent_executions(id) | 执行ID |
| `model` | VARCHAR(100) | NOT NULL | 模型名称 |
| `prompt` | TEXT | NOT NULL | Prompt 内容 |
| `response` | TEXT | NULL | 响应内容 |
| `prompt_tokens` | INTEGER | NULL | Prompt Token 数 |
| `completion_tokens` | INTEGER | NULL | 完成 Token 数 |
| `total_tokens` | INTEGER | NULL | 总 Token 数 |
| `cost` | DECIMAL(10, 6) | NULL | 成本（美元） |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 调用时间 |

**索引**:
```sql
CREATE INDEX idx_llm_calls_execution_id ON llm_calls(execution_id);
CREATE INDEX idx_llm_calls_model ON llm_calls(model);
CREATE INDEX idx_llm_calls_created_at ON llm_calls(created_at DESC);
```

**约束**:
```sql
ALTER TABLE llm_calls ADD CONSTRAINT fk_llm_calls_execution_id
    FOREIGN KEY (execution_id) REFERENCES agent_executions(id) ON DELETE CASCADE;
```

---

### 6. code_files（代码文件表）

**用途**: 存储生成的代码文件

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 文件ID |
| `project_id` | INTEGER | NOT NULL | 项目ID |
| `file_path` | VARCHAR(500) | NOT NULL | 文件路径 |
| `content` | TEXT | NOT NULL | 文件内容 |
| `file_hash` | VARCHAR(64) | NOT NULL | 文件哈希（SHA-256） |
| `language` | VARCHAR(50) | NOT NULL | 编程语言 |
| `execution_id` | INTEGER | FK → agent_executions(id) | 执行ID |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_code_files_project_id ON code_files(project_id);
CREATE INDEX idx_code_files_file_path ON code_files(file_path);
CREATE INDEX idx_code_files_language ON code_files(language);
CREATE INDEX idx_code_files_execution_id ON code_files(execution_id);
CREATE UNIQUE INDEX idx_code_files_project_path ON code_files(project_id, file_path);
```

---

### 7. code_versions（代码版本表）

**用途**: 存储代码文件的版本历史

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 版本ID |
| `code_file_id` | INTEGER | FK → code_files(id), NOT NULL | 文件ID |
| `version_number` | INTEGER | NOT NULL | 版本号 |
| `content` | TEXT | NOT NULL | 文件内容 |
| `file_hash` | VARCHAR(64) | NOT NULL | 文件哈希 |
| `created_by` | INTEGER | FK → users(id) | 创建者 |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
```sql
CREATE INDEX idx_versions_code_file_id ON code_versions(code_file_id);
CREATE INDEX idx_versions_created_at ON code_versions(created_at DESC);
CREATE UNIQUE INDEX idx_versions_file_version ON code_versions(code_file_id, version_number);
```

**约束**:
```sql
ALTER TABLE code_versions ADD CONSTRAINT fk_versions_code_file_id
    FOREIGN KEY (code_file_id) REFERENCES code_files(id) ON DELETE CASCADE;
```

---

### 8. quality_metrics（质量指标表）

**用途**: 存储代码质量指标

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 指标ID |
| `project_id` | INTEGER | NOT NULL | 项目ID |
| `code_file_id` | INTEGER | FK → code_files(id) | 文件ID（可选） |
| `avg_complexity` | FLOAT | NULL | 平均圈复杂度 |
| `maintainability_index` | FLOAT | NULL | 可维护性指数 |
| `test_coverage` | FLOAT | NULL | 测试覆盖率（%） |
| `security_issues` | INTEGER | NULL | 安全问题数量 |
| `code_smells` | INTEGER | NULL | 代码异味数量 |
| `measured_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 测量时间 |

**索引**:
```sql
CREATE INDEX idx_quality_project_id ON quality_metrics(project_id);
CREATE INDEX idx_quality_code_file_id ON quality_metrics(code_file_id);
CREATE INDEX idx_quality_measured_at ON quality_metrics(measured_at DESC);
```

**质量标准**:
- 圈复杂度：< 10（理想）
- 可维护性指数：> 20（可接受）
- 测试覆盖率：> 80%（目标）
- 安全问题：0（必须）

---

### 9. health_checks（健康检查表）

**用途**: 记录系统健康检查结果

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INTEGER | PK, AUTO_INCREMENT | 检查ID |
| `service_name` | VARCHAR(100) | NOT NULL | 服务名称 |
| `status` | VARCHAR(20) | NOT NULL | 状态 |
| `details` | JSONB | NULL | 详细信息 |
| `checked_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | 检查时间 |

**状态枚举**:
- `healthy`: 健康
- `degraded`: 降级
- `unhealthy`: 不健康

**索引**:
```sql
CREATE INDEX idx_health_service_name ON health_checks(service_name);
CREATE INDEX idx_health_checked_at ON health_checks(checked_at DESC);
```

---

## 索引设计

### 索引类型

| 索引类型 | 用途 | 示例 |
|----------|------|------|
| B-Tree (默认) | 等值查询、范围查询 | `CREATE INDEX idx_users_email ON users(email)` |
| UNIQUE | 唯一性约束 | `CREATE UNIQUE INDEX idx_users_email ON users(email)` |
| 复合索引 | 多列查询 | `CREATE INDEX idx_tasks_status_priority ON tasks(status, priority)` |
| 部分索引 | 条件过滤 | `CREATE INDEX idx_active_agents ON agents(id) WHERE is_active = true` |
| JSONB 索引 | JSON 查询 | `CREATE INDEX idx_agent_config ON agents USING GIN (config)` |

### 推荐索引

```sql
-- 高频查询索引
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC);
CREATE INDEX idx_executions_task_status ON agent_executions(task_id, status);

-- 部分索引（仅索引活跃记录）
CREATE INDEX idx_active_tasks ON tasks(id) WHERE status IN ('pending', 'in_progress');
CREATE INDEX idx_running_executions ON agent_executions(id) WHERE status = 'running';

-- JSONB 索引
CREATE INDEX idx_agent_config_gin ON agents USING GIN (config);
CREATE INDEX idx_execution_output_gin ON agent_executions USING GIN (output_data);
```

---

## 性能优化

### 1. 查询优化

**使用 EXPLAIN ANALYZE**:

```sql
EXPLAIN ANALYZE
SELECT t.*, u.username
FROM tasks t
JOIN users u ON t.assigned_to = u.id
WHERE t.status = 'pending'
ORDER BY t.priority DESC
LIMIT 10;
```

**慢查询日志**:

```sql
-- 开启慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1秒
SELECT pg_reload_conf();

-- 查看慢查询
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

---

### 2. 连接池配置

```python
# SQLAlchemy 连接池
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # 连接池大小
    max_overflow=10,     # 最大溢出连接
    pool_timeout=30,     # 超时时间
    pool_recycle=3600,   # 连接回收时间
)
```

---

### 3. 批量操作

```python
# 批量插入
async with db.begin():
    db.add_all([
        CodeFile(file_path="file1.py", content="..."),
        CodeFile(file_path="file2.py", content="..."),
    ])
```

---

### 4. 分区表（未来）

```sql
-- 按日期分区（大表优化）
CREATE TABLE agent_executions_2026_06 PARTITION OF agent_executions
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

---

## 迁移历史

### Alembic 迁移版本

| 版本号 | 日期 | 说明 |
|--------|------|------|
| `001` | 2026-06-16 | 初始化数据库，创建 users 和 tasks 表 |
| `002` | 2026-06-16 | 添加 agents 和 agent_executions 表 |
| `003` | 2026-06-16 | 添加 code_files 和 code_versions 表 |
| `004` | 2026-06-16 | 添加 quality_metrics 表 |
| `005` | 2026-06-16 | 添加 llm_calls 表 |
| `006` | 2026-06-16 | 添加 health_checks 表 |
| `007` | 2026-06-17 | 添加索引优化 |

### 查看迁移历史

```bash
# 查看当前版本
poetry run alembic current

# 查看所有历史
poetry run alembic history

# 升级到最新版本
poetry run alembic upgrade head

# 回滚到指定版本
poetry run alembic downgrade <revision_id>
```

### 创建新迁移

```bash
# 自动生成迁移（基于模型变更）
poetry run alembic revision --autogenerate -m "Add new column to users table"

# 手动创建迁移
poetry run alembic revision -m "Custom migration"
```

---

## 备份和恢复

### 备份数据库

```bash
# 完整备份
pg_dump -h localhost -U postgres -d jules > jules_backup.sql

# 仅备份数据（不包含表结构）
pg_dump -h localhost -U postgres -d jules --data-only > jules_data.sql

# 压缩备份
pg_dump -h localhost -U postgres -d jules | gzip > jules_backup.sql.gz
```

### 恢复数据库

```bash
# 恢复完整备份
psql -h localhost -U postgres -d jules < jules_backup.sql

# 恢复压缩备份
gunzip -c jules_backup.sql.gz | psql -h localhost -U postgres -d jules
```

---

## 监控和维护

### 1. 表大小统计

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. 索引使用统计

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 3. 表膨胀检查

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. VACUUM 和 ANALYZE

```sql
-- 清理和分析所有表
VACUUM ANALYZE;

-- 清理特定表
VACUUM ANALYZE tasks;

-- 完整 VACUUM（锁表）
VACUUM FULL tasks;
```

---

## 安全配置

### 1. 用户权限

```sql
-- 创建只读用户
CREATE USER readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE jules TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- 创建应用用户
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT CONNECT ON DATABASE jules TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 2. SSL 连接

```bash
# 启用 SSL 连接
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/jules?ssl=require
```

---

## 许可证

MIT License - 详见根目录 [LICENSE](../LICENSE) 文件

---

**最后更新**: 2026-06-17
