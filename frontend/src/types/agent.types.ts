/**
 * Agent type definitions based on backend Pydantic schemas
 */

export interface Agent {
  id: string
  name: string
  description?: string
  config: Record<string, unknown>
  is_active: string
  created_at: string
  updated_at?: string
}

export interface AgentCreate {
  name: string
  description?: string
  config?: Record<string, unknown>
  is_active?: string
}

export interface AgentUpdate {
  name?: string
  description?: string
  config?: Record<string, unknown>
  is_active?: string
}

export interface AgentResponse extends Agent {}
