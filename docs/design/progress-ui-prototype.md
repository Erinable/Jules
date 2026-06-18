# 进度追踪 UI 原型设计

**版本**: v1.0 (设计稿)
**作者**: tom
**日期**: 2026-06-17
**关联任务**: #56c7bb89 (Sprint 3)
**依赖**: Sprint 2 (WebSocket) - 实时数据需要

---

## 1. 概述

定义进度追踪系统的前端组件结构、状态流、交互设计。本文档仅设计原型和接口契约，不含完整实现代码。

### 设计目标

- **实时性**: WebSocket 推送即时更新，无延迟
- **可读性**: 复杂执行过程一目了然
- **可交互**: 用户可暂停/取消/查看详情
- **可访问性**: WCAG 2.1 AA 标准

---

## 2. 页面布局

### 2.1 进度追踪页面整体结构

```
┌─────────────────────────────────────────────────────────────────┐
│  [Header] Jules > Agent 执行 > 运行 #550e8400                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  [进度概览卡片 ProgressOverview]                         │    │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░  65%  ETA: 1m 45s             │    │
│  │  状态: 运行中    步骤: 3/5    总耗时: 3m 30s            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  [步骤流水线 StepPipeline]                               │    │
│  │  ✓ Researcher → ✓ Planner → ● Coder → ○ Reviewer → ○ T │    │
│  │  0.5s done     0.45s done   running    pending    pend │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────────────┬─────────────────────────┐    │
│  │  [日志面板 LogPanel]           │  [详情面板 DetailPanel]  │    │
│  │  ▼ Researcher (12 logs)      │  当前步骤: Coder         │    │
│  │  ▼ Planner (8 logs)           │  开始: 10:26:15         │    │
│  │  ▶ Coder (5 logs)             │  Token: 1,250/2,000    │    │
│  │  ▶ Reviewer                   │  ─────────────────     │    │
│  │  ▶ Tester                     │  [暂停] [取消]           │    │
│  └──────────────────────────────┴─────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 响应式断点

| 断点 | 宽度 | 布局 |
|------|------|------|
| Mobile | < 640px | 单列垂直堆叠 |
| Tablet | 640-1024px | 步骤水平滚动，日志+详情垂直 |
| Desktop | > 1024px | 完整双列布局 |

---

## 3. 核心组件设计

### 3.1 ProgressOverview（进度概览卡片）

**职责**: 显示整体执行进度、ETA、关键状态

```typescript
interface ProgressOverviewProps {
  progress: RunProgress;
  onRefresh?: () => void;
}

