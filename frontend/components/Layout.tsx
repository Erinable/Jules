/**
 * Main Layout component with navigation
 */

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/users', label: 'Users' },
  { href: '/tasks', label: 'Tasks' },
  { href: '/agents', label: 'Agents' },
  { href: '/executions', label: 'Executions' },
  { href: '/code-files', label: 'Code Files' },
  { href: '/quality', label: 'Quality' },
  { href: '/health', label: 'Health' },
]

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Jules AI Platform</h1>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 border-r bg-gray-50 p-4">
          <nav className="space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'block px-4 py-2 rounded-md transition-colors',
                  pathname === item.href
                    ? 'bg-blue-100 text-blue-900 font-medium'
                    : 'text-gray-700 hover:bg-gray-200'
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 bg-gray-100">
          <div className="container mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          Jules AI Platform © 2024 | Backend API: <a href="http://localhost:8000/docs" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">API Docs</a>
        </div>
      </footer>
    </div>
  )
}
