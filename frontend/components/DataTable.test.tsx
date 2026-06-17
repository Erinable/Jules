/**
 * DataTable Component Tests
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import DataTable from '@/components/DataTable'

interface TestData {
  id: string
  name: string
  age: number
}

describe('DataTable', () => {
  const mockData: TestData[] = [
    { id: '1', name: 'Alice', age: 30 },
    { id: '2', name: 'Bob', age: 25 },
  ]

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'age', label: 'Age' },
  ]

  it('renders table with data', () => {
    render(<DataTable data={mockData} columns={columns} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Age')).toBeInTheDocument()
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
    expect(screen.getByText('30')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
  })

  it('renders custom cell content with render function', () => {
    const customColumns = [
      {
        key: 'name',
        label: 'Name',
        render: (item: TestData) => <strong>{item.name.toUpperCase()}</strong>,
      },
    ]

    render(<DataTable data={mockData} columns={customColumns} />)

    expect(screen.getByText('ALICE')).toBeInTheDocument()
    expect(screen.getByText('BOB')).toBeInTheDocument()
  })

  it('displays loading spinner when loading is true', () => {
    render(<DataTable data={[]} columns={columns} loading={true} />)

    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays empty message when no data', () => {
    render(<DataTable data={[]} columns={columns} emptyMessage="No items found" />)

    expect(screen.getByText('No items found')).toBeInTheDocument()
  })

  it('calls onRowClick when row is clicked', () => {
    const handleRowClick = vi.fn()

    render(<DataTable data={mockData} columns={columns} onRowClick={handleRowClick} />)

    const rows = screen.getAllByRole('row')
    fireEvent.click(rows[1]) // Click first data row (skip header)

    expect(handleRowClick).toHaveBeenCalledWith(mockData[0])
  })

  it('applies cursor-pointer class when onRowClick is provided', () => {
    const handleRowClick = vi.fn()

    render(<DataTable data={mockData} columns={columns} onRowClick={handleRowClick} />)

    const rows = screen.getAllByRole('row')
    expect(rows[1]).toHaveClass('cursor-pointer')
  })

  it('does not apply cursor-pointer class when onRowClick is not provided', () => {
    render(<DataTable data={mockData} columns={columns} />)

    const rows = screen.getAllByRole('row')
    expect(rows[1]).not.toHaveClass('cursor-pointer')
  })

  it('applies custom className', () => {
    const { container } = render(
      <DataTable data={mockData} columns={columns} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })
})
