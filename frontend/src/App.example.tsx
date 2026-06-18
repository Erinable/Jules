/**
 * App Component - Main Application Entry Point
 *
 * Sets up routing and authentication context.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

// Pages
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProgressDemoPage from "@/pages/ProgressDemoPage";
import ProgressPhase2DemoPage from "@/pages/ProgressPhase2DemoPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/progress-demo"
            element={
              <ProtectedRoute>
                <ProgressDemoPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/progress-phase2-demo"
            element={
              <ProtectedRoute>
                <ProgressPhase2DemoPage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
