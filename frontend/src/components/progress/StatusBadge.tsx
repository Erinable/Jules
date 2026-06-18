/**
 * StatusBadge Component (Sprint 3 - Phase 1 MVP)
 *
 * Displays status with color-coded badge.
 * Based on docs/design/progress-ui-prototype.md
 */

type StepStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "skipped"
  | "retrying"
  | "cancelled";

interface StatusBadgeProps {
  status: StepStatus;
  className?: string;
}

/**
 * Get badge color classes based on status
 */
function getStatusColors(status: StepStatus): {
  bg: string;
  text: string;
  border: string;
} {
  switch (status) {
    case "pending":
      return {
        bg: "bg-gray-100",
        text: "text-gray-700",
        border: "border-gray-300",
      };
    case "running":
      return {
        bg: "bg-yellow-100",
        text: "text-yellow-700",
        border: "border-yellow-300",
      };
    case "completed":
      return {
        bg: "bg-green-100",
        text: "text-green-700",
        border: "border-green-300",
      };
    case "failed":
      return {
        bg: "bg-red-100",
        text: "text-red-700",
        border: "border-red-300",
      };
    case "skipped":
      return {
        bg: "bg-gray-100",
        text: "text-gray-500",
        border: "border-gray-200",
      };
    case "retrying":
      return {
        bg: "bg-orange-100",
        text: "text-orange-700",
        border: "border-orange-300",
      };
    case "cancelled":
      return {
        bg: "bg-gray-200",
        text: "text-gray-600",
        border: "border-gray-400",
      };
    default:
      return {
        bg: "bg-gray-100",
        text: "text-gray-700",
        border: "border-gray-300",
      };
  }
}

/**
 * Get status icon/symbol
 */
function getStatusIcon(status: StepStatus): string {
  switch (status) {
    case "pending":
      return "○";
    case "running":
      return "●";
    case "completed":
      return "✓";
    case "failed":
      return "✗";
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
 * Get localized status label
 */
function getStatusLabel(status: StepStatus): string {
  switch (status) {
    case "pending":
      return "待处理";
    case "running":
      return "运行中";
    case "completed":
      return "已完成";
    case "failed":
      return "失败";
    case "skipped":
      return "跳过";
    case "retrying":
      return "重试中";
    case "cancelled":
      return "已取消";
    default:
      return status;
  }
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const colors = getStatusColors(status);
  const icon = getStatusIcon(status);
  const label = getStatusLabel(status);

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border} ${className}`}
      role="status"
      aria-label={label}
    >
      <span className="text-sm" aria-hidden="true">
        {icon}
      </span>
      <span>{label}</span>
    </span>
  );
}
