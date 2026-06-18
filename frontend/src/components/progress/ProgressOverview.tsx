/**
 * ProgressOverview Component (Sprint 3 - Phase 1 MVP)
 *
 * Displays overall progress snapshot with percentage, ETA, and status.
 * Based on docs/design/progress-ui-prototype.md
 */

import { useProgressTracking } from "@/hooks/useProgressTracking";
import { ProgressBar } from "./ProgressBar";
import { StatusBadge } from "./StatusBadge";

interface ProgressOverviewProps {
  runId: string;
  className?: string;
}

type RunStatus =
  | "queued"
  | "running"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled"
  | "timeout";

/**
 * Get run status badge configuration
 */
function getRunStatusBadge(status: RunStatus): {
  label: string;
  className: string;
} {
  switch (status) {
    case "queued":
      return {
        label: "排队中",
        className: "bg-gray-100 text-gray-700 border-gray-300",
      };
    case "running":
      return {
        label: "运行中",
        className: "bg-blue-100 text-blue-700 border-blue-300",
      };
    case "paused":
      return {
        label: "已暂停",
        className: "bg-yellow-100 text-yellow-700 border-yellow-300",
      };
    case "completed":
      return {
        label: "已完成",
        className: "bg-green-100 text-green-700 border-green-300",
      };
    case "failed":
      return {
        label: "失败",
        className: "bg-red-100 text-red-700 border-red-300",
      };
    case "cancelled":
      return {
        label: "已取消",
        className: "bg-gray-200 text-gray-600 border-gray-400",
      };
    case "timeout":
      return {
        label: "超时",
        className: "bg-orange-100 text-orange-700 border-orange-300",
      };
    default:
      return {
        label: status,
        className: "bg-gray-100 text-gray-700 border-gray-300",
      };
  }
}

/**
 * Format duration from start to now (or completion)
 */
function calculateTotalDuration(
  startedAt: string,
  completedAt: string | null,
): string {
  const start = new Date(startedAt).getTime();
  const end = completedAt ? new Date(completedAt).getTime() : Date.now();
  const durationMs = end - start;

  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  }

  if (minutes > 0) {
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }

  return `${seconds}s`;
}

export function ProgressOverview({
  runId,
  className = "",
}: ProgressOverviewProps) {
  const { progress, isLoading, error } = useProgressTracking(runId);

  // Loading state
  if (isLoading) {
    return (
      <div
        className={`rounded-lg border border-gray-200 bg-white p-6 shadow-sm ${className}`}
      >
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/2" />
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className={`rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm ${className}`}
      >
        <div className="flex items-center gap-2 text-red-700">
          <span className="text-xl">⚠</span>
          <span className="font-medium">加载进度失败</span>
        </div>
        <p className="mt-2 text-sm text-red-600">{error}</p>
      </div>
    );
  }

  // No data state
  if (!progress) {
    return (
      <div
        className={`rounded-lg border border-gray-200 bg-gray-50 p-6 shadow-sm ${className}`}
      >
        <p className="text-gray-500">暂无进度数据</p>
      </div>
    );
  }

  const statusBadge = getRunStatusBadge(progress.status as RunStatus);
  const completedSteps = progress.steps.filter(
    (s) => s.status === "completed",
  ).length;
  const totalSteps = progress.steps.length;
  const totalDuration = calculateTotalDuration(
    progress.startedAt,
    progress.completedAt,
  );

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-6 shadow-sm ${className}`}
      role="region"
      aria-label="执行进度概览"
    >
      {/* Header with status badge */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">执行进度</h2>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusBadge.className}`}
          role="status"
        >
          {statusBadge.label}
        </span>
      </div>

      {/* Progress bar */}
      <ProgressBar
        percentage={progress.overallPercentage}
        eta={progress.etaSeconds}
      />

      {/* Progress details */}
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-500">当前步骤</span>
          <p className="mt-1 font-medium text-gray-900">
            {progress.currentStep || "准备中"}
          </p>
        </div>

        <div>
          <span className="text-gray-500">步骤进度</span>
          <p className="mt-1 font-medium text-gray-900">
            {completedSteps}/{totalSteps}
          </p>
        </div>

        <div className="col-span-2 sm:col-span-1">
          <span className="text-gray-500">总耗时</span>
          <p className="mt-1 font-medium text-gray-900">{totalDuration}</p>
        </div>
      </div>

      {/* Run ID (for debugging) */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <span className="text-xs text-gray-400">Run ID: {runId}</span>
      </div>
    </div>
  );
}
