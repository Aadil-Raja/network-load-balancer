// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import SimulatorPage from "./components/simulation/simulation"
import StatusDashboard from "./components/status/status";


function App() {
  return (
    <Router>
      <div className="container">
        <nav>
          <Link to="/">Simulator</Link> | <Link to="/status">Server Status</Link>
        </nav>
        <Routes>
          <Route path="/" element={<SimulatorPage />} />
          <Route path="/status" element={<StatusDashboard />} />
         
        </Routes>
      </div>
    </Router>
  );
}

export default App;
