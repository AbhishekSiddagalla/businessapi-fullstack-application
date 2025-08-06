import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import axiosInstance from "./axiosInstance";

export default function ProtectedRoute({ children }) {
  const [isValid, setIsValid] = useState(null);

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setIsValid(false);
        return;
      }

      try {
        await axiosInstance.get("api/v1/menu/validate-token/");
        setIsValid(true);
      } catch (error) {
        localStorage.removeItem("token");
        localStorage.removeItem("refresh");
        setIsValid(false);
      }
    };

    validateToken();
  }, []);

  if (isValid === null) {
    return <div>loading...</div>;
  }

  if (!isValid) {
    return <Navigate to="/" replace />;
  }
  return children;
}
