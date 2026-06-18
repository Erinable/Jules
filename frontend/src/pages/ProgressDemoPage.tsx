/**
 * Progress Demo Page (Sprint 3 - Phase 1 MVP)
 *
 * Demonstrates the 4 basic progress components with mock data.
 * This file can be used for development and testing.
 */

import {
  ProgressOverview,
  StepPipeline,
  ProgressBar,
  StatusBadge,
} from "@/components/progress";
import type { StepState } from "@/hooks/useProgressTracking";

// Mock step data for demonstration
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
    retryCount: 0,
    errorMessage: null,
  },
  {
    name: "coder",
    status: "running",
    startedAt: "2026-06-17T10:01:15Z",
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
];

export default function ProgressDemoPage() {
  const mockRunId = "550e8400-e29b-41d4-a716-446655440000";

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">进度追踪组件示例</h1>
          <p className="mt-2 text-gray-600">
            Sprint 3 Phase 1 MVP - 4 个基础组件演示（使用 Mock 数据）
          </p>
        </div>

        {/* Component 1: ProgressBar standalone */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            1. ProgressBar 组件
          </h2>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="space-y-4">
              <ProgressBar percentage={65} eta={180} />
              <ProgressBar percentage={100} eta={null} />
              <ProgressBar percentage={25} eta={300} />
            </div>
          </div>
        </section>

        {/* Component 2: StatusBadge showcase */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            2. StatusBadge 组件
          </h2>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex flex-wrap gap-3">
              <StatusBadge status="pending" />
              <StatusBadge status="running" />
              <StatusBadge status="completed" />
              <StatusBadge status="failed" />
              <StatusBadge status="skipped" />
              <StatusBadge status="retrying" />
              <StatusBadge status="cancelled" />
            </div>
          </div>
        </section>

        {/* Component 3: ProgressOverview with mock runId */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            3. ProgressOverview 组件
          </h2>
          <ProgressOverview runId={mockRunId} />
          <p className="mt-2 text-sm text-gray-500">
            注意：此组件使用 useProgressTracking Hook 从 API 获取真实数据。 如果
            API 未运行，将显示加载或错误状态。
          </p>
        </section>

        {/* Component 4: StepPipeline with mock steps */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            4. StepPipeline 组件
          </h2>
          <StepPipeline steps={mockSteps} currentStep="coder" />
        </section>

        {/* Combined example */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            5. 组合示例（完整布局）
          </h2>
          <div className="space-y-4">
            <ProgressOverview runId={mockRunId} />
            <StepPipeline steps={mockSteps} currentStep="coder" />
          </div>
        </section>

        {/* Responsive test section */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            6. 响应式布局测试
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            调整浏览器窗口大小以查看响应式布局效果：
            <br />
            - 移动端 (&lt; 640px): 单列垂直堆叠，步骤管道可横向滚动
            <br />
            - 平板 (640-1024px): 卡片自适应
            <br />- 桌面 (&gt; 1024px): 完整布局
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ProgressOverview runId={mockRunId} />
            <StepPipeline steps={mockSteps} currentStep="coder" />
          </div>
        </section>
      </div>
    </div>
  );
}