// 状态展示规则
function getStatusBadge(status: RunStatus): { label, color, icon } {
  switch (status) {
    case "running": return { label: "运行中", color: "blue", icon: Spinner };
    case "completed": return { label: "已完成", color: "green", icon: Check };
    case "failed": return { label: "失败", color: "red", icon: X };
    case "paused": return { label: "已暂停", color: "yellow", icon: Pause };
    case "cancelled": return { label: "已取消", color: "gray", icon: Ban };
  }
}
```

**UI 示例**:
```
┌─────────────────────────────────────────────┐
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  65%                │
│                                             │
│  🟢 运行中    步骤 3/5    总耗时 3m 30s      │
│  预计剩余: 1m 45s                          │
└─────────────────────────────────────────────┘
```

**交互**:
- 点击百分比数字切换显示模式（百分比/剩余时间/总耗时）
- 进度条支持悬停查看各步骤占比

---

### 3.2 StepPipeline（步骤流水线）

**职责**: 可视化 5 步骤执行流水线

```typescript
interface StepPipelineProps {
  steps: StepState[];
  currentStep: AgentStep | null;
  onSelectStep?: (step: AgentStep) => void;
  selectedStep?: AgentStep;
}
```

**UI 示例**:
```
┌──────────────────────────────────────────────────────────┐
│  ✓ ──── ✓ ──── ● ──── ○ ──── ○                          │
│  Researcher  Planner  Coder  Reviewer  Tester             │
│  0.5s done  45s done  running  pending    pending        │
│  12 logs    8 logs   5 logs   ─          ─               │
└──────────────────────────────────────────────────────────┘
```

**步骤状态样式**:
| 状态 | 图标 | 颜色 | 动画 |
|------|------|------|------|
| completed | ✓ | 绿色 | 无 |
| running | ● | 蓝色 | 脉冲 (pulse) |
| pending | ○ | 灰色 | 无 |
| failed | ✗ | 红色 | 抖动 (shake) |
| skipped | ⊘ | 黄色 | 无 |
| retrying | ↻ | 橙色 | 旋转 (spin) |
| cancelled | ⊘ | 灰色 | 无 |

**交互**:
- 点击任意步骤切换详情面板显示该步骤的日志
- 失败步骤悬停显示错误消息 tooltip
- 重试次数 > 0 时显示徽章 `↻2`

---

### 3.3 LogPanel（日志面板）

**职责**: 显示执行日志，支持级别过滤和搜索

```typescript
interface LogPanelProps {
  progressId: string;
  steps: StepState[];
  filter: {
    step?: AgentStep;
    level?: LogLevel;
    search?: string;
  };
  autoScroll: boolean;
  onFilterChange: (filter: LogFilter) => void;
}
```

**UI 示例**:
```
┌──────────────────────────────────────────┐
│  日志 [搜索🔍] [级别▼] [自动滚动 ✓]      │
├──────────────────────────────────────────┤
│  ▼ Researcher (12) 0.5s                 │
│    [10:25:00.123] ℹ 开始分析需求...     │
│    [10:25:00.500] ℹ 读取代码上下文      │
│    ...                                  │
│  ▼ Planner (8) 0.45s                   │
│    [10:25:30.100] ℹ 生成方案 v1         │
│    [10:25:32.200] ⚠ 发现循环依赖        │
│    [10:25:33.400] ℹ 重新规划           │
│  ▶ Coder (5, live)                      │
│    [10:26:15.000] ℹ 开始生成代码        │
│    [10:26:18.500] ℹ 生成 main.py       │
│    [10:26:22.100] ▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮ │ <- 实时光标
└──────────────────────────────────────────┘
```

**特性**:
- 按步骤分组（折叠面板）
- 当前运行步骤自动展开
- 日志级别颜色编码（info 蓝、warn 黄、error 红、debug 灰）
- 支持日志搜索（高亮匹配）
- 自动滚动到底部（可暂停）
- 复制单条日志到剪贴板
- 下载完整日志（.txt / .json）

**性能优化**:
- 虚拟滚动（react-virtual）支持 10k+ 日志
- 日志批量更新（每 100ms 合并一次渲染）
- 离屏日志暂停渲染

---

### 3.4 DetailPanel（详情面板）

**职责**: 显示当前步骤详情、控制按钮

```typescript
interface DetailPanelProps {
  progress: RunProgress;
  selectedStep: AgentStep;
  canControl: boolean;  // 权限检查结果
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: (reason: string) => void;
}
```

**UI 示例**:
```
┌────────────────────────────────┐
│  Coder 步骤                    │
├────────────────────────────────┤
│  状态: 运行中 🟢              │
│  开始: 10:26:15               │
│  已运行: 2m 15s               │
│  Token: 1,250 / 2,000         │
│  重试: 0 / 3                  │
├────────────────────────────────┤
│  [⏸ 暂停]  [✗ 取消]           │
├────────────────────────────────┤
│  元数据:                       │
│  - 模型: gpt-4o                │
│  - 温度: 0.2                   │
│  - 上下文窗口: 8000/128000    │
└────────────────────────────────┘
```

**控制按钮规则**:
| 状态 | 显示按钮 |
|------|---------|
| running | [暂停] [取消] |
| paused | [恢复] [取消] |
| completed | [查看代码] |
| failed | [查看错误] [重试]（admin） |
| cancelled | （无） |

---

## 4. 状态管理

### 4.1 React Hook 设计

```typescript
// src/hooks/useProgressTracking.ts
interface UseProgressTrackingOptions {
  runId: string;
  autoConnect?: boolean;  // 默认 true
}

interface UseProgressTrackingResult {
  progress: RunProgress | null;
  logs: LogEntry[];
  transitions: StateTransition[];
  isConnected: boolean;
  error: Error | null;
  actions: {
    refresh: () => Promise<void>;
    pause: () => Promise<void>;
    resume: () => Promise<void>;
    cancel: (reason: string) => Promise<void>;
    setLogFilter: (filter: LogFilter) => void;
  };
}

function useProgressTracking({
  runId,
  autoConnect = true,
}: UseProgressTrackingOptions): UseProgressTrackingResult {
  // 1. 初始加载 REST 数据
  // 2. 建立 WebSocket 连接（Sprint 2）
  // 3. 处理实时事件，不可变更新状态
  // 4. 自动重连（3 次指数退避）
  // 5. 暴露 actions 给 UI
}
```

### 4.2 状态更新策略

**使用 useReducer + 不可变更新**:

```typescript
type ProgressEvent =
  | { type: "progress.updated"; data: RunProgress }
  | { type: "progress.step.started"; step: AgentStep; timestamp: string }
  | { type: "progress.step.completed"; step: AgentStep; durationMs: number }
  | { type: "progress.step.failed"; step: AgentStep; error: string }
  | { type: "progress.log.appended"; log: LogEntry }
  | { type: "progress.run.completed"; finalPercentage: number };

