/**
 * Health Page Tests
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import HealthPage from '@/app/health/page'
import { healthService } from '@/services'

vi.mock('@/services', () => ({
  healthService: {
    getHealth: vi.fn(),
    getReady: vi.fn(),
    getLive: vi.fn(),
  },
}))

describe('HealthPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders the page title', () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({ status: 'healthy' })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)
    expect(screen.getByText('System Health')).toBeInTheDocument()
  })

  it('loads health status on mount', async () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({ status: 'healthy' })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByText('healthy')).toBeInTheDocument()
      expect(screen.getAllByText('ok')).toHaveLength(2)
    })
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked(healthService.getHealth).mockRejectedValue(new Error('API Error'))
    vi.mocked(healthService.getReady).mockRejectedValue(new Error('API Error'))
    vi.mocked(healthService.getLive).mockRejectedValue(new Error('API Error'))

    render(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load health status')).toBeInTheDocument()
    })
  })

  it('refreshes health status when refresh button is clicked', async () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({ status: 'healthy' })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)

    await waitFor(() => screen.getByText('healthy'))

    fireEvent.click(screen.getByText('Refresh'))

    await waitFor(() => {
      expect(healthService.getHealth).toHaveBeenCalledTimes(2)
    })
  })

  it('auto-refreshes every 10 seconds', async () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({ status: 'healthy' })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)

    await waitFor(() => screen.getByText('healthy'))

    expect(healthService.getHealth).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(10000)

    await waitFor(() => {
      expect(healthService.getHealth).toHaveBeenCalledTimes(2)
    })
  })

  it('displays database status when available', async () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({
      status: 'healthy',
      database: 'connected',
    })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)

    await waitFor(() => {
      expect(screen.getByText('connected')).toBeInTheDocument()
    })
  })

  it('shows loading spinner while fetching', () => {
    vi.mocked(healthService.getHealth).mockImplementation(() => new Promise(() => {}))
    vi.mocked(healthService.getReady).mockImplementation(() => new Promise(() => {}))
    vi.mocked(healthService.getLive).mockImplementation(() => new Promise(() => {}))

    render(<HealthPage />)

    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays green indicator for healthy status', async () => {
    vi.mocked(healthService.getHealth).mockResolvedValue({ status: 'healthy' })
    vi.mocked(healthService.getReady).mockResolvedValue({ status: 'ok' })
    vi.mocked(healthService.getLive).mockResolvedValue({ status: 'ok' })

    render(<HealthPage />)

    await waitFor(() => {
      const indicators = document.querySelectorAll('.bg-green-500')
      expect(indicators.length).toBeGreaterThan(0)
    })
  })
})
