/**
 * StepCard Component (Sprint 3 - Phase 2)
 *
 * Displays detailed information for a single execution step.
 * Based on docs/design/progress-ui-prototype.md
 */

import type { StepState } from "@/hooks/useProgressTracking";
import { StatusBadge } from "./StatusBadge";

interface StepCardProps {
  step: StepState;
  isExpanded?: boolean;
  onToggle?: () => void;
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
 * Format duration in milliseconds to human-readable
 */
function formatDuration(durationMs: number | null): string {
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
 * Format timestamp to readable format
 */
function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) {
    return "—";
  }

  const date = new Date(timestamp);
  return date.toLocaleString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

/**
 * Get status icon
 */
function getStatusIcon(status: StepState["status"]): string {
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

export function StepCard({
  step,
  isExpanded = false,
  onToggle,
  className = "",
}: StepCardProps) {
  const displayName = getStepDisplayName(step.name);
  const icon = getStatusIcon(step.status);
  const duration = formatDuration(step.durationMs);
  const startedAt = formatTimestamp(step.startedAt);
  const completedAt = formatTimestamp(step.completedAt);

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}
      role="article"
      aria-label={`步骤详情: ${displayName}`}
    >
      {/* Header */}
      <div
        className={`flex items-center justify-between p-4 ${onToggle ? "cursor-pointer hover:bg-gray-50" : ""}`}
        onClick={onToggle}
        role={onToggle ? "button" : undefined}
        aria-expanded={onToggle ? isExpanded : undefined}
      >
        <div className="flex items-center gap-3">
          {/* Status icon */}
          <span
            className={`text-2xl ${
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

          {/* Step name and status */}
          <div>
            <h3 className="font-semibold text-gray-900">{displayName}</h3>
            <div className="flex items-center gap-2 mt-1">
              <StatusBadge status={step.status} />
              {step.retryCount > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">
                  重试 {step.retryCount} 次
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Duration */}
        <div className="text-right">
          <div className="text-sm font-medium text-gray-900">{duration}</div>
          <div className="text-xs text-gray-500">
            {step.status === "completed"
              ? "已完成"
              : step.status === "running"
                ? "进行中"
                : step.status === "failed"
                  ? "失败"
                  : "待处理"}
          </div>
        </div>

        {/* Expand indicator */}
        {onToggle && (
          <span className="ml-2 text-gray-400" aria-hidden="true">
            {isExpanded ? "▼" : "▶"}
          </span>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-gray-100 space-y-3">
          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">开始时间</span>
              <p className="mt-1 font-mono text-gray-900">{startedAt}</p>
            </div>
            <div>
              <span className="text-gray-500">完成时间</span>
              <p className="mt-1 font-mono text-gray-900">{completedAt}</p>
            </div>
          </div>

          {/* Duration breakdown */}
          {step.durationMs !== null && (
            <div>
              <span className="text-sm text-gray-500">耗时详情</span>
              <p className="mt-1 text-sm text-gray-900">
                {duration} ({step.durationMs.toLocaleString()} ms)
              </p>
            </div>
          )}

          {/* Error message */}
          {step.status === "failed" && step.errorMessage && (
            <div className="p-3 rounded bg-red-50 border border-red-200">
              <div className="text-sm font-medium text-red-800 mb-1">
                错误信息
              </div>
              <p className="text-sm text-red-700">{step.errorMessage}</p>
            </div>
          )}

          {/* Retry information */}
          {step.retryCount > 0 && (
            <div className="p-3 rounded bg-orange-50 border border-orange-200">
              <div className="text-sm font-medium text-orange-800">
                已重试 {step.retryCount} 次
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
