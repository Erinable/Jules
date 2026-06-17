/**
 * Quality Metrics Page
 */

'use client'

import { useEffect, useState } from 'react'
import { qualityService } from '@/services'
import type { QualityMetric } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function QualityPage() {
  const [latestMetric, setLatestMetric] = useState<QualityMetric | null>(null)
  const [history, setHistory] = useState<QualityMetric[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [projectId, setProjectId] = useState('')

  const loadLatestMetric = async (projectId: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await qualityService.getLatest(projectId)
      setLatestMetric(data)
    } catch (err) {
      setError('Failed to load quality metric')
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async (projectId: string) => {
    try {
      const data = await qualityService.getHistory(projectId, { limit: 10 })
      setHistory(data)
    } catch (err) {
      setError('Failed to load history')
    }
  }

  const handleLoadMetrics = () => {
    if (projectId) {
      loadLatestMetric(projectId)
      loadHistory(projectId)
    }
  }

  const MetricCard = ({ label, value, color }: { label: string; value: number; color: string }) => (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-sm font-medium text-gray-600 mb-2">{label}</h3>
      <p className={`text-3xl font-bold ${color}`}>{value.toFixed(2)}</p>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Quality Metrics</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-3">Load Metrics by Project</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Project ID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLoadMetrics}
            disabled={!projectId}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Load Metrics
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : latestMetric ? (
        <>
          <div>
            <h2 className="text-2xl font-bold mb-4">Latest Metrics</h2>
            <p className="text-sm text-gray-600 mb-4">
              Measured at: {new Date(latestMetric.measured_at).toLocaleString()}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                label="Avg Complexity"
                value={latestMetric.avg_complexity}
                color="text-blue-600"
              />
              <MetricCard
                label="Maintainability Index"
                value={latestMetric.maintainability_index}
                color="text-green-600"
              />
              <MetricCard
                label="Security Issues"
                value={latestMetric.security_issues}
                color="text-red-600"
              />
              <MetricCard
                label="Test Coverage (%)"
                value={latestMetric.test_coverage}
                color="text-purple-600"
              />
            </div>
          </div>

          {history.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">History</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Complexity</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Maintainability</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Security Issues</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Coverage (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {history.map((metric) => (
                      <tr key={metric.id}>
                        <td className="px-4 py-2 text-sm">{new Date(metric.measured_at).toLocaleDateString()}</td>
                        <td className="px-4 py-2 text-sm">{metric.avg_complexity.toFixed(2)}</td>
                        <td className="px-4 py-2 text-sm">{metric.maintainability_index.toFixed(2)}</td>
                        <td className="px-4 py-2 text-sm">{metric.security_issues}</td>
                        <td className="px-4 py-2 text-sm">{metric.test_coverage.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow text-center text-gray-500">
          Enter a Project ID to load quality metrics
        </div>
      )}
    </div>
  )
}
