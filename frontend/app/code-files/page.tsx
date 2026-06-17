/**
 * Code Files Management Page
 */

'use client'

import { useEffect, useState } from 'react'
import { codeFileService } from '@/services'
import type { CodeFile } from '@/types'
import DataTable from '@/components/DataTable'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function CodeFilesPage() {
  const [codeFiles, setCodeFiles] = useState<CodeFile[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [projectId, setProjectId] = useState('')
  const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null)

  const loadCodeFiles = async (projectId: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await codeFileService.getByProject(projectId)
      setCodeFiles(data)
    } catch (err) {
      setError('Failed to load code files')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadFiles = () => {
    if (projectId) {
      loadCodeFiles(projectId)
    }
  }

  const handleViewFile = (file: CodeFile) => {
    setSelectedFile(file)
  }

  const columns = [
    { key: 'path', label: 'Path' },
    {
      key: 'hash',
      label: 'Hash',
      render: (file: CodeFile) => (
        <span className="font-mono text-xs">{file.hash.substring(0, 8)}</span>
      ),
    },
    {
      key: 'updated_at',
      label: 'Updated At',
      render: (file: CodeFile) => new Date(file.updated_at).toLocaleString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (file: CodeFile) => (
        <button
          onClick={() => handleViewFile(file)}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          View
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Code Files</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-3">Load Files by Project</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Project ID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLoadFiles}
            disabled={!projectId}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Load Files
          </button>
        </div>
      </div>

      {selectedFile && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-xl font-semibold">{selectedFile.path}</h2>
              <p className="text-sm text-gray-600 font-mono mt-1">Hash: {selectedFile.hash}</p>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
          <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-96 text-sm">
            <code>{selectedFile.content}</code>
          </pre>
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : codeFiles.length > 0 ? (
        <div className="bg-white rounded-lg shadow">
          <DataTable data={codeFiles} columns={columns} />
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow text-center text-gray-500">
          Enter a Project ID to load code files
        </div>
      )}
    </div>
  )
}
