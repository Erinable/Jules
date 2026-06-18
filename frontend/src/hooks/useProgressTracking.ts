/**
 * useProgressTracking Hook (Sprint 3)
 *
 * Manages progress tracking state with WebSocket updates.
 * Based on docs/design/progress-ui-prototype.md
 */

import { useEffect, useState } from "react";
import { useWebSocketContext } from "@/contexts/WebSocketContext";
import type {
  ProgressStepCompletedData,
  ProgressStepFailedData,
  ProgressStepStartedData,
  ProgressUpdatedData,
  ProgressLogAppendedData,
} from "@/types/websocket.types";

export interface StepState {
  name: string;
  status:
    | "pending"
    | "running"
    | "completed"
    | "failed"
    | "skipped"
    | "retrying"
    | "cancelled";
  startedAt: string | null;
  completedAt: string | null;
  durationMs: number | null;
  retryCount: number;
  errorMessage: string | null;
}

export interface ProgressState {
  runId: string;
  status: string;
  steps: StepState[];
  currentStep: string | null;
  overallPercentage: number;
  etaSeconds: number | null;
  startedAt: string;
  updatedAt: string;
  completedAt: string | null;
}

export interface LogEntry {
  step: string;
  level: "debug" | "info" | "warning" | "error";
  message: string;
  sequenceNum: number;
  timestamp: string;
}

interface UseProgressTrackingReturn {
  progress: ProgressState | null;
  logs: LogEntry[];
  isLoading: boolean;
  error: string | null;
}

export function useProgressTracking(runId: string): UseProgressTrackingReturn {
  const { on, subscribe } = useWebSocketContext();
  const [progress, setProgress] = useState<ProgressState | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Subscribe to progress channel
    subscribe(`progress:${runId}`);

    // Fetch initial state (REST API call)
    fetch(`/api/v1/progress/${runId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setProgress(data.data);
          setIsLoading(false);
        } else {
          setError(data.error || "Failed to load progress");
          setIsLoading(false);
        }
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });

    // Handle progress.step.started
    const cleanupStepStarted = on<ProgressStepStartedData>(
      "progress.step.started",
      (msg) => {
        if (msg.data.run_id === runId) {
          setProgress((prev) => {
            if (!prev) return prev;
            const updatedSteps = prev.steps.map((step) =>
              step.name === msg.data.step
                ? {
                    ...step,
                    status: "running" as const,
                    startedAt: msg.data.started_at,
                  }
                : step,
            );
            return { ...prev, steps: updatedSteps, currentStep: msg.data.step };
          });
        }
      },
    );

    // Handle progress.step.completed
    const cleanupStepCompleted = on<ProgressStepCompletedData>(
      "progress.step.completed",
      (msg) => {
        if (msg.data.run_id === runId) {
          setProgress((prev) => {
            if (!prev) return prev;
            const updatedSteps = prev.steps.map((step) =>
              step.name === msg.data.step
                ? {
                    ...step,
                    status: "completed" as const,
                    completedAt: new Date().toISOString(),
                    durationMs: msg.data.duration_ms,
                    retryCount: msg.data.retry_count,
                  }
                : step,
            );
            return { ...prev, steps: updatedSteps };
          });
        }
      },
    );

    // Handle progress.step.failed
    const cleanupStepFailed = on<ProgressStepFailedData>(
      "progress.step.failed",
      (msg) => {
        if (msg.data.run_id === runId) {
          setProgress((prev) => {
            if (!prev) return prev;
            const updatedSteps = prev.steps.map((step) =>
              step.name === msg.data.step
                ? {
                    ...step,
                    status: "failed" as const,
                    errorMessage: msg.data.error_message,
                    retryCount: msg.data.retry_count,
                  }
                : step,
            );
            return { ...prev, steps: updatedSteps };
          });
        }
      },
    );

    // Handle progress.updated
    const cleanupProgressUpdated = on<ProgressUpdatedData>(
      "progress.updated",
      (msg) => {
        if (msg.data.run_id === runId) {
          setProgress((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              overallPercentage: msg.data.overall_percentage,
              etaSeconds: msg.data.eta_seconds,
              currentStep: msg.data.current_step,
              updatedAt: new Date().toISOString(),
            };
          });
        }
      },
    );

    // Handle progress.log.appended
    const cleanupLogAppended = on<ProgressLogAppendedData>(
      "progress.log.appended",
      (msg) => {
        if (msg.data.run_id === runId) {
          setLogs((prev) => [
            ...prev,
            {
              step: msg.data.step,
              level: msg.data.level as LogEntry["level"],
              message: msg.data.message,
              sequenceNum: msg.data.sequence_num,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      },
    );

    return () => {
      cleanupStepStarted();
      cleanupStepCompleted();
      cleanupStepFailed();
      cleanupProgressUpdated();
      cleanupLogAppended();
    };
  }, [runId, on, subscribe]);

  return {
    progress,
    logs,
    isLoading,
    error,
  };
}
