import React, { useEffect, useState } from "react";
import "./status.css";

const StatusDashboard = () => {
  const [status, setStatus] = useState({});

  useEffect(() => {
    fetch("http://localhost:5050/")
      .then((res) => res.text())
      .then((html) => {
        const matches = Array.from(html.matchAll(/<li><strong>(.*?)<\/strong>: (.*?)<\/li>/g));
        const statusObj = {};
        matches.forEach(([, server, state]) => {
          statusObj[server] = state;
        });
        setStatus(statusObj);
      });
  }, []);

  return (
    <div className="status-dashboard-container">
      <h2 className="status-title">🖥️ Backend Server Status</h2>
      <ul className="status-list">
        {Object.entries(status).map(([name, stat], idx) => (
          <li key={idx} className="status-item">
            <strong>{name}</strong>: {stat}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StatusDashboard;
