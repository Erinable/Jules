/**
 * Users Page Tests
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import UsersPage from '@/app/users/page'
import { userService } from '@/services'

// Mock the userService
vi.mock('@/services', () => ({
  userService: {
    getAll: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('UsersPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    vi.mocked(userService.getAll).mockResolvedValue([])

    render(<UsersPage />)

    expect(screen.getByText('Users')).toBeInTheDocument()
  })

  it('loads and displays users', async () => {
    const mockUsers = [
      {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      },
    ]

    vi.mocked(userService.getAll).mockResolvedValue(mockUsers)

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
      expect(screen.getByText('Test User')).toBeInTheDocument()
    })
  })

  it('shows loading spinner while fetching', () => {
    vi.mocked(userService.getAll).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<UsersPage />)

    // LoadingSpinner should be visible
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked(userService.getAll).mockRejectedValue(new Error('API Error'))

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load users')).toBeInTheDocument()
    })
  })

  it('shows create form when button is clicked', async () => {
    vi.mocked(userService.getAll).mockResolvedValue([])

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.queryByText('Create New User')).not.toBeInTheDocument()
    })

    const createButton = screen.getByText('Create User')
    fireEvent.click(createButton)

    expect(screen.getByText('Create New User')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Name')).toBeInTheDocument()
  })

  it('creates a new user when form is submitted', async () => {
    const mockUsers = []
    vi.mocked(userService.getAll).mockResolvedValue(mockUsers)
    vi.mocked(userService.create).mockResolvedValue({
      id: '1',
      email: 'new@example.com',
      name: 'New User',
      created_at: '2024-01-01T00:00:00Z',
    })

    render(<UsersPage />)

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Create User')).toBeInTheDocument()
    })

    // Open form
    fireEvent.click(screen.getByText('Create User'))

    // Fill form
    const emailInput = screen.getByLabelText('Email')
    const nameInput = screen.getByLabelText('Name')

    fireEvent.change(emailInput, { target: { value: 'new@example.com' } })
    fireEvent.change(nameInput, { target: { value: 'New User' } })

    // Submit form
    const submitButton = screen.getByText('Create')
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(userService.create).toHaveBeenCalledWith({
        email: 'new@example.com',
        name: 'New User',
      })
      expect(userService.getAll).toHaveBeenCalledTimes(2) // Initial + after create
    })
  })

  it('deletes a user when delete button is clicked and confirmed', async () => {
    const mockUsers = [
      {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      },
    ]

    vi.mocked(userService.getAll).mockResolvedValue(mockUsers)
    vi.mocked(userService.delete).mockResolvedValue()

    // Mock window.confirm
    global.confirm = vi.fn(() => true)

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this user?')

    await waitFor(() => {
      expect(userService.delete).toHaveBeenCalledWith('1')
      expect(userService.getAll).toHaveBeenCalledTimes(2) // Initial + after delete
    })
  })

  it('does not delete user when confirmation is cancelled', async () => {
    const mockUsers = [
      {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      },
    ]

    vi.mocked(userService.getAll).mockResolvedValue(mockUsers)

    // Mock window.confirm to return false
    global.confirm = vi.fn(() => false)

    render(<UsersPage />)

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    expect(global.confirm).toHaveBeenCalled()
    expect(userService.delete).not.toHaveBeenCalled()
  })
})
