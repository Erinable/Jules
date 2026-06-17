/**
 * Executions Page Tests
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ExecutionsPage from '@/app/executions/page'
import { executionService } from '@/services'

vi.mock('@/services', () => ({
  executionService: {
    getAll: vi.fn(),
  },
}))

describe('ExecutionsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    vi.mocked(executionService.getAll).mockResolvedValue([])
    render(<ExecutionsPage />)
    expect(screen.getByText('Executions')).toBeInTheDocument()
  })

  it('loads and displays executions', async () => {
    const mockExecutions = [
      {
        id: '1',
        task_id: 'task-123',
        agent_type: 'test-agent',
        status: 'completed' as const,
        started_at: '2024-01-01T00:00:00Z',
      },
    ]
    vi.mocked(executionService.getAll).mockResolvedValue(mockExecutions)

    render(<ExecutionsPage />)

    await waitFor(() => {
      expect(screen.getByText('test-agent')).toBeInTheDocument()
      expect(screen.getByText('completed')).toBeInTheDocument()
    })
  })

  it('shows loading spinner while fetching', () => {
    vi.mocked(executionService.getAll).mockImplementation(() => new Promise(() => {}))
    render(<ExecutionsPage />)
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked(executionService.getAll).mockRejectedValue(new Error('API Error'))
    render(<ExecutionsPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load executions')).toBeInTheDocument()
    })
  })

  it('filters executions by task ID', async () => {
    vi.mocked(executionService.getAll).mockResolvedValue([])
    render(<ExecutionsPage />)

    await waitFor(() => screen.getByPlaceholderText('Task ID'))

    fireEvent.change(screen.getByPlaceholderText('Task ID'), {
      target: { value: 'task-123' },
    })
    fireEvent.click(screen.getByText('Filter'))

    await waitFor(() => {
      expect(executionService.getAll).toHaveBeenCalledWith('task-123')
    })
  })

  it('clears filter when clear button is clicked', async () => {
    vi.mocked(executionService.getAll).mockResolvedValue([])
    render(<ExecutionsPage />)

    await waitFor(() => screen.getByPlaceholderText('Task ID'))

    fireEvent.change(screen.getByPlaceholderText('Task ID'), {
      target: { value: 'task-123' },
    })
    fireEvent.click(screen.getByText('Clear'))

    await waitFor(() => {
      expect(executionService.getAll).toHaveBeenCalledWith(undefined)
    })
  })

  it('displays execution status with correct styling', async () => {
    const mockExecutions = [
      {
        id: '1',
        task_id: 'task-1',
        agent_type: 'test',
        status: 'running' as const,
        started_at: '2024-01-01T00:00:00Z',
      },
    ]
    vi.mocked(executionService.getAll).mockResolvedValue(mockExecutions)

    render(<ExecutionsPage />)

    await waitFor(() => {
      const statusElement = screen.getByText('running')
      expect(statusElement).toHaveClass('bg-blue-100')
    })
  })
})
