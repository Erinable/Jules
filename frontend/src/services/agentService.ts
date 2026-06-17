/**
 * Agent API service
 */

import apiClient from './apiClient'
import type { Agent, AgentCreate, AgentUpdate, AgentResponse } from '@/types'

export const agentService = {
  /**
   * Get all agents with optional active filter
   */
  async getAll(isActive?: boolean): Promise<Agent[]> {
    const params = isActive !== undefined ? { is_active: isActive } : {}
    const response = await apiClient.get<Agent[]>('/agents/', { params })
    return response.data
  },

  /**
   * Get agent by ID
   */
  async getById(agentId: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(`/agents/${agentId}`)
    return response.data
  },

  /**
   * Create new agent
   */
  async create(agent: AgentCreate): Promise<AgentResponse> {
    const response = await apiClient.post<AgentResponse>('/agents/', agent)
    return response.data
  },

  /**
   * Update agent
   */
  async update(agentId: string, agent: AgentUpdate): Promise<AgentResponse> {
    const response = await apiClient.put<AgentResponse>(`/agents/${agentId}`, agent)
    return response.data
  },

  /**
   * Delete agent
   */
  async delete(agentId: string): Promise<void> {
    await apiClient.delete(`/agents/${agentId}`)
  },
}
