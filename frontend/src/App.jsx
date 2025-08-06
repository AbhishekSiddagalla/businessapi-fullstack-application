import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./Login";
import Dashboard from "./DashBoard";
import ProtectedRoute from "./ProtectedRoute";
import axiosInstance from "./axiosInstance";
import { useEffect } from "react";

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
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
