/**
 * Execution API service
 */

import apiClient from './apiClient'
import type { Execution, ExecutionCreate, ExecutionStatusUpdate, ExecutionResponse } from '@/types'

export const executionService = {
  /**
   * Get all executions with optional task filter
   */
  async getAll(taskId?: string): Promise<Execution[]> {
    const params = taskId ? { task_id: taskId } : {}
    const response = await apiClient.get<Execution[]>('/executions/', { params })
    return response.data
  },

  /**
   * Get execution by ID
   */
  async getById(executionId: string): Promise<Execution> {
    const response = await apiClient.get<Execution>(`/executions/${executionId}`)
    return response.data
  },

  /**
   * Create new execution
   */
  async create(execution: ExecutionCreate): Promise<ExecutionResponse> {
    const response = await apiClient.post<ExecutionResponse>('/executions/', execution)
    return response.data
  },

  /**
   * Update execution status
   */
  async updateStatus(executionId: string, status: ExecutionStatusUpdate): Promise<ExecutionResponse> {
    const response = await apiClient.patch<ExecutionResponse>(`/executions/${executionId}/status`, status)
    return response.data
  },

  /**
   * Delete execution
   */
  async delete(executionId: string): Promise<void> {
    await apiClient.delete(`/executions/${executionId}`)
  },
}
