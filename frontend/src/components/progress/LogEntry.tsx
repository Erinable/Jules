/**
 * LogEntry Component (Sprint 3 - Phase 2)
 *
 * Single log entry display with level-based color coding.
 * Based on docs/design/progress-ui-prototype.md
 */

import type { LogEntry as LogEntryType } from "@/hooks/useProgressTracking";

interface LogEntryProps {
  log: LogEntryType;
  className?: string;
}

/**
 * Get log level color classes
 */
function getLogLevelColors(level: LogEntryType["level"]): {
  text: string;
  bg: string;
  badge: string;
} {
  switch (level) {
    case "debug":
      return {
        text: "text-gray-600",
        bg: "bg-gray-50",
        badge: "bg-gray-200 text-gray-700",
      };
    case "info":
      return {
        text: "text-blue-700",
        bg: "bg-blue-50",
        badge: "bg-blue-200 text-blue-700",
      };
    case "warning":
      return {
        text: "text-yellow-700",
        bg: "bg-yellow-50",
        badge: "bg-yellow-200 text-yellow-700",
      };
    case "error":
      return {
        text: "text-red-700",
        bg: "bg-red-50",
        badge: "bg-red-200 text-red-700",
      };
    default:
      return {
        text: "text-gray-600",
        bg: "bg-gray-50",
        badge: "bg-gray-200 text-gray-700",
      };
  }
}

/**
 * Get log level icon
 */
function getLogLevelIcon(level: LogEntryType["level"]): string {
  switch (level) {
    case "debug":
      return "🔍";
    case "info":
      return "ℹ️";
    case "warning":
      return "⚠️";
    case "error":
      return "❌";
    default:
      return "•";
  }
}

/**
 * Format timestamp to human-readable format
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
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

export function LogEntry({ log, className = "" }: LogEntryProps) {
  const colors = getLogLevelColors(log.level);
  const icon = getLogLevelIcon(log.level);
  const time = formatTimestamp(log.timestamp);
  const stepName = getStepDisplayName(log.step);

  return (
    <div
      className={`flex items-start gap-3 px-3 py-2 rounded hover:${colors.bg} transition-colors ${className}`}
      role="article"
      aria-label={`日志: ${log.message}`}
    >
      {/* Level icon */}
      <span className="text-sm flex-shrink-0 mt-0.5" aria-label={log.level}>
        {icon}
      </span>

      {/* Log content */}
      <div className="flex-1 min-w-0">
        {/* Header: timestamp + level + step */}
        <div className="flex items-center gap-2 mb-1">
          <time
            className="text-xs text-gray-500 font-mono"
            dateTime={log.timestamp}
          >
            {time}
          </time>

          <span
            className={`text-xs px-1.5 py-0.5 rounded ${colors.badge} font-medium`}
          >
            {log.level.toUpperCase()}
          </span>

          <span className="text-xs text-gray-600">{stepName}</span>

          <span className="text-xs text-gray-400">#{log.sequenceNum}</span>
        </div>

        {/* Message */}
        <p className={`text-sm ${colors.text} break-words`}>{log.message}</p>
      </div>
    </div>
  );
}
