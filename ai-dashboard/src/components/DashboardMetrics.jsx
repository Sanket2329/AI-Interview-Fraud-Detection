export default function DashboardMetrics({ state }) {
  const metrics = [
    {
      title: "Fraud Score",
      value: state?.fraud_score ?? 0,
      icon: "🔥",
      gradient: "metric-gradient-red",
      accent: "#ef4444",
    },
    {
      title: "Attention Score",
      value: `${state?.attention_score ?? 100}%`,
      icon: "👁️",
      gradient: "metric-gradient-amber",
      accent: "#f59e0b",
    },
    {
      title: "Session Duration",
      value: state?.session_duration ?? "0 Min",
      icon: "⏱️",
      gradient: "metric-gradient-blue",
      accent: "#3b82f6",
    },
    {
      title: "Risk Level",
      value: state?.risk_level ?? "LOW",
      icon: "⚡",
      gradient:
        state?.risk_level === "CRITICAL" || state?.risk_level === "HIGH"
          ? "metric-gradient-red"
          : state?.risk_level === "MEDIUM"
          ? "metric-gradient-amber"
          : "metric-gradient-green",
      accent:
        state?.risk_level === "CRITICAL" || state?.risk_level === "HIGH"
          ? "#ef4444"
          : state?.risk_level === "MEDIUM"
          ? "#f59e0b"
          : "#22c55e",
    },
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((m, i) => (
        <div key={i} className={`metric-card ${m.gradient}`}>
          <div className="metric-icon-wrap">
            <span className="metric-icon">{m.icon}</span>
          </div>
          <p className="metric-title">{m.title}</p>
          <p className="metric-value" style={{ color: m.accent }}>
            {m.value}
          </p>
          <div
            className="metric-bar"
            style={{ background: m.accent, opacity: 0.3 }}
          />
        </div>
      ))}
    </div>
  );
}
