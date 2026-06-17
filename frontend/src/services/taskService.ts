/**
 * Task API service
 */

import apiClient from './apiClient'
import type { Task, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse } from '@/types'

export const taskService = {
  /**
   * Get all tasks with optional filters
   */
  async getAll(filters?: { status?: string; priority?: number }): Promise<Task[]> {
    const response = await apiClient.get<Task[]>('/tasks/', { params: filters })
    return response.data
  },

  /**
   * Get task by ID
   */
  async getById(taskId: string): Promise<Task> {
    const response = await apiClient.get<Task>(`/tasks/${taskId}`)
    return response.data
  },

  /**
   * Create new task
   */
  async create(task: TaskCreate): Promise<TaskResponse> {
    const response = await apiClient.post<TaskResponse>('/tasks/', task)
    return response.data
  },

  /**
   * Update task
   */
  async update(taskId: string, task: TaskUpdate): Promise<TaskResponse> {
    const response = await apiClient.put<TaskResponse>(`/tasks/${taskId}`, task)
    return response.data
  },

  /**
   * Update task status
   */
  async updateStatus(taskId: string, status: TaskStatusUpdate): Promise<TaskResponse> {
    const response = await apiClient.patch<TaskResponse>(`/tasks/${taskId}/status`, status)
    return response.data
  },

  /**
   * Delete task
   */
  async delete(taskId: string): Promise<void> {
    await apiClient.delete(`/tasks/${taskId}`)
  },
}
