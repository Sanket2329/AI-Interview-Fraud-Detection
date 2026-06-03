

const navItems = [
  { label: "Dashboard", icon: "📊", id: "dashboard" },
  { label: "Live Monitoring", icon: "🎥", id: "monitoring" },
  { label: "Fraud Analytics", icon: "🔍", id: "analytics" },
  { label: "Candidate Reports", icon: "📋", id: "reports" },
  { label: "Activity Logs", icon: "📝", id: "logs" },
];

export default function Sidebar({ state, activeTab, onTabChange }) {
  const riskLevel = state?.risk_level || "LOW";

  const riskColor =
    riskLevel === "CRITICAL"
      ? "text-red-500"
      : riskLevel === "HIGH"
      ? "text-orange-400"
      : riskLevel === "MEDIUM"
      ? "text-yellow-400"
      : "text-green-400";

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-icon">🛡️</div>
        <div>
          <h1 className="brand-title">AI Proctor</h1>
          <p className="brand-subtitle">Fraud Detection Suite</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeTab === item.id ? "nav-item-active" : ""}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Candidate Card */}
      <div className="candidate-card">
        <div className="candidate-avatar">
          <span>S</span>
        </div>
        <div className="candidate-info">
          <h2 className="candidate-name">Sanket Shakya</h2>
          <p className="candidate-id">ID: INT-2048</p>
        </div>
        <div className="candidate-meta">
          <div className="meta-row">
            <span className="meta-label">Status</span>
            <span className={`meta-value ${riskColor}`}>{riskLevel} Risk</span>
          </div>
          <div className="meta-row">
            <span className="meta-label">Session</span>
            <span className="meta-value text-cyan-400">
              {state?.is_active ? "● Active" : "○ Inactive"}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
