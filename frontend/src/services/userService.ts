/**
 * User API service
 */

import apiClient from './apiClient'
import type { User, UserCreate, UserUpdate, UserResponse } from '@/types'

export const userService = {
  /**
   * Get all users
   */
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users/')
    return response.data
  },

  /**
   * Get user by ID
   */
  async getById(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${userId}`)
    return response.data
  },

  /**
   * Create new user
   */
  async create(user: UserCreate): Promise<UserResponse> {
    const response = await apiClient.post<UserResponse>('/users/', user)
    return response.data
  },

  /**
   * Update user
   */
  async update(userId: string, user: UserUpdate): Promise<UserResponse> {
    const response = await apiClient.put<UserResponse>(`/users/${userId}`, user)
    return response.data
  },

  /**
   * Delete user
   */
  async delete(userId: string): Promise<void> {
    await apiClient.delete(`/users/${userId}`)
  },
}
