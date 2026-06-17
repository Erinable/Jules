/**
 * Health Check API service
 */

import apiClient from './apiClient'
import type { HealthStatus } from '@/types'

export const healthService = {
  /**
   * Get overall health status
   */
  async getHealth(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health')
    return response.data
  },

  /**
   * Get readiness status
   */
  async getReady(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health/ready')
    return response.data
  },

  /**
   * Get liveness status
   */
  async getLive(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health/live')
    return response.data
  },
}
