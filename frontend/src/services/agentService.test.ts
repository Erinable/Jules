/**
 * Agent Service Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { agentService } from '@/services/agentService'
import apiClient from '@/services/apiClient'

vi.mock('@/services/apiClient')

describe('agentService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAll', () => {
    it('fetches all agents without filter', async () => {
      const mockAgents = [
        { id: '1', name: 'Agent 1', config: {}, is_active: 'true', created_at: '2024-01-01' },
      ]
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAgents })

      const result = await agentService.getAll()

      expect(apiClient.get).toHaveBeenCalledWith('/agents/', { params: {} })
      expect(result).toEqual(mockAgents)
    })

    it('fetches agents with active filter', async () => {
      const mockAgents = []
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAgents })

      await agentService.getAll(true)

      expect(apiClient.get).toHaveBeenCalledWith('/agents/', { params: { is_active: true } })
    })
  })

  describe('getById', () => {
    it('fetches an agent by ID', async () => {
      const mockAgent = { id: '1', name: 'Agent 1', config: {}, is_active: 'true', created_at: '2024-01-01' }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAgent })

      const result = await agentService.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/agents/1')
      expect(result).toEqual(mockAgent)
    })
  })

  describe('create', () => {
    it('creates a new agent', async () => {
      const newAgent = { name: 'New Agent', config: {}, is_active: 'true' }
      const createdAgent = { id: '2', ...newAgent, created_at: '2024-01-01' }
      vi.mocked(apiClient.post).mockResolvedValue({ data: createdAgent })

      const result = await agentService.create(newAgent)

      expect(apiClient.post).toHaveBeenCalledWith('/agents/', newAgent)
      expect(result).toEqual(createdAgent)
    })
  })

  describe('update', () => {
    it('updates an agent', async () => {
      const updateData = { name: 'Updated Agent' }
      const updatedAgent = { id: '1', name: 'Updated Agent', config: {}, is_active: 'true', created_at: '2024-01-01' }
      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedAgent })

      const result = await agentService.update('1', updateData)

      expect(apiClient.put).toHaveBeenCalledWith('/agents/1', updateData)
      expect(result).toEqual(updatedAgent)
    })
  })

  describe('delete', () => {
    it('deletes an agent', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined })

      await agentService.delete('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/agents/1')
    })
  })
})
