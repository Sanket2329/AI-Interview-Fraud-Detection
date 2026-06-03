import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import DashboardMetrics from "./components/DashboardMetrics";
import LiveVideoFeed from "./components/LiveVideoFeed";
import RiskAnalysis from "./components/RiskAnalysis";
import ActivityLogs from "./components/ActivityLogs";
import { connectSSE } from "./services/api";
import "./App.css";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [state, setState] = useState(null);
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const es = connectSSE((data) => {
      setState(data.state);
      setEvents(data.events || []);
      setConnected(true);
    });

    return () => es.close();
  }, []);

  const riskLevel = state?.risk_level ?? "LOW";
  const isHighRisk = riskLevel === "HIGH" || riskLevel === "CRITICAL";

  return (
    <div className="app-layout">
      <Sidebar state={state} activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="header-left">
            <h1 className="header-title">
              Enterprise AI Monitoring Dashboard
            </h1>
            <p className="header-subtitle">
              Real-time interview fraud detection &amp; analytics
            </p>
          </div>

          <div className="header-right">
            <div
              className={`connection-badge ${
                connected ? "connected" : "disconnected"
              }`}
            >
              <span className="conn-dot" />
              {connected ? "Live" : "Connecting..."}
            </div>

            {isHighRisk && (
              <div className="alert-badge">
                <span className="alert-pulse" />
                ⚠ {riskLevel} RISK DETECTED
              </div>
            )}
          </div>
        </header>

        {/* Content based on Active Tab */}
        {activeTab === "dashboard" && (
          <>
            <DashboardMetrics state={state} />
            <div className="panels-grid">
              <LiveVideoFeed state={state} />
              <RiskAnalysis state={state} />
            </div>
            <ActivityLogs events={events} onReset={() => {}} />
          </>
        )}

        {activeTab === "monitoring" && (
          <div className="panels-grid" style={{ gridTemplateColumns: '1fr' }}>
            <LiveVideoFeed state={state} />
          </div>
        )}

        {activeTab === "analytics" && (
          <div className="panels-grid" style={{ gridTemplateColumns: '1fr' }}>
            <DashboardMetrics state={state} />
            <RiskAnalysis state={state} />
          </div>
        )}

        {activeTab === "logs" && (
          <ActivityLogs events={events} onReset={() => {}} />
        )}

        {activeTab === "reports" && (
          <div className="glass-card">
            <h2 className="card-title mb-4">Candidate Session Report</h2>
            <p className="text-gray-400">Current Session Duration: {state?.session_duration || '0 Min'}</p>
            <p className="text-gray-400">Total Suspicious Events: {events.length}</p>
            <p className="text-gray-400">Final Risk Designation: <span className="font-bold">{riskLevel}</span></p>
          </div>
        )}

        {/* Footer */}
        <footer className="app-footer">
          <p>
            Enterprise AI Interview Fraud Detection System • Built with React +
            FastAPI + OpenCV + MediaPipe
          </p>
        </footer>
      </main>
    </div>
  );
}
