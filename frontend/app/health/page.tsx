/**
 * Health Check Page
 */

'use client'

import { useEffect, useState } from 'react'
import { healthService } from '@/services'
import type { HealthStatus } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [ready, setReady] = useState<HealthStatus | null>(null)
  const [live, setLive] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadHealth = async () => {
    try {
      setLoading(true)
      setError(null)
      const [healthData, readyData, liveData] = await Promise.all([
        healthService.getHealth(),
        healthService.getReady(),
        healthService.getLive(),
      ])
      setHealth(healthData)
      setReady(readyData)
      setLive(liveData)
    } catch (err) {
      setError('Failed to load health status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
    // Refresh every 10 seconds
    const interval = setInterval(loadHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  const StatusCard = ({ title, status }: { title: string; status: HealthStatus | null }) => {
    const isHealthy = status?.status === 'healthy' || status?.status === 'ok'
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-3">{title}</h3>
        {status ? (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className={`text-xl font-bold ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
                {status.status}
              </span>
            </div>
            {status.database && (
              <p className="text-sm text-gray-600">
                Database: <span className="font-medium">{status.database}</span>
              </p>
            )}
            {status.timestamp && (
              <p className="text-sm text-gray-600">
                Timestamp: <span className="font-medium">{new Date(status.timestamp).toLocaleString()}</span>
              </p>
            )}
          </div>
        ) : (
          <p className="text-gray-500">No data</p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">System Health</h1>
        <button
          onClick={loadHealth}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {loading && !health ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatusCard title="Overall Health" status={health} />
            <StatusCard title="Readiness" status={ready} />
            <StatusCard title="Liveness" status={live} />
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">API Connection</h2>
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-medium">Backend URL:</span>{' '}
                <a
                  href={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}
                </a>
              </p>
              <p className="text-sm">
                <span className="font-medium">API Docs:</span>{' '}
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  http://localhost:8000/docs
                </a>
              </p>
              <p className="text-sm text-gray-600">Auto-refresh: Every 10 seconds</p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
