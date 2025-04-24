import React, { useState } from "react";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from "chart.js";
import "./simulation.css";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

function SimulatorPage() {
  const [algorithm, setAlgorithm] = useState("round_robin");
  const [logs, setLogs] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [method, setMethod] = useState("nginx");
  const [count, setCount] = useState(10);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState({});

  const startSimulation = async () => {
    const res = await fetch("http://localhost:5050/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count, method }),
    });
    const data = await res.json();
    setResults(data.results);
    setSummary(data.summary);
    setLogs(data.logs);
    setTimeline(data.timeline || []);
    console.log(data.timeline)
  };

  const applyAlgorithm = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5050/set-algorithm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithm, method }),
    });
    const data = await res.json();
    alert(data.message);
  };

  const pieData = {
    labels: Object.keys(summary),
    datasets: [
      {
        label: "Request Distribution",
        data: Object.values(summary),
        backgroundColor: ["#66b3ff", "#99ff99", "#ffcc99"],
        borderWidth: 1,
      },
    ],
  };

  const timelineChartData = {
    labels: (timeline || []).map((item) => `Req ${item.request_id} (${item.server})`),
    datasets: [
      {
        label: "Request Duration (s)",
        data: (timeline || []).map((item) => item.duration),
        backgroundColor: "#3399ff",
      },
    ],
  };

  const timelineChartOptions = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `${context.raw}s`,
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Duration (s)",
        },
      },
      y: {
        ticks: {
          font: {
            size: 12,
          },
          autoSkip: false, // Show all labels
        },
      },
    },
  };
     
  return (
    <div className="simulation-container">
      <h2 className="simulation-h2">⚙️ Load Balancer Configuration</h2>
      <form onSubmit={applyAlgorithm} className="simulation-form">
        <label className="simulation-label">Select Algorithm:</label>
        <select
          className="simulation-select"
          value={algorithm}
          onChange={(e) => setAlgorithm(e.target.value)}
        >
          <option value="round_robin">Round Robin</option>
          <option value="least_conn">Least Connections</option>
          <option value="ip_hash">IP Hash</option>
        </select>

        <label className="simulation-label">Select Load Balancer:</label>
        <select
          className="simulation-select"
          value={method}
          onChange={(e) => setMethod(e.target.value)}
        >
          <option value="nginx">NGINX</option>
          <option value="haproxy">HAProxy</option>
        </select>

        <button className="simulation-button" type="submit">
          Apply Algorithm
        </button>
      </form>

      <h2 className="simulation-h2">📡 Simulate Load Balancer Requests</h2>
      <label className="simulation-label">Number of Requests: </label>
      <input
        type="number"
        className="simulation-input"
        value={count}
        min="1"
        onChange={(e) => setCount(parseInt(e.target.value))}
      />
      <button className="simulation-button" onClick={startSimulation}>
        Send Requests
      </button>

      <h3 className="simulation-h3">Results</h3>
      <table className="simulation-table">
        <thead>
          <tr>
            <th className="simulation-th">Request #</th>
            <th className="simulation-th">Response</th>
          </tr>
        </thead>
        <tbody>
          {results.map((row, idx) => (
            <tr key={idx}>
              <td className="simulation-td">{row.request}</td>
              <td className="simulation-td">{row.response}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 className="simulation-h3">📊 Request Summary</h3>
      <ul className="simulation-ul">
        {Object.entries(summary).map(([server, count], idx) => (
          <li key={idx}>
            {server}: {count} request(s)
          </li>
        ))}
      </ul>

      <h3 className="simulation-h3">📊 Load Distribution Chart</h3>
      <div style={{ width: "400px", marginTop: "20px" }}>
        <Pie data={pieData} />
      </div>

      <h3 className="simulation-h3">📈 Request Timeline</h3>
      <div
  style={{
    width: "100%",
    maxWidth: "900px",
    height: `${timeline.length * 40}px`,
    marginTop: "20px",
  }}
>
  <Bar data={timelineChartData} options={timelineChartOptions} />
</div>

      <h3 className="simulation-h3">🧾 Detailed Simulation Logs</h3>
      <div className="simulation-logs">
        {logs.map((log, idx) => (
          <div key={idx}>{log}</div>
        ))}
      </div>
    </div>
  );
}

export default SimulatorPage;