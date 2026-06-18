# Sprint 3 React 组件清单

本文件记录 Sprint 3 进度追踪 UI 组件的实现状态。

基于 docs/design/progress-ui-prototype.md

## 已完成（Phase 1 MVP）

### Hooks

- ✅ **useProgressTracking.ts** - 核心 Hook，管理进度状态和 WebSocket 更新

### Phase 1 MVP 组件（4 个基础组件）

- ✅ **ProgressBar.tsx** - 可重用进度条组件（百分比 + ETA）
- ✅ **StatusBadge.tsx** - 状态徽章组件（颜色编码）
- ✅ **ProgressOverview.tsx** - 总体进度概览卡片
- ✅ **StepPipeline.tsx** - 5 步骤可视化管道

### 示例页面

- ✅ **ProgressDemoPage.tsx** - 组件演示页面（带 Mock 数据）

## 待创建组件骨架（Phase 2 - 5 个高级组件）

### 1. LogPanel.tsx

**用途**: 总体进度概览（百分比 + ETA）
**Props**: `{ runId: string }`
**状态**: Mock 数据驱动
**主要功能**:

- 显示 overall_percentage（进度条）
- 显示 ETA（剩余时间）
- 显示当前步骤
- 使用 useProgressTracking Hook

### 2. StepPipeline.tsx

**用途**: 5 步骤可视化管道
**Props**: `{ steps: StepState[] }`
**状态**: Mock 数据驱动
**主要功能**:

- 水平展示 5 个步骤（Researcher → Planner → Coder → Reviewer → Tester）
- 每步显示状态图标（pending/running/completed/failed）
- 当前步骤高亮
- 点击展开详情

### 3. StepCard.tsx

**用途**: 单个步骤卡片
**Props**: `{ step: StepState }`
**状态**: 无状态组件
**主要功能**:

- 显示步骤名称、状态、时长
- 状态颜色编码（green/yellow/red/gray）
- retry_count 徽章

### 4. LogPanel.tsx

**用途**: 实时日志面板
**Props**: `{ runId: string }`
**状态**: Mock 数据驱动
**主要功能**:

- 显示滚动日志列表
- 按 level 颜色编码（debug/info/warning/error）
- 自动滚动到底部（新日志追加）
- 过滤器（按 level、按 step）

### 5. DetailPanel.tsx

**用途**: 步骤详细信息面板
**Props**: `{ step: StepState }`
**状态**: Mock 数据驱动
**主要功能**:

- 显示 started_at / completed_at
- 显示 duration_ms
- 显示 error_message（如果失败）
- 显示 metadata

### 6. ProgressBar.tsx

**用途**: 可重用进度条组件
**Props**: `{ percentage: number, eta: number | null }`
**状态**: 无状态组件
**主要功能**:

- 显示填充进度条（0-100%）
- 显示百分比文本
- 显示 ETA（如果有）

### 7. StatusBadge.tsx

**用途**: 状态徽章组件
**Props**: `{ status: StepStatus }`
**状态**: 无状态组件
**主要功能**:

- 根据状态显示颜色徽章
- pending: gray, running: yellow, completed: green, failed: red

### 8. LogEntry.tsx

**用途**: 单条日志条目组件
**Props**: `{ log: LogEntry }`
**状态**: 无状态组件
**主要功能**:

- 显示时间戳、level、step、message
- level 颜色编码

### 9. ProgressDashboard.tsx

**用途**: 主仪表盘，组合所有组件
**Props**: `{ runId: string }`
**状态**: Mock 数据驱动
**主要功能**:

- 布局：ProgressOverview（顶部）+ StepPipeline（中部）+ LogPanel（底部）
- 响应式布局（桌面 3 栏，移动 1 栏）

## Mock 数据示例

```typescript
// Mock progress state
const mockProgress: ProgressState = {
  runId: "run-550e8400",
  status: "running",
  steps: [
    {
      name: "researcher",
      status: "completed",
      startedAt: "2026-06-17T10:00:00Z",
      completedAt: "2026-06-17T10:00:15Z",
      durationMs: 15000,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "planner",
      status: "running",
      startedAt: "2026-06-17T10:00:15Z",
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "coder",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "reviewer",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "tester",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
  ],
  currentStep: "planner",
  overallPercentage: 22.5,
  etaSeconds: 120,
  startedAt: "2026-06-17T10:00:00Z",
  updatedAt: "2026-06-17T10:00:20Z",
  completedAt: null,
};

// Mock logs
const mockLogs: LogEntry[] = [
  {
    step: "researcher",
    level: "info",
    message: "Starting research phase",
    sequenceNum: 1,
    timestamp: "2026-06-17T10:00:00Z",
  },
  {
    step: "researcher",
    level: "info",
    message: "Research completed",
    sequenceNum: 2,
    timestamp: "2026-06-17T10:00:15Z",
  },
  {
    step: "planner",
    level: "info",
    message: "Generating plan...",
    sequenceNum: 3,
    timestamp: "2026-06-17T10:00:15Z",
  },
];
```

## 实施优先级

1. **Phase 1**（MVP）：
   - ProgressBar（基础组件）
   - StatusBadge（基础组件）
   - ProgressOverview（核心功能）
   - StepPipeline（核心功能）

2. **Phase 2**（完整功能）：
   - LogPanel（实时日志）
   - StepCard（详细步骤）
   - DetailPanel（步骤详情）
   - LogEntry（日志条目）

3. **Phase 3**（集成）：
   - ProgressDashboard（主仪表盘）
   - WebSocket 集成测试
   - 响应式布局调整

## 下一步

完成 Sprint 3 准备工作后：

1. 实施 ProgressRepository（数据层）
2. 实施 REST API 端点（10 个）
3. WebSocket 集成（5 种 progress.\* 消息）
4. 创建实际组件（替换 Mock 数据）
5. E2E 测试
