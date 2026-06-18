/**
 * StepPipeline Component (Sprint 3 - Phase 1 MVP)
 *
 * Visualizes the 5-step agent execution pipeline with status indicators.
 * Based on docs/design/progress-ui-prototype.md
 */

import type { StepState } from "@/hooks/useProgressTracking";
import { StatusBadge } from "./StatusBadge";

interface StepPipelineProps {
  steps: StepState[];
  currentStep: string | null;
  className?: string;
}

/**
 * Get step display name (localized)
 */
function getStepDisplayName(stepName: string): string {
  const nameMap: Record<string, string> = {
    researcher: "调研",
    planner: "规划",
    coder: "编码",
    reviewer: "审查",
    tester: "测试",
  };

  return nameMap[stepName.toLowerCase()] || stepName;
}

/**
 * Format duration in milliseconds to human-readable
 */
function formatDurationMs(durationMs: number | null): string {
  if (durationMs === null) {
    return "—";
  }

  const seconds = Math.floor(durationMs / 1000);

  if (seconds < 1) {
    return `${durationMs}ms`;
  }

  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return remainingSeconds > 0
    ? `${minutes}m ${remainingSeconds}s`
    : `${minutes}m`;
}

/**
 * Get step icon based on status
 */
function getStepIcon(status: StepState["status"]): string {
  switch (status) {
    case "completed":
      return "✓";
    case "running":
      return "●";
    case "failed":
      return "✗";
    case "pending":
      return "○";
    case "skipped":
      return "—";
    case "retrying":
      return "↻";
    case "cancelled":
      return "⊗";
    default:
      return "○";
  }
}

/**
 * Individual step card in the pipeline
 */
function StepCard({
  step,
  isCurrent,
}: {
  step: StepState;
  isCurrent: boolean;
}) {
  const displayName = getStepDisplayName(step.name);
  const icon = getStepIcon(step.status);
  const duration = formatDurationMs(step.durationMs);

  return (
    <div
      className={`flex-1 min-w-[120px] rounded-lg border p-3 transition-all ${
        isCurrent
          ? "border-blue-400 bg-blue-50 shadow-md"
          : "border-gray-200 bg-white hover:border-gray-300"
      }`}
      role="article"
      aria-label={`步骤: ${displayName}`}
      aria-current={isCurrent ? "step" : undefined}
    >
      {/* Step icon and name */}
      <div className="flex items-center gap-2 mb-2">
        <span
          className={`text-xl ${
            step.status === "completed"
              ? "text-green-600"
              : step.status === "running"
                ? "text-blue-600"
                : step.status === "failed"
                  ? "text-red-600"
                  : "text-gray-400"
          }`}
          aria-hidden="true"
        >
          {icon}
        </span>
        <span className="font-medium text-sm text-gray-900">{displayName}</span>
      </div>

      {/* Status badge */}
      <StatusBadge status={step.status} className="mb-2" />

      {/* Duration */}
      <div className="text-xs text-gray-500">
        {step.status === "completed"
          ? `耗时: ${duration}`
          : step.status === "running"
            ? "进行中"
            : "—"}
      </div>

      {/* Retry count badge (if > 0) */}
      {step.retryCount > 0 && (
        <div className="mt-2 text-xs text-orange-600 font-medium">
          重试 {step.retryCount} 次
        </div>
      )}

      {/* Error message (if failed) */}
      {step.status === "failed" && step.errorMessage && (
        <div
          className="mt-2 text-xs text-red-600 truncate"
          title={step.errorMessage}
        >
          {step.errorMessage}
        </div>
      )}
    </div>
  );
}

/**
 * Arrow connector between steps
 */
function StepConnector() {
  return (
    <div
      className="flex items-center justify-center px-2 text-gray-400"
      aria-hidden="true"
    >
      <span className="text-xl">→</span>
    </div>
  );
}

export function StepPipeline({
  steps,
  currentStep,
  className = "",
}: StepPipelineProps) {
  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-4 shadow-sm ${className}`}
      role="region"
      aria-label="执行步骤管道"
    >
      {/* Title */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">执行步骤</h3>

      {/* Pipeline container with horizontal scroll on mobile */}
      <div className="overflow-x-auto">
        <div className="flex items-stretch gap-2 min-w-max">
          {steps.map((step, index) => (
            <div key={step.name} className="flex items-stretch">
              <StepCard step={step} isCurrent={step.name === currentStep} />

              {/* Connector arrow (except after last step) */}
              {index < steps.length - 1 && <StepConnector />}
            </div>
          ))}
        </div>
      </div>

      {/* Empty state */}
      {steps.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          <p>暂无步骤数据</p>
        </div>
      )}
    </div>
  );
}
