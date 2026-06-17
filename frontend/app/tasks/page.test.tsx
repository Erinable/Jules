/**
 * Tasks Page Tests
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import TasksPage from '@/app/tasks/page'
import { taskService } from '@/services'

vi.mock('@/services', () => ({
  taskService: {
    getAll: vi.fn(),
    create: vi.fn(),
    updateStatus: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('TasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    vi.mocked(taskService.getAll).mockResolvedValue([])
    render(<TasksPage />)
    expect(screen.getByText('Tasks')).toBeInTheDocument()
  })

  it('loads and displays tasks', async () => {
    const mockTasks = [
      {
        id: '1',
        project_id: 'proj-1',
        title: 'Test Task',
        status: 'pending' as const,
        priority: 5,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]
    vi.mocked(taskService.getAll).mockResolvedValue(mockTasks)

    render(<TasksPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument()
    })
  })

  it('shows loading spinner while fetching', () => {
    vi.mocked(taskService.getAll).mockImplementation(() => new Promise(() => {}))
    render(<TasksPage />)
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked(taskService.getAll).mockRejectedValue(new Error('API Error'))
    render(<TasksPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load tasks')).toBeInTheDocument()
    })
  })

  it('shows create form when button is clicked', async () => {
    vi.mocked(taskService.getAll).mockResolvedValue([])
    render(<TasksPage />)

    await waitFor(() => {
      expect(screen.queryByText('Create New Task')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Create Task'))
    expect(screen.getByText('Create New Task')).toBeInTheDocument()
  })

  it('creates a new task when form is submitted', async () => {
    vi.mocked(taskService.getAll).mockResolvedValue([])
    vi.mocked(taskService.create).mockResolvedValue({
      id: '1',
      project_id: 'proj-1',
      title: 'New Task',
      status: 'pending',
      priority: 5,
      created_at: '2024-01-01T00:00:00Z',
    })

    render(<TasksPage />)
    await waitFor(() => screen.getByText('Create Task'))

    fireEvent.click(screen.getByText('Create Task'))

    fireEvent.change(screen.getByLabelText('Project ID'), { target: { value: 'proj-1' } })
    fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'New Task' } })
    fireEvent.click(screen.getByText('Create'))

    await waitFor(() => {
      expect(taskService.create).toHaveBeenCalledWith({
        project_id: 'proj-1',
        title: 'New Task',
        description: '',
        priority: 5,
      })
    })
  })

  it('updates task status when dropdown is changed', async () => {
    const mockTasks = [
      {
        id: '1',
        project_id: 'proj-1',
        title: 'Test Task',
        status: 'pending' as const,
        priority: 5,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]
    vi.mocked(taskService.getAll).mockResolvedValue(mockTasks)
    vi.mocked(taskService.updateStatus).mockResolvedValue(mockTasks[0])

    render(<TasksPage />)

    await waitFor(() => screen.getByText('Test Task'))

    const statusSelect = screen.getByDisplayValue('pending')
    fireEvent.change(statusSelect, { target: { value: 'completed' } })

    await waitFor(() => {
      expect(taskService.updateStatus).toHaveBeenCalledWith('1', { status: 'completed' })
    })
  })

  it('deletes a task when delete button is clicked and confirmed', async () => {
    const mockTasks = [
      {
        id: '1',
        project_id: 'proj-1',
        title: 'Test Task',
        status: 'pending' as const,
        priority: 5,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]
    vi.mocked(taskService.getAll).mockResolvedValue(mockTasks)
    vi.mocked(taskService.delete).mockResolvedValue()
    global.confirm = vi.fn(() => true)

    render(<TasksPage />)
    await waitFor(() => screen.getByText('Test Task'))

    fireEvent.click(screen.getByText('Delete'))

    await waitFor(() => {
      expect(taskService.delete).toHaveBeenCalledWith('1')
    })
  })
})
