import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./Login";
import Dashboard from "./DashBoard";
import ProtectedRoute from "./ProtectedRoute";
import axiosInstance from "./axiosInstance";
import { useEffect } from "react";

import SendMessage from "./SendMessage";
import TemplateList from "./TemplateList";
import CreateTemplate from "./CreateTemplate";
import Reports from "./Reports";

export default function App() {
  // refreshing the token
  const refreshAccessToken = async () => {
    const refresh = localStorage.getItem("refresh");
    if (!refresh) return;

    try {
      const response = await axiosInstance.post("/api/v1/token/refresh/", {
        refresh,
      });

      localStorage.setItem("token", response.data.access_token);
    } catch (error) {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh");
      window.location.href = "/";
    }
  };

  useEffect(() => {
    const hasTokens =
      localStorage.getItem("token") && localStorage.getItem("refresh");
    if (hasTokens) {
      const interval = setInterval(() => {
        refreshAccessToken();
      }, 25 * 60 * 1000);

      return () => clearInterval(interval);
    }
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/api/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        >
          <Route
            index
            element={<h1>Welcome to the WhatsApp API Dashboard</h1>}
          />
          <Route
            path="send-message"
            element={
              <ProtectedRoute>
                <SendMessage />
              </ProtectedRoute>
            }
          />
          <Route
            path="template-list"
            element={
              <ProtectedRoute>
                <TemplateList />
              </ProtectedRoute>
            }
          />
          <Route
            path="create-template"
            element={
              <ProtectedRoute>
                <CreateTemplate />
              </ProtectedRoute>
            }
          />
          <Route
            path="reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </Router>
  );
}
