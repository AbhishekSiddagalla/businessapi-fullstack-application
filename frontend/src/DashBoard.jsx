import { useState } from "react";
import { useNavigate } from "react-router-dom";

import styles from "./dashboard.module.css";

import SendMessage from "./SendMessage";
import TemplateList from "./TemplateList";
import CreateTemplate from "./CreateTemplate";
import Reports from "./Reports";
import axiosInstance from "./axiosInstance";

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState("home");

  const sections = {
    "send-message": <SendMessage />,
    "template-list": <TemplateList />,
    "create-template": <CreateTemplate />,
    reports: <Reports />,
  };

  const renderSection = sections[activeSection] || (
    <h1>Welcome to the WhatsApp API Dashboard</h1>
  );

  const handleLogout = async () => {
    const token = localStorage.getItem("token");
    const refresh = localStorage.getItem("refresh");

    const response = await axiosInstance.post("/logout/", {
      token,
    });

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
            <li onClick={() => setActiveSection("send-message")}>
              Send Message
            </li>
            <li onClick={() => setActiveSection("template-list")}>
              Templates List
            </li>
            <li onClick={() => setActiveSection("create-template")}>
              Create Template
            </li>
            <li onClick={() => setActiveSection("reports")}>Reports</li>
          </ul>
        </nav>

        <section className={styles.content}>{renderSection}</section>
      </div>
    </div>
  );
}
