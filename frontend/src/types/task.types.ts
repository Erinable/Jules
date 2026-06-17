/**
 * Task type definitions based on backend Pydantic schemas
 */

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export interface Task {
  id: string
  project_id: string
  title: string
  description?: string
  status: TaskStatus
  priority: number
  created_at: string
  updated_at?: string
}

export interface TaskCreate {
  project_id: string
  title: string
  description?: string
  status?: TaskStatus
  priority?: number
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: number
}

export interface TaskStatusUpdate {
  status: TaskStatus
}

export interface TaskResponse extends Task {}