function progressReducer(state: ProgressState, event: ProgressEvent): ProgressState {
  switch (event.type) {
    case "progress.updated":
      // 不可变更新：返回新对象
      return { ...state, progress: event.data };
    case "progress.log.appended":
      return {
        ...state,
        logs: [...state.logs, event.log],  // 追加新日志，保留旧数组
      };
    // ...
  }
}
```

---

## 5. WebSocket 事件订阅

### 5.1 事件订阅协议

```typescript
// 客户端 → 服务端（订阅特定 run 的事件）
{
  "action": "subscribe",
  "channel": "progress",
  "run_id": "550e8400-..."
}

// 服务端 → 客户端（推送事件）
{
  "type": "progress.step.completed",
  "data": {
    "run_id": "...",
    "step": "researcher",
    "duration_ms": 30000
  },
  "timestamp": "2026-06-17T10:25:30Z"
}
```

### 5.2 重连策略

```typescript
const RECONNECT_CONFIG = {
  maxRetries: 3,
  baseDelay: 1000,     // 1s
  maxDelay: 30000,     // 30s
  backoffFactor: 2,
};

function calculateDelay(attempt: number): number {
  const delay = RECONNECT_CONFIG.baseDelay * Math.pow(RECONNECT_CONFIG.backoffFactor, attempt);
  return Math.min(delay, RECONNECT_CONFIG.maxDelay);
}
```

**重连后处理**:
1. 重新订阅之前的 channel
2. 请求离线期间错过的事件（基于 lastEventId）
3. 合并到本地状态

---

## 6. 路由设计

```typescript
// src/app/progress/[runId]/page.tsx
export default function ProgressPage({ params }: { params: { runId: string } }) {
  const { progress, isConnected, actions } = useProgressTracking({ runId: params.runId });

  return (
    <div className="container mx-auto py-6 space-y-6">
      <ProgressHeader runId={params.runId} />
      <ProgressOverview progress={progress} />
      <StepPipeline steps={progress?.steps} currentStep={progress?.currentStep} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LogPanel progressId={params.runId} steps={progress?.steps ?? []} />
        <DetailPanel progress={progress} {...actions} />
      </div>
    </div>
  );
}

// 列表页: /progress
// 详情页: /progress/[runId]
```

---

## 7. 可访问性 (A11y)

- **ARIA 标签**: 所有交互元素有 `aria-label`
- **键盘导航**: Tab 键切换步骤，Enter/Space 触发
- **屏幕阅读器**: 进度更新通过 `aria-live="polite"` 播报
- **颜色对比**: WCAG AA 标准（4.5:1）
- **动画控制**: 尊重 `prefers-reduced-motion`

```tsx
<div
  role="progressbar"
  aria-valuenow={progress.overall_percentage}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label="Agent 执行进度"
>
  <div style={{ width: `${progress.overall_percentage}%` }} />
</div>

// 屏幕阅读器实时播报
<div aria-live="polite" className="sr-only">
  {lastEventDescription}
</div>
```

---

## 8. 性能预算

| 指标 | 目标 |
|------|------|
| 首屏渲染 | < 500ms |
| WebSocket 事件 → UI 更新 | < 100ms |
| 10k 日志渲染 | 60fps |
| 内存占用（10k 日志） | < 50MB |

---

## 9. 组件清单（待实施）

| 组件 | 文件 | 复杂度 |
|------|------|--------|
| ProgressOverview | `components/progress/ProgressOverview.tsx` | 中 |
| StepPipeline | `components/progress/StepPipeline.tsx` | 高 |
| StepNode | `components/progress/StepNode.tsx` | 低 |
| LogPanel | `components/progress/LogPanel.tsx` | 高 |
| LogEntry | `components/progress/LogEntry.tsx` | 低 |
| DetailPanel | `components/progress/DetailPanel.tsx` | 中 |
| ProgressControls | `components/progress/ProgressControls.tsx` | 低 |
| useProgressTracking | `hooks/useProgressTracking.ts` | 高 |
| useWebSocket (Sprint 2) | `hooks/useWebSocket.ts` | 高 |

---

## 10. 测试策略

### 10.1 单元测试
- 每个 UI 组件渲染测试
- 进度计算函数（与后端共享纯函数）
- reducer 状态更新

### 10.2 集成测试
- WebSocket 事件 → UI 更新流程
- 暂停/取消操作 API 调用

### 10.3 E2E 测试
- 完整 Agent 执行流程
- 断线重连场景
- 大量日志场景

---

## 11. 待决问题

| # | 问题 | 默认建议 |
|---|------|---------|
| 1 | 是否支持多语言（i18n）？ | v1.1 中文为主，v1.2 加英文 |
| 2 | 是否导出执行报告（PDF）？ | v1.2 实现 |
| 3 | 主题切换（暗黑模式）？ | v1.1 默认浅色，v1.2 暗色 |
| 4 | 步骤图标自定义？ | 配置文件，v1.2 支持 |

---

**变更记录**:
- 2026-06-17: v1.0 初版设计（tom）
