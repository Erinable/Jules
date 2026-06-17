/**
 * Agents Management Page
 */

'use client'

import { useEffect, useState } from 'react'
import { agentService } from '@/services'
import type { Agent, AgentCreate } from '@/types'
import DataTable from '@/components/DataTable'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState<AgentCreate>({
    name: '',
    description: '',
    config: {},
    is_active: 'true',
  })

  const loadAgents = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await agentService.getAll()
      setAgents(data)
    } catch (err) {
      setError('Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAgents()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await agentService.create(formData)
      setShowCreateForm(false)
      setFormData({ name: '', description: '', config: {}, is_active: 'true' })
      loadAgents()
    } catch (err) {
      setError('Failed to create agent')
    }
  }

  const handleToggleActive = async (agentId: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'true' ? 'false' : 'true'
      await agentService.update(agentId, { is_active: newStatus })
      loadAgents()
    } catch (err) {
      setError('Failed to toggle agent status')
    }
  }

  const handleDelete = async (agentId: string) => {
    if (confirm('Are you sure you want to delete this agent?')) {
      try {
        await agentService.delete(agentId)
        loadAgents()
      } catch (err) {
        setError('Failed to delete agent')
      }
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'description', label: 'Description' },
    {
      key: 'is_active',
      label: 'Status',
      render: (agent: Agent) => (
        <button
          onClick={() => handleToggleActive(agent.id, agent.is_active)}
          className={`px-3 py-1 rounded text-white transition-colors ${
            agent.is_active === 'true' ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          {agent.is_active === 'true' ? 'Active' : 'Inactive'}
        </button>
      ),
    },
    {
      key: 'created_at',
      label: 'Created At',
      render: (agent: Agent) => new Date(agent.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (agent: Agent) => (
        <button
          onClick={() => handleDelete(agent.id)}
          className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Agents</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          {showCreateForm ? 'Cancel' : 'Create Agent'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Create New Agent</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Config (JSON)
              </label>
              <textarea
                value={JSON.stringify(formData.config, null, 2)}
                onChange={(e) => {
                  try {
                    setFormData({ ...formData, config: JSON.parse(e.target.value) })
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                rows={5}
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            >
              Create
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="bg-white rounded-lg shadow">
          <DataTable data={agents} columns={columns} />
        </div>
      )}
    </div>
  )
}
