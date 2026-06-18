/**
 * WebSocket message types (Sprint 2)
 *
 * TypeScript definitions matching backend Pydantic schemas.
 * Based on docs/design/websocket-message-protocol.md
 */

/**
 * All WebSocket message types
 */
export type MessageType =
  // Server → Client
  | "agent.status"
  | "code.chunk"
  | "task.created"
  | "task.completed"
  | "system.error"
  | "pong"
  | "ack"
  | "welcome"
  // Client → Server
  | "ping"
  | "subscribe"
  | "unsubscribe"
  | "ack.response"
  // Sprint 3 integration (progress tracking)
  | "progress.step.started"
  | "progress.step.completed"
  | "progress.step.failed"
  | "progress.updated"
  | "progress.log.appended";

/**
 * WebSocket message envelope (immutable)
 *
 * All WebSocket messages follow this unified structure.
 */
export interface WSMessage<T = Record<string, unknown>> {
  type: MessageType;
  data: T;
  timestamp: string; // ISO 8601 UTC
  id: string; // UUID
  ack_required?: boolean;
}

/**
 * Message data types by message type
 */

export interface AgentStatusData {
  agent_id: string;
  run_id: string;
  previous_status?: string;
  current_status: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
}

export interface CodeChunkData {
  run_id: string;
  step: string;
  file_path?: string;
  chunk_index: number;
  content: string;
  is_final: boolean;
}

export interface TaskCreatedData {
  task_id: string;
  user_id: string;
  title: string;
  priority: string;
  created_at: string;
}

export interface TaskCompletedData {
  task_id: string;
  status: "completed" | "failed" | "cancelled";
  result_summary: string;
  artifacts?: Array<{ type: string; path: string }>;
  total_duration_ms: number;
}

export interface SystemErrorData {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  recoverable: boolean;
}

export interface PongData {
  server_time: string;
}

export interface WelcomeData {
  connection_id: string;
  user_id: string;
  heartbeat_interval_seconds: number;
  server_time: string;
  protocol_version: string;
}

export interface SubscribeData {
  channel: string;
}

export interface UnsubscribeData {
  channel: string;
}

export interface AckResponseData {
  message_id: string;
  status: "received" | "processed" | "failed";
}

// Sprint 3 progress tracking data types

export interface ProgressStepStartedData {
  run_id: string;
  step: string;
  started_at: string;
}

export interface ProgressStepCompletedData {
  run_id: string;
  step: string;
  duration_ms: number;
  retry_count: number;
}

export interface ProgressStepFailedData {
  run_id: string;
  step: string;
  error_message: string;
  retry_count: number;
}

export interface ProgressUpdatedData {
  run_id: string;
  overall_percentage: number;
  eta_seconds: number | null;
  current_step: string | null;
}

export interface ProgressLogAppendedData {
  run_id: string;
  step: string;
  level: "debug" | "info" | "warning" | "error";
  message: string;
  sequence_num: number;
}

/**
 * WebSocket connection states
 */
export type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting"
  | "error";

/**
 * WebSocket hook configuration
 */
export interface WebSocketConfig {
  url: string;
  token: string;
  heartbeatInterval?: number; // ms (default 30000)
  reconnectDelays?: number[]; // ms (default [1000, 2000, 4000])
  maxReconnectAttempts?: number; // default 3
}

/**
 * WebSocket message handler
 */
export type MessageHandler<T = Record<string, unknown>> = (
  message: WSMessage<T>,
) => void;

/**
 * WebSocket error types
 */
export type WebSocketErrorCode =
  | "AUTH_FAILED" // 4401
  | "FORBIDDEN" // 4403
  | "PROTOCOL_VERSION_MISMATCH" // 4404
  | "CONFLICT" // 4409
  | "RATE_LIMITED" // 4429
  | "CONNECTION_TIMEOUT"
  | "INVALID_MESSAGE"
  | "UNKNOWN_ERROR";

export interface WebSocketError {
  code: WebSocketErrorCode;
  message: string;
  recoverable: boolean;
}
