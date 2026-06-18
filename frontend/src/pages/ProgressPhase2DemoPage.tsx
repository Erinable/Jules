/**
 * Progress Phase 2 Demo Page (Sprint 3)
 *
 * Demonstrates the 4 Phase 2 components with mock data.
 */

import { useState } from "react";
import {
  LogPanel,
  StepCard,
  DetailPanel,
  LogEntry,
} from "@/components/progress";
import type {
  StepState,
  LogEntry as LogEntryType,
} from "@/hooks/useProgressTracking";

// Mock step data
const mockSteps: StepState[] = [
  {
    name: "researcher",
    status: "completed",
    startedAt: "2026-06-17T10:00:00Z",
    completedAt: "2026-06-17T10:00:30Z",
    durationMs: 30000,
    retryCount: 0,
    errorMessage: null,
  },
  {
    name: "planner",
    status: "completed",
    startedAt: "2026-06-17T10:00:30Z",
    completedAt: "2026-06-17T10:01:15Z",
    durationMs: 45000,
    retryCount: 1,
    errorMessage: null,
  },
  {
    name: "coder",
    status: "failed",
    startedAt: "2026-06-17T10:01:15Z",
    completedAt: "2026-06-17T10:03:00Z",
    durationMs: 105000,
    retryCount: 2,
    errorMessage: "SyntaxError: Unexpected token in line 42",
  },
  {
    name: "reviewer",
    status: "running",
    startedAt: "2026-06-17T10:03:00Z",
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
];

// Mock log data
const mockLogs: LogEntryType[] = [
  {
    step: "researcher",
    level: "info",
    message: "开始分析项目需求...",
    sequenceNum: 1,
    timestamp: "2026-06-17T10:00:01Z",
  },
  {
    step: "researcher",
    level: "debug",
    message: "读取配置文件: config.json",
    sequenceNum: 2,
    timestamp: "2026-06-17T10:00:05Z",
  },
  {
    step: "researcher",
    level: "info",
    message: "需求分析完成，生成报告",
    sequenceNum: 3,
    timestamp: "2026-06-17T10:00:28Z",
  },
  {
    step: "planner",
    level: "info",
    message: "开始生成执行计划...",
    sequenceNum: 4,
    timestamp: "2026-06-17T10:00:31Z",
  },
  {
    step: "planner",
    level: "warning",
    message: "检测到潜在的性能瓶颈，建议优化",
    sequenceNum: 5,
    timestamp: "2026-06-17T10:00:45Z",
  },
  {
    step: "planner",
    level: "info",
    message: "执行计划生成完成",
    sequenceNum: 6,
    timestamp: "2026-06-17T10:01:13Z",
  },
  {
    step: "coder",
    level: "info",
    message: "开始编码实现...",
    sequenceNum: 7,
    timestamp: "2026-06-17T10:01:16Z",
  },
  {
    step: "coder",
    level: "debug",
    message: "创建文件: src/components/Button.tsx",
    sequenceNum: 8,
    timestamp: "2026-06-17T10:01:30Z",
  },
  {
    step: "coder",
    level: "error",
    message: "编译错误: SyntaxError: Unexpected token in line 42",
    sequenceNum: 9,
    timestamp: "2026-06-17T10:02:45Z",
  },
  {
    step: "coder",
    level: "info",
    message: "重试第 1 次...",
    sequenceNum: 10,
    timestamp: "2026-06-17T10:02:50Z",
  },
  {
    step: "reviewer",
    level: "info",
    message: "开始代码审查...",
    sequenceNum: 11,
    timestamp: "2026-06-17T10:03:01Z",
  },
  {
    step: "reviewer",
    level: "info",
    message: "检查代码风格规范...",
    sequenceNum: 12,
    timestamp: "2026-06-17T10:03:15Z",
  },
];

export default function ProgressPhase2DemoPage() {
  const mockRunId = "550e8400-e29b-41d4-a716-446655440000";
  const [selectedStep, setSelectedStep] = useState<StepState | null>(
    mockSteps[2],
  ); // Default to failed coder step
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());

  const toggleCard = (stepName: string) => {
    setExpandedCards((prev) => {
      const next = new Set(prev);
      if (next.has(stepName)) {
        next.delete(stepName);
      } else {
        next.add(stepName);
      }
      return next;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            进度追踪组件 Phase 2 示例
          </h1>
          <p className="mt-2 text-gray-600">
            Sprint 3 Phase 2 - 4 个高级组件演示（使用 Mock 数据）
          </p>
        </div>

        {/* Component 1: LogEntry standalone */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            1. LogEntry 组件（单条日志）
          </h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-2">
            {mockLogs.slice(0, 4).map((log) => (
              <LogEntry key={log.sequenceNum} log={log} />
            ))}
          </div>
        </section>

        {/* Component 2: StepCard showcase */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            2. StepCard 组件（步骤卡片）
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mockSteps.slice(0, 4).map((step) => (
              <StepCard
                key={step.name}
                step={step}
                isExpanded={expandedCards.has(step.name)}
                onToggle={() => toggleCard(step.name)}
              />
            ))}
          </div>
        </section>

        {/* Component 3: DetailPanel with mock step */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            3. DetailPanel 组件（详情面板）
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Step selector */}
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                选择步骤:
              </h3>
              {mockSteps.map((step) => (
                <button
                  key={step.name}
                  onClick={() => setSelectedStep(step)}
                  className={`w-full text-left px-3 py-2 rounded border text-sm transition-colors ${
                    selectedStep?.name === step.name
                      ? "bg-blue-50 border-blue-300 text-blue-700 font-medium"
                      : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {step.name} ({step.status})
                </button>
              ))}
            </div>

            {/* Detail panel */}
            <div className="lg:col-span-2">
              <DetailPanel step={selectedStep} />
            </div>
          </div>
        </section>

        {/* Component 4: LogPanel with filters */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            4. LogPanel 组件（日志面板）
          </h2>
          <LogPanel runId={mockRunId} />
          <p className="mt-2 text-sm text-gray-500">
            注意：此组件使用 useProgressTracking Hook 从 API 获取真实日志。 如果
            API 未运行，将显示加载或错误状态。
          </p>
        </section>

        {/* Component 5: Combined layout example */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            5. 组合示例（完整布局）
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <LogPanel runId={mockRunId} />
            <DetailPanel step={selectedStep} />
          </div>
        </section>

        {/* Features showcase */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            6. 功能亮点
          </h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <ul className="space-y-3 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>
                  <strong>LogPanel</strong>:
                  实时日志滚动、自动滚动切换、按级别/步骤过滤
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>
                  <strong>StepCard</strong>: 可展开/折叠、显示重试次数、错误消息
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>
                  <strong>DetailPanel</strong>: 完整时间信息、执行时长、状态描述
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>
                  <strong>LogEntry</strong>: 颜色编码（4
                  种级别）、时间戳、步骤标签
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">ℹ️</span>
                <span>所有组件支持响应式布局（移动/平板/桌面）</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">ℹ️</span>
                <span>完整可访问性支持（WCAG 2.1 AA 标准）</span>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
