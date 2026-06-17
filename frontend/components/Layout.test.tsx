/**
 * Layout Component Tests
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Layout from '@/components/Layout'

describe('Layout', () => {
  it('renders the header with title', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    expect(screen.getByText('Jules AI Platform')).toBeInTheDocument()
  })

  it('renders all navigation items', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Agents')).toBeInTheDocument()
    expect(screen.getByText('Executions')).toBeInTheDocument()
    expect(screen.getByText('Code Files')).toBeInTheDocument()
    expect(screen.getByText('Quality')).toBeInTheDocument()
    expect(screen.getByText('Health')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(
      <Layout>
        <div data-testid="test-content">Test content</div>
      </Layout>
    )

    expect(screen.getByTestId('test-content')).toBeInTheDocument()
  })

  it('renders footer', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    expect(screen.getByText(/Jules AI Platform © 2024/)).toBeInTheDocument()
  })

  it('renders API docs link in footer', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    const apiLink = screen.getByText('API Docs')
    expect(apiLink).toHaveAttribute('href', 'http://localhost:8000/docs')
    expect(apiLink).toHaveAttribute('target', '_blank')
  })

  it('highlights active navigation item', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    // Home should be highlighted (pathname is '/')
    const homeLink = screen.getByText('Home').closest('a')
    expect(homeLink).toHaveClass('bg-blue-100')
  })

  it('applies correct navigation link styles', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    const homeLink = screen.getByText('Home').closest('a')
    expect(homeLink).toHaveClass('block', 'px-4', 'py-2', 'rounded-md')
  })

  it('renders sidebar with gray background', () => {
    const { container } = render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    const sidebar = container.querySelector('aside')
    expect(sidebar).toHaveClass('bg-gray-50')
  })

  it('renders main content area with gray background', () => {
    const { container } = render(
      <Layout>
        <div>Test content</div>
      </Layout>
    )

    const main = container.querySelector('main')
    expect(main).toHaveClass('bg-gray-100')
  })
})
