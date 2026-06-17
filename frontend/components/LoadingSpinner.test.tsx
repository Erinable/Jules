/**
 * LoadingSpinner Component Tests
 */

import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner from '@/components/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders the spinner', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('renders with default medium size', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.w-8')
    expect(spinner).toBeInTheDocument()
  })

  it('renders with small size', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    const spinner = container.querySelector('.w-4')
    expect(spinner).toBeInTheDocument()
  })

  it('renders with large size', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.w-12')
    expect(spinner).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<LoadingSpinner className="custom-class" />)
    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('has blue border color', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.border-blue-600')
    expect(spinner).toBeInTheDocument()
  })

  it('has transparent top border', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.border-t-transparent')
    expect(spinner).toBeInTheDocument()
  })
})
