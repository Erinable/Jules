/**
 * Execution type definitions based on backend Pydantic schemas
 */

export type ExecutionStatus = "pending" | "running" | "completed" | "failed";

export interface Execution {
  id: string;
  task_id: string;
  agent_type: string;
  state?: Record<string, unknown>;
  status: ExecutionStatus;
  started_at: string;
  completed_at?: string;
  [key: string]: unknown;
}

export interface ExecutionCreate {
  task_id: string;
  agent_type: string;
  state?: Record<string, unknown>;
}

export interface ExecutionStatusUpdate {
  status: ExecutionStatus;
}

export interface ExecutionResponse extends Execution {}
