# Jules 项目迭代计划 v1.1-v2.0

**制定日期**: 2026-06-17
**制定人**: tom (Developer)
**当前版本**: v1.0.0 (2026-06-17 发布)
**状态**: 待批准

---

## 执行摘要

基于 v1.0.0 已完成的核心功能（Phase 1-4：Docker 环境、后端 API、前端界面、Agent 系统、测试覆盖），本计划制定 **v1.1-v2.0 三个版本**的迭代路线图，聚焦：

1. **v1.1 (2026 Q3)**: 认证授权 + 实时通知 + Agent 进度追踪
2. **v1.2 (2026 Q4)**: Multi-Agent 协作流程 + 自定义 Prompt 模板
3. **v2.0 (2027 Q1)**: 多 LLM Provider + Fine-tuning + Agent 记忆

**核心目标**: 从 MVP（最小可行产品）演进到**企业级生产平台**。

---

## 当前状态总结 (v1.0.0)

### 已完成功能

**Phase 1: Docker Compose 环境** ✅

- PostgreSQL 16 + Redis 7 + FastAPI + Next.js 15
- 完整的开发环境配置

**Phase 2: 后端实现** ✅

- 9 个 SQLAlchemy 模型 + 7 个 Repository
- 39 个 RESTful API 端点
- Agent 系统（Scheduler, Executor, LLMClient, Analyzer）

**Phase 3: 前端实现** ✅

- 7 个管理页面（用户/任务/Agent/执行记录/代码文件/质量指标/健康检查）
- shadcn/ui 组件库 + Tailwind CSS

**Phase 4: 测试和质量保障** ✅

- 测试覆盖率：后端 85%+，前端 80%+，整体 82%
- CI/CD 配置：7 个 GitHub Actions 工作流
- Pre-commit hooks 配置完成

### 优化完成记录

