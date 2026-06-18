/**
 * LogPanel Component (Sprint 3 - Phase 2)
 *
 * Displays real-time scrolling logs with filtering capabilities.
 * Based on docs/design/progress-ui-prototype.md
 */

import { useEffect, useRef, useState } from "react";
import {
  useProgressTracking,
  type LogEntry as LogEntryType,
} from "@/hooks/useProgressTracking";
import { LogEntry } from "./LogEntry";

interface LogPanelProps {
  runId: string;
  className?: string;
}

type LogLevel = "debug" | "info" | "warning" | "error";
type StepFilter =
  | "all"
  | "researcher"
  | "planner"
  | "coder"
  | "reviewer"
  | "tester";

export function LogPanel({ runId, className = "" }: LogPanelProps) {
  const { logs, isLoading, error } = useProgressTracking(runId);
  const [levelFilter, setLevelFilter] = useState<LogLevel | "all">("all");
  const [stepFilter, setStepFilter] = useState<StepFilter>("all");
  const [autoScroll, setAutoScroll] = useState(true);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const prevLogsLengthRef = useRef(0);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (
      autoScroll &&
      logs.length > prevLogsLengthRef.current &&
      logContainerRef.current
    ) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
    prevLogsLengthRef.current = logs.length;
  }, [logs, autoScroll]);

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    const levelMatch = levelFilter === "all" || log.level === levelFilter;
    const stepMatch = stepFilter === "all" || log.step === stepFilter;
    return levelMatch && stepMatch;
  });

  // Handle scroll to detect manual scrolling
  const handleScroll = () => {
    if (!logContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
    const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < 10;

    setAutoScroll(isAtBottom);
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        className={`rounded-lg border border-gray-200 bg-white p-6 shadow-sm ${className}`}
      >
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
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
          <span className="font-medium">加载日志失败</span>
        </div>
        <p className="mt-2 text-sm text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}
      role="region"
      aria-label="执行日志"
    >
      {/* Header with filters */}
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Title and count */}
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-semibold text-gray-900">执行日志</h3>
            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
              {filteredLogs.length} / {logs.length}
            </span>
          </div>

          {/* Auto-scroll toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              autoScroll
                ? "bg-blue-50 border-blue-200 text-blue-700"
                : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
            }`}
            aria-pressed={autoScroll}
          >
            {autoScroll ? "✓ 自动滚动" : "○ 自动滚动"}
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mt-3">
          {/* Level filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">级别:</span>
            <div className="flex gap-1">
              {(["all", "debug", "info", "warning", "error"] as const).map(
                (level) => (
                  <button
                    key={level}
                    onClick={() => setLevelFilter(level)}
                    className={`text-xs px-2 py-1 rounded border transition-colors ${
                      levelFilter === level
                        ? "bg-blue-50 border-blue-300 text-blue-700 font-medium"
                        : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50"
                    }`}
                    aria-pressed={levelFilter === level}
                  >
                    {level === "all" ? "全部" : level.toUpperCase()}
                  </button>
                ),
              )}
            </div>
          </div>

          {/* Step filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">步骤:</span>
            <div className="flex gap-1">
              {(
                [
                  "all",
                  "researcher",
                  "planner",
                  "coder",
                  "reviewer",
                  "tester",
                ] as const
              ).map((step) => {
                const stepNames: Record<string, string> = {
                  all: "全部",
                  researcher: "调研",
                  planner: "规划",
                  coder: "编码",
                  reviewer: "审查",
                  tester: "测试",
                };

                return (
                  <button
                    key={step}
                    onClick={() => setStepFilter(step)}
                    className={`text-xs px-2 py-1 rounded border transition-colors ${
                      stepFilter === step
                        ? "bg-blue-50 border-blue-300 text-blue-700 font-medium"
                        : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50"
                    }`}
                    aria-pressed={stepFilter === step}
                  >
                    {stepNames[step]}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Log entries container */}
      <div
        ref={logContainerRef}
        onScroll={handleScroll}
        className="overflow-y-auto max-h-96 divide-y divide-gray-100"
        role="log"
        aria-live="polite"
        aria-atomic="false"
      >
        {filteredLogs.length > 0 ? (
          filteredLogs.map((log) => (
            <LogEntry key={`${log.sequenceNum}-${log.timestamp}`} log={log} />
          ))
        ) : (
          <div className="p-8 text-center text-gray-500">
            <p>暂无日志</p>
            {(levelFilter !== "all" || stepFilter !== "all") && (
              <p className="text-sm mt-2">尝试调整过滤条件</p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      {filteredLogs.length > 0 && (
        <div className="border-t border-gray-100 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>
              显示 {filteredLogs.length} 条日志
              {(levelFilter !== "all" || stepFilter !== "all") && ` (已过滤)`}
            </span>
            {!autoScroll && (
              <button
                onClick={() => {
                  if (logContainerRef.current) {
                    logContainerRef.current.scrollTop =
                      logContainerRef.current.scrollHeight;
                    setAutoScroll(true);
                  }
                }}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                滚动到底部 ↓
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
