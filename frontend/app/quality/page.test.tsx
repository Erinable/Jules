/**
 * Quality Page Tests
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import QualityPage from '@/app/quality/page'
import { qualityService } from '@/services'

vi.mock('@/services', () => ({
  qualityService: {
    getLatest: vi.fn(),
    getHistory: vi.fn(),
  },
}))

describe('QualityPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    render(<QualityPage />)
    expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
  })

  it('loads quality metrics when project ID is submitted', async () => {
    const mockMetric = {
      id: '1',
      project_id: 'proj-1',
      avg_complexity: 5.2,
      maintainability_index: 85.5,
      security_issues: 2,
      test_coverage: 92.3,
      measured_at: '2024-01-01T00:00:00Z',
    }
    vi.mocked(qualityService.getLatest).mockResolvedValue(mockMetric)
    vi.mocked(qualityService.getHistory).mockResolvedValue([])

    render(<QualityPage />)

    fireEvent.change(screen.getByPlaceholderText('Project ID'), {
      target: { value: 'proj-1' },
    })
    fireEvent.click(screen.getByText('Load Metrics'))

    await waitFor(() => {
      expect(screen.getByText('5.20')).toBeInTheDocument()
      expect(screen.getByText('85.50')).toBeInTheDocument()
      expect(screen.getByText('2.00')).toBeInTheDocument()
      expect(screen.getByText('92.30')).toBeInTheDocument()
    })
  })

  it('displays quality history table', async () => {
    const mockMetric = {
      id: '1',
      project_id: 'proj-1',
      avg_complexity: 5.2,
      maintainability_index: 85.5,
      security_issues: 2,
      test_coverage: 92.3,
      measured_at: '2024-01-01T00:00:00Z',
    }
    const mockHistory = [
      {
        id: '2',
        project_id: 'proj-1',
        avg_complexity: 4.8,
        maintainability_index: 87.0,
        security_issues: 1,
        test_coverage: 90.0,
        measured_at: '2024-01-02T00:00:00Z',
      },
    ]
    vi.mocked(qualityService.getLatest).mockResolvedValue(mockMetric)
    vi.mocked(qualityService.getHistory).mockResolvedValue(mockHistory)

    render(<QualityPage />)

    fireEvent.change(screen.getByPlaceholderText('Project ID'), {
      target: { value: 'proj-1' },
    })
    fireEvent.click(screen.getByText('Load Metrics'))

    await waitFor(() => {
      expect(screen.getByText('History')).toBeInTheDocument()
    })
  })

  it('disables load button when project ID is empty', () => {
    render(<QualityPage />)
    expect(screen.getByText('Load Metrics')).toBeDisabled()
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked(qualityService.getLatest).mockRejectedValue(new Error('API Error'))

    render(<QualityPage />)

    fireEvent.change(screen.getByPlaceholderText('Project ID'), {
      target: { value: 'proj-1' },
    })
    fireEvent.click(screen.getByText('Load Metrics'))

    await waitFor(() => {
      expect(screen.getByText('Failed to load quality metric')).toBeInTheDocument()
    })
  })

  it('shows loading spinner while fetching', () => {
    vi.mocked(qualityService.getLatest).mockImplementation(() => new Promise(() => {}))
    vi.mocked(qualityService.getHistory).mockResolvedValue([])

    render(<QualityPage />)

    fireEvent.change(screen.getByPlaceholderText('Project ID'), {
      target: { value: 'proj-1' },
    })
    fireEvent.click(screen.getByText('Load Metrics'))

    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })
})
