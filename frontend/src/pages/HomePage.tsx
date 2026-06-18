/**
 * HomePage Component
 *
 * Protected home page showing user info and navigation.
 */

import { useAuth } from "@/hooks/useAuth";
import { Link } from "react-router-dom";

export default function HomePage() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Jules</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {user?.name} ({user?.role})
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                退出登录
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            欢迎回来！
          </h2>

          {/* User info */}
          <div className="space-y-3 mb-6">
            <div>
              <span className="text-sm text-gray-500">用户 ID:</span>
              <p className="font-mono text-sm text-gray-900">{user?.id}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">邮箱:</span>
              <p className="text-sm text-gray-900">{user?.email}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">角色:</span>
              <p className="text-sm text-gray-900">{user?.role}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">账户状态:</span>
              <p className="text-sm text-gray-900">
                {user?.isActive ? (
                  <span className="text-green-600">✓ 活跃</span>
                ) : (
                  <span className="text-red-600">✗ 未激活</span>
                )}
              </p>
            </div>
          </div>

          {/* Navigation links */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">功能导航</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <Link
                to="/progress-demo"
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <h4 className="font-medium text-gray-900">进度追踪 Demo</h4>
                <p className="text-sm text-gray-600 mt-1">
                  查看进度追踪组件演示
                </p>
              </Link>

              <Link
                to="/progress-phase2-demo"
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <h4 className="font-medium text-gray-900">进度追踪 Phase 2</h4>
                <p className="text-sm text-gray-600 mt-1">查看高级组件演示</p>
              </Link>

              <div className="p-4 border border-gray-200 rounded-lg bg-gray-50 opacity-50">
                <h4 className="font-medium text-gray-900">任务管理</h4>
                <p className="text-sm text-gray-600 mt-1">即将推出</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
