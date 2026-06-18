/**
 * Executions Management Page
 */

"use client";

import { useEffect, useState } from "react";
import { executionService } from "@/services";
import type { Execution } from "@/types";
import DataTable from "@/components/DataTable";
import LoadingSpinner from "@/components/LoadingSpinner";

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterTaskId, setFilterTaskId] = useState("");

  const loadExecutions = async (taskId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await executionService.getAll(taskId);
      setExecutions(data);
    } catch (err) {
      setError("Failed to load executions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExecutions();
  }, []);

  const handleFilter = () => {
    loadExecutions(filterTaskId || undefined);
  };

  const handleClearFilter = () => {
    setFilterTaskId("");
    loadExecutions();
  };

  const columns = [
    { key: "agent_type", label: "Agent Type" },
    {
      key: "status",
      label: "Status",
      render: (execution: Execution) => {
        const statusColors = {
          pending: "bg-yellow-100 text-yellow-800",
          running: "bg-blue-100 text-blue-800",
          completed: "bg-green-100 text-green-800",
          failed: "bg-red-100 text-red-800",
        };
        return (
          <span
            className={`px-2 py-1 rounded text-sm font-medium ${statusColors[execution.status]}`}
          >
            {execution.status}
          </span>
        );
      },
    },
    {
      key: "task_id",
      label: "Task ID",
      render: (execution: Execution) => (
        <span className="font-mono text-xs">
          {execution.task_id.substring(0, 8)}
        </span>
      ),
    },
    {
      key: "started_at",
      label: "Started At",
      render: (execution: Execution) =>
        new Date(execution.started_at).toLocaleString(),
    },
    {
      key: "completed_at",
      label: "Completed At",
      render: (execution: Execution) =>
        execution.completed_at
          ? new Date(execution.completed_at).toLocaleString()
          : "-",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Executions</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-3">Filter Executions</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Task ID"
            value={filterTaskId}
            onChange={(e) => setFilterTaskId(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleFilter}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Filter
          </button>
          <button
            onClick={handleClearFilter}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="bg-white rounded-lg shadow">
          <DataTable data={executions} columns={columns} />
        </div>
      )}
    </div>
  );
}
