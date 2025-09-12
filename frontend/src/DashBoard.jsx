// Dashboard.jsx
import { Outlet, useNavigate } from "react-router-dom";
import styles from "./dashboard.module.css";
import axiosInstance from "./axiosInstance";

export default function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const token = localStorage.getItem("token");
    await axiosInstance.post("/logout/", { token });
    localStorage.removeItem("token");
    localStorage.removeItem("refresh");
    navigate("/");
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h3>Dashboard</h3>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          Logout
        </button>
      </header>

      <div className={styles.main}>
        <nav className={styles.sidebar}>
          <ul>
            <li onClick={() => navigate("send-message")}>Send Message</li>
            <li onClick={() => navigate("template-list")}>Templates List</li>
            <li onClick={() => navigate("create-template")}>Create Template</li>
            <li onClick={() => navigate("reports")}>Reports</li>
          </ul>
        </nav>

        <section className={styles.content}>
          <Outlet />
        </section>
      </div>
    </div>
  );
}
