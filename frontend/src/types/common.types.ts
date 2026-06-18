/**
 * Common API types and pagination
 */

export interface ApiError {
  detail: string;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface HealthStatus {
  status: string;
  database?: string;
  timestamp?: string;
}
