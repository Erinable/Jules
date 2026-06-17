/**
 * User Service Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { userService } from '@/services/userService'
import apiClient from '@/services/apiClient'

vi.mock('@/services/apiClient')

describe('userService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAll', () => {
    it('fetches all users', async () => {
      const mockUsers = [
        { id: '1', email: 'test@example.com', name: 'Test User', created_at: '2024-01-01' },
      ]
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockUsers })

      const result = await userService.getAll()

      expect(apiClient.get).toHaveBeenCalledWith('/users/')
      expect(result).toEqual(mockUsers)
    })
  })

  describe('getById', () => {
    it('fetches a user by ID', async () => {
      const mockUser = { id: '1', email: 'test@example.com', name: 'Test User', created_at: '2024-01-01' }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockUser })

      const result = await userService.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/users/1')
      expect(result).toEqual(mockUser)
    })
  })

  describe('create', () => {
    it('creates a new user', async () => {
      const newUser = { email: 'new@example.com', name: 'New User' }
      const createdUser = { id: '2', ...newUser, created_at: '2024-01-01' }
      vi.mocked(apiClient.post).mockResolvedValue({ data: createdUser })

      const result = await userService.create(newUser)

      expect(apiClient.post).toHaveBeenCalledWith('/users/', newUser)
      expect(result).toEqual(createdUser)
    })
  })

  describe('update', () => {
    it('updates a user', async () => {
      const updateData = { name: 'Updated Name' }
      const updatedUser = { id: '1', email: 'test@example.com', name: 'Updated Name', created_at: '2024-01-01' }
      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedUser })

      const result = await userService.update('1', updateData)

      expect(apiClient.put).toHaveBeenCalledWith('/users/1', updateData)
      expect(result).toEqual(updatedUser)
    })
  })

  describe('delete', () => {
    it('deletes a user', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined })

      await userService.delete('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/users/1')
    })
  })
})