**依赖优化** ✅ (任务 #aa2d179b)

- 前端：移除 10 个未使用依赖
- 后端：移除 5 个 LangChain 未使用包
- 减少依赖体积 ~248M (718M → ~470M)

**测试覆盖率提升** ✅ (任务 #963c7af1)

- 后端覆盖率：65% → 93-95%
- 前端覆盖率：提升至 85-90%
- Agent 系统覆盖率：87-100%

**CI/CD 恢复** ✅ (任务 #6c407a57)

- 7 个 GitHub Actions 工作流已恢复
- 文档完整（README + QUICK_REFERENCE + SUMMARY）

---

## v1.0.0 技术债务与已知问题

### 技术债务

1. **认证授权缺失** ❌
   - 当前所有 API 端点无权限控制
   - 无用户登录/注册功能
   - 无 JWT Token 机制

2. **实时通知缺失** ❌
   - Agent 执行状态变更无推送
   - 前端需要轮询 API
   - 无 WebSocket 连接

3. **Multi-Agent 协作未实现** ❌
   - 仅有单个 Agent 执行
   - 无 Researcher → Planner → Coder → Reviewer 流程
   - 无 Agent 间通信机制

4. **Prompt 模板硬编码** ❌
   - Prompt 写死在代码中
   - 无法动态调整
   - 无版本管理

5. **LLM Provider 单一** ❌
   - 仅支持 OpenAI + Anthropic (Mock 模式)
   - 无 Azure OpenAI, Google Gemini 等
   - 无智能降级机制

### 已知 Bug

1. Agent 并发限制为 5，高负载时排队
2. LLM API 超时 60 秒，复杂任务可能超时
3. 前端页面刷新丢失临时状态

---

## v1.1.0 迭代计划 (2026 Q3)

**发布目标**: 企业级认证授权 + 实时通知 + Agent 进度追踪
**预计开发时间**: 6-8 周
**优先级**: 高（生产环境必需）

### 1.1.1 用户认证授权系统

#### 功能需求

**用户注册/登录**:

- 邮箱 + 密码注册
- JWT Token 认证
- Token 刷新机制（Access Token 30min + Refresh Token 7天）
- 密码加密（bcrypt）
- 邮箱验证（可选）

**权限管理（RBAC）**:

- 角色定义：
  - `admin`: 全部权限
  - `developer`: 创建/执行 Agent，查看自己的任务
  - `viewer`: 仅查看权限
- 权限矩阵：
  - 用户管理：仅 admin
  - Agent 配置：admin + developer
  - 任务执行：admin + developer
  - 查看记录：全部角色

**API 端点设计**:

```
POST   /api/v1/auth/register       # 注册
POST   /api/v1/auth/login          # 登录
POST   /api/v1/auth/refresh        # Token 刷新
POST   /api/v1/auth/logout         # 登出
GET    /api/v1/auth/me             # 获取当前用户信息
PUT    /api/v1/auth/password       # 修改密码
```

#### 验收标准

- [ ] 用户可以注册新账号
- [ ] 用户可以使用邮箱/密码登录
- [ ] Token 过期后自动刷新
- [ ] 未授权 API 调用返回 401
- [ ] 不同角色权限正确限制
- [ ] 密码安全存储（不可逆加密）

---

### 1.1.2 实时通知系统 (WebSocket)

#### 功能需求

**实时推送场景**:

1. Agent 执行状态变更（running → completed/failed）
2. 新任务创建通知
3. 代码生成进度（流式输出）
4. 质量检查结果通知

#### 验收标准

- [ ] WebSocket 连接成功建立
- [ ] Agent 状态变更实时推送到前端
- [ ] 断线自动重连（3 次重试）
- [ ] 多用户隔离（用户 A 不收到用户 B 的通知）
- [ ] 性能测试：支持 100 并发连接

---

### 1.1.3 Agent 执行进度追踪

#### 功能需求

**进度指标**:

- 当前步骤: `Researcher → Planner → Coder → Reviewer → Tester`
- 完成百分比: `0-100%`
- 预计剩余时间: `ETA: 2m 30s`
- 实时日志流: 每个步骤的输出

#### 验收标准

- [ ] Agent 执行时实时显示当前步骤
- [ ] 进度百分比准确计算
- [ ] 日志实时流式输出
- [ ] 失败步骤高亮显示错误
- [ ] 历史执行记录可回溯进度

---

### v1.1.0 开发时间表

| 周次 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| Week 1-2 | 认证授权系统 | bob + alice | 待开始 |
| Week 3-4 | WebSocket 实时通知 | bob + alice | 待开始 |
| Week 5-6 | Agent 进度追踪 | tom + alice | 待开始 |
| Week 7-8 | 集成测试 + Bug 修复 | 全员 | 待开始 |

### v1.1.0 验收标准

**功能完整性**:

- [ ] 用户可以注册/登录
- [ ] API 端点有权限控制
- [ ] WebSocket 实时推送工作
- [ ] Agent 进度可视化

**质量标准**:

- [ ] 测试覆盖率 ≥ 80%
- [ ] 安全漏洞扫描通过（Bandit）
- [ ] 性能测试：WebSocket 支持 100 并发

---

## v1.2.0 迭代计划 (2026 Q4)

**发布目标**: Multi-Agent 协作流程 + 自定义 Prompt 模板
**预计开发时间**: 8-10 周
**优先级**: 中（差异化特性）

### 1.2.1 Multi-Agent 协作流程

#### 功能需求

**Agent 角色定义**:

```
Researcher → Planner → Coder → Reviewer → Tester
    ↓          ↓         ↓        ↓         ↓
  竞品调研   架构设计   代码实现  质量审查  测试验证
```

**LangGraph 状态机实现**:

- 显式状态管理（AgentState）
- 条件边路由（quality_passed → next_step）
- 循环支持（Reviewer → Coder 修复循环，最多 3 次）

#### 验收标准

- [ ] 5 个 Agent 角色完整实现
- [ ] Agent 间数据传递正确
- [ ] 失败重试机制工作
- [ ] React Flow 可视化工作流
- [ ] 执行历史可追溯

---

### 1.2.2 自定义 Prompt 模板管理

#### 功能需求

**模板管理功能**:

- CRUD 操作：创建/编辑/删除模板
- 变量插值：`{{task_description}}`, `{{code_context}}`
- 版本管理：v1, v2, v3
- 模板分类：Researcher, Planner, Coder, Reviewer, Tester

#### 验收标准

- [ ] 用户可以创建自定义模板
- [ ] 模板变量正确替换
- [ ] 版本回滚功能工作
- [ ] A/B 测试支持（可选）

---

### v1.2.0 开发时间表

| 周次 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| Week 1-4 | Multi-Agent 协作流程 | tom + bob | 待开始 |
| Week 5-6 | Prompt 模板管理 | bob | 待开始 |
| Week 7-8 | React Flow 可视化 | alice | 待开始 |
| Week 9-10 | 集成测试 + Bug 修复 | 全员 | 待开始 |

---

## v2.0.0 迭代计划 (2027 Q1)

**发布目标**: 多 LLM Provider + Fine-tuning + Agent 记忆
**预计开发时间**: 12 周
**优先级**: 低（增强特性）

### 2.0.1 多 LLM Provider 支持

#### 支持的 Provider

1. **OpenAI** (已支持)
   - GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo

2. **Anthropic** (已支持 Mock)
   - Claude Opus 4.8, Sonnet 4.6, Haiku 4.5

3. **新增 Provider**:
   - Azure OpenAI
   - Google Gemini (1.5 Pro, 1.5 Flash)
   - Cohere Command R+
   - 本地部署（Ollama）

#### 验收标准

- [ ] 4+ LLM Provider 可用
- [ ] 智能降级（主 Provider 失败 → 备用）
- [ ] 成本对比（实时显示各 Provider 价格）

---

### 2.0.2 Fine-tuning 自定义模型

#### 功能需求

- 收集高质量训练数据（用户标注的好/坏代码）
- 集成 OpenAI Fine-tuning API
- 模型版本管理
- A/B 测试（基础模型 vs Fine-tuned）

---

### 2.0.3 Agent 记忆系统

#### 功能需求

- 短期记忆：当前会话上下文
- 长期记忆：历史任务经验（向量数据库）
- 检索增强（RAG）：从历史中学习

---

## 附录

### 资源需求

**人力**:

- 后端开发: 2人
- 前端开发: 1人
- 测试/QA: 1人（兼职）

**硬件**:

- 开发服务器: 8核 16GB RAM
- PostgreSQL: 生产级配置
- Redis: 持久化配置

**预算**:

- LLM API 调用: $500/月（开发 + 测试）
- 云服务器: $200/月
- 监控工具: $100/月

---

**制定人**: tom (Developer)
**审批**: 待 team-lead 批准
**下次评审**: 每季度末
