/**
 * WebSocket message handlers (Sprint 2)
 *
 * Utilities for handling different WebSocket message types.
 */

import type {
  AgentStatusData,
  CodeChunkData,
  ProgressLogAppendedData,
  ProgressStepCompletedData,
  ProgressStepFailedData,
  ProgressStepStartedData,
  ProgressUpdatedData,
  SystemErrorData,
  TaskCompletedData,
  TaskCreatedData,
  WSMessage,
} from "../types/websocket.types";

/**
 * Create a type-safe message handler wrapper
 */
export function createMessageHandler<T = Record<string, unknown>>(
  handler: (data: T, message: WSMessage<T>) => void,
) {
  return (message: WSMessage<T>) => {
    handler(message.data, message);
  };
}

/**
 * Agent status change handler
 */
export function handleAgentStatus(
  data: AgentStatusData,
  onStatusChange?: (status: string, agentId: string, runId: string) => void,
) {
  if (onStatusChange) {
    onStatusChange(data.current_status, data.agent_id, data.run_id);
  }
}

/**
 * Code chunk handler (for streaming code display)
 */
export function handleCodeChunk(
  data: CodeChunkData,
  onChunk?: (chunk: string, index: number, isFinal: boolean) => void,
) {
  if (onChunk) {
    onChunk(data.content, data.chunk_index, data.is_final);
  }
}

/**
 * Task created notification handler
 */
export function handleTaskCreated(
  data: TaskCreatedData,
  onTaskCreated?: (taskId: string, title: string) => void,
) {
  if (onTaskCreated) {
    onTaskCreated(data.task_id, data.title);
  }
}

/**
 * Task completed notification handler
 */
export function handleTaskCompleted(
  data: TaskCompletedData,
  onTaskCompleted?: (taskId: string, status: string, summary: string) => void,
) {
  if (onTaskCompleted) {
    onTaskCompleted(data.task_id, data.status, data.result_summary);
  }
}

/**
 * System error handler
 */
export function handleSystemError(
  data: SystemErrorData,
  onError?: (code: string, message: string, recoverable: boolean) => void,
) {
  if (onError) {
    onError(data.code, data.message, data.recoverable);
  }
}

/**
 * Progress step started handler (Sprint 3 integration)
 */
export function handleProgressStepStarted(
  data: ProgressStepStartedData,
  onStepStarted?: (runId: string, step: string) => void,
) {
  if (onStepStarted) {
    onStepStarted(data.run_id, data.step);
  }
}

/**
 * Progress step completed handler (Sprint 3 integration)
 */
export function handleProgressStepCompleted(
  data: ProgressStepCompletedData,
  onStepCompleted?: (runId: string, step: string, duration: number) => void,
) {
  if (onStepCompleted) {
    onStepCompleted(data.run_id, data.step, data.duration_ms);
  }
}

/**
 * Progress step failed handler (Sprint 3 integration)
 */
export function handleProgressStepFailed(
  data: ProgressStepFailedData,
  onStepFailed?: (runId: string, step: string, error: string) => void,
) {
  if (onStepFailed) {
    onStepFailed(data.run_id, data.step, data.error_message);
  }
}

/**
 * Progress updated handler (Sprint 3 integration)
 */
export function handleProgressUpdated(
  data: ProgressUpdatedData,
  onProgressUpdate?: (
    runId: string,
    percentage: number,
    eta: number | null,
  ) => void,
) {
  if (onProgressUpdate) {
    onProgressUpdate(data.run_id, data.overall_percentage, data.eta_seconds);
  }
}

/**
 * Progress log appended handler (Sprint 3 integration)
 */
export function handleProgressLogAppended(
  data: ProgressLogAppendedData,
  onLogAppended?: (runId: string, level: string, message: string) => void,
) {
  if (onLogAppended) {
    onLogAppended(data.run_id, data.level, data.message);
  }
}

/**
 * Batch register all message handlers
 */
export function registerMessageHandlers(
  on: <T = Record<string, unknown>>(
    type: import("../types/websocket.types").MessageType,
    handler: import("../types/websocket.types").MessageHandler<T>,
  ) => () => void,
  handlers: {
    onAgentStatus?: (status: string, agentId: string, runId: string) => void;
    onCodeChunk?: (chunk: string, index: number, isFinal: boolean) => void;
    onTaskCreated?: (taskId: string, title: string) => void;
    onTaskCompleted?: (taskId: string, status: string, summary: string) => void;
    onSystemError?: (
      code: string,
      message: string,
      recoverable: boolean,
    ) => void;
    onProgressStepStarted?: (runId: string, step: string) => void;
    onProgressStepCompleted?: (
      runId: string,
      step: string,
      duration: number,
    ) => void;
    onProgressStepFailed?: (runId: string, step: string, error: string) => void;
    onProgressUpdate?: (
      runId: string,
      percentage: number,
      eta: number | null,
    ) => void;
    onLogAppended?: (runId: string, level: string, message: string) => void;
  },
): (() => void)[] {
  const cleanups: (() => void)[] = [];

  if (handlers.onAgentStatus) {
    cleanups.push(
      on<AgentStatusData>("agent.status", (msg) =>
        handleAgentStatus(msg.data, handlers.onAgentStatus),
      ),
    );
  }

  if (handlers.onCodeChunk) {
    cleanups.push(
      on<CodeChunkData>("code.chunk", (msg) =>
        handleCodeChunk(msg.data, handlers.onCodeChunk),
      ),
    );
  }

  if (handlers.onTaskCreated) {
    cleanups.push(
      on<TaskCreatedData>("task.created", (msg) =>
        handleTaskCreated(msg.data, handlers.onTaskCreated),
      ),
    );
  }

  if (handlers.onTaskCompleted) {
    cleanups.push(
      on<TaskCompletedData>("task.completed", (msg) =>
        handleTaskCompleted(msg.data, handlers.onTaskCompleted),
      ),
    );
  }

  if (handlers.onSystemError) {
    cleanups.push(
      on<SystemErrorData>("system.error", (msg) =>
        handleSystemError(msg.data, handlers.onSystemError),
      ),
    );
  }

  if (handlers.onProgressStepStarted) {
    cleanups.push(
      on<ProgressStepStartedData>("progress.step.started", (msg) =>
        handleProgressStepStarted(msg.data, handlers.onProgressStepStarted),
      ),
    );
  }

  if (handlers.onProgressStepCompleted) {
    cleanups.push(
      on<ProgressStepCompletedData>("progress.step.completed", (msg) =>
        handleProgressStepCompleted(msg.data, handlers.onProgressStepCompleted),
      ),
    );
  }

  if (handlers.onProgressStepFailed) {
    cleanups.push(
      on<ProgressStepFailedData>("progress.step.failed", (msg) =>
        handleProgressStepFailed(msg.data, handlers.onProgressStepFailed),
      ),
    );
  }

  if (handlers.onProgressUpdate) {
    cleanups.push(
      on<ProgressUpdatedData>("progress.updated", (msg) =>
        handleProgressUpdated(msg.data, handlers.onProgressUpdate),
      ),
    );
  }

  if (handlers.onLogAppended) {
    cleanups.push(
      on<ProgressLogAppendedData>("progress.log.appended", (msg) =>
        handleProgressLogAppended(msg.data, handlers.onLogAppended),
      ),
    );
  }

  return cleanups;
}
