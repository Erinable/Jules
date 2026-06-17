export default function HomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold mb-4">Jules AI 代码生成平台</h1>
      <p className="text-xl mb-8 text-gray-700">生产级代码质量 | Multi-Agent 协作 | 质量优先</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">质量优先</h2>
          <p className="text-gray-600">内置静态分析和复杂度门禁</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">可迭代性</h2>
          <p className="text-gray-600">增量编辑 + Git 集成</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">Multi-Agent</h2>
          <p className="text-gray-600">智能协作工作流</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow mt-8">
        <h2 className="text-2xl font-semibold mb-4">Quick Start</h2>
        <ul className="space-y-2 text-gray-700">
          <li>• Use the sidebar to navigate to different management pages</li>
          <li>• Manage Users, Tasks, and Agents</li>
          <li>• Monitor Executions and Code Quality</li>
          <li>• Check System Health</li>
        </ul>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <p className="text-sm text-gray-700">
          <strong>Backend API:</strong>{' '}
          <a
            href="http://localhost:8000/docs"
            className="text-blue-600 hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            http://localhost:8000/docs
          </a>
        </p>
      </div>
    </div>
  )
}
