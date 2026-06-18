/**
 * DetailPanel Component (Sprint 3 - Phase 2)
 *
 * Displays detailed information for a specific execution step.
 * Based on docs/design/progress-ui-prototype.md
 */

import type { StepState } from "@/hooks/useProgressTracking";
import { StatusBadge } from "./StatusBadge";

interface DetailPanelProps {
  step: StepState | null;
  className?: string;
}

/**
 * Get step display name (localized)
 */
function getStepDisplayName(stepName: string): string {
  const nameMap: Record<string, string> = {
    researcher: "调研阶段",
    planner: "规划阶段",
    coder: "编码阶段",
    reviewer: "审查阶段",
    tester: "测试阶段",
  };

  return nameMap[stepName.toLowerCase()] || stepName;
}

/**
 * Format timestamp to readable format
 */
function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) {
    return "—";
  }

  const date = new Date(timestamp);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

/**
 * Format duration in milliseconds
 */
function formatDuration(durationMs: number | null): string {
  if (durationMs === null) {
    return "—";
  }

  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    const remainingMinutes = minutes % 60;
    const remainingSeconds = seconds % 60;
    return `${hours}h ${remainingMinutes}m ${remainingSeconds}s`;
  }

  if (minutes > 0) {
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }

  if (seconds > 0) {
    return `${seconds}s`;
  }

  return `${durationMs}ms`;
}

/**
 * Get status description
 */
function getStatusDescription(status: StepState["status"]): string {
  switch (status) {
    case "pending":
      return "此步骤正在等待执行";
    case "running":
      return "此步骤正在运行中";
    case "completed":
      return "此步骤已成功完成";
    case "failed":
      return "此步骤执行失败";
    case "skipped":
      return "此步骤已被跳过";
    case "retrying":
      return "此步骤正在重试";
    case "cancelled":
      return "此步骤已被取消";
    default:
      return "";
  }
}

export function DetailPanel({ step, className = "" }: DetailPanelProps) {
  // Empty state
  if (!step) {
    return (
      <div
        className={`rounded-lg border border-gray-200 bg-white p-6 shadow-sm ${className}`}
        role="region"
        aria-label="步骤详情"
      >
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg mb-2">暂无选中步骤</p>
          <p className="text-sm">请点击步骤卡片查看详细信息</p>
        </div>
      </div>
    );
  }

  const displayName = getStepDisplayName(step.name);
  const statusDescription = getStatusDescription(step.status);
  const startedAt = formatTimestamp(step.startedAt);
  const completedAt = formatTimestamp(step.completedAt);
  const duration = formatDuration(step.durationMs);

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}
      role="region"
      aria-label={`步骤详情: ${displayName}`}
    >
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          {displayName}
        </h2>
        <div className="flex items-center gap-3">
          <StatusBadge status={step.status} />
          {step.retryCount > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">
              重试 {step.retryCount} 次
            </span>
          )}
        </div>
        {statusDescription && (
          <p className="mt-2 text-sm text-gray-600">{statusDescription}</p>
        )}
      </div>

      {/* Details */}
      <div className="p-6 space-y-6">
        {/* Timestamps */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">时间信息</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-500">开始时间</span>
              <p className="mt-1 text-sm font-mono text-gray-900">
                {startedAt}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-500">完成时间</span>
              <p className="mt-1 text-sm font-mono text-gray-900">
                {completedAt}
              </p>
            </div>
          </div>
        </div>

        {/* Duration */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">执行时长</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{duration}</span>
            {step.durationMs !== null && step.durationMs >= 1000 && (
              <span className="text-sm text-gray-500">
                ({step.durationMs.toLocaleString()} ms)
              </span>
            )}
          </div>
        </div>

        {/* Error message (if failed) */}
        {step.status === "failed" && step.errorMessage && (
          <div>
            <h3 className="text-sm font-semibold text-red-700 mb-3">
              错误信息
            </h3>
            <div className="p-4 rounded bg-red-50 border border-red-200">
              <p className="text-sm text-red-800 whitespace-pre-wrap">
                {step.errorMessage}
              </p>
            </div>
          </div>
        )}

        {/* Retry information */}
        {step.retryCount > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-orange-700 mb-3">
              重试信息
            </h3>
            <div className="p-4 rounded bg-orange-50 border border-orange-200">
              <p className="text-sm text-orange-800">
                此步骤已重试{" "}
                <span className="font-bold">{step.retryCount}</span> 次
              </p>
            </div>
          </div>
        )}

        {/* Status-specific information */}
        {step.status === "running" && (
          <div className="p-4 rounded bg-blue-50 border border-blue-200">
            <p className="text-sm text-blue-800">
              ⏳ 此步骤正在执行中，请稍候...
            </p>
          </div>
        )}

        {step.status === "pending" && (
          <div className="p-4 rounded bg-gray-50 border border-gray-200">
            <p className="text-sm text-gray-700">⏸ 此步骤正在队列中等待执行</p>
          </div>
        )}

        {step.status === "completed" && (
          <div className="p-4 rounded bg-green-50 border border-green-200">
            <p className="text-sm text-green-800">✓ 此步骤已成功完成</p>
          </div>
        )}

        {step.status === "skipped" && (
          <div className="p-4 rounded bg-gray-50 border border-gray-200">
            <p className="text-sm text-gray-700">— 此步骤已被跳过</p>
          </div>
        )}

        {step.status === "cancelled" && (
          <div className="p-4 rounded bg-gray-100 border border-gray-300">
            <p className="text-sm text-gray-700">⊗ 此步骤已被取消</p>
          </div>
        )}
      </div>
    </div>
  );
}
