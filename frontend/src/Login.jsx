import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import styles from "./login.module.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/token/", {
        username,
        password,
      });
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("refresh", response.data.refresh);

      navigate("/dashboard");
    } catch (error) {
      setError("Invalid Username or Password");
    }
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginBox}>
        <form onSubmit={handleSubmit}>
          <h2>WhatsApp Business API</h2>
          {error && <p style={{ color: "red" }}>{error}</p>}
          <label>Username:</label>
          <input type="text" onChange={(e) => setUsername(e.target.value)} />
          <br />
          <br />
          <label>Password:</label>
          <input
            type="password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <br />
          <br />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}
