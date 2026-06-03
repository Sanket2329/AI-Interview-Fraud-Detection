export default function RiskAnalysis({ state }) {
  const bars = [
    {
      label: "Fraud Probability",
      value: state?.fraud_probability ?? 0,
      color: "#ef4444",
      bg: "rgba(239,68,68,0.15)",
    },
    {
      label: "Attention Score",
      value: state?.attention_score ?? 100,
      color: "#f59e0b",
      bg: "rgba(245,158,11,0.15)",
    },
    {
      label: "Identity Confidence",
      value: state?.identity_confidence ?? 100,
      color: "#22c55e",
      bg: "rgba(34,197,94,0.15)",
    },
    {
      label: "Head Movement Suspicion",
      value: state?.head_suspicion ?? 0,
      color: "#f97316",
      bg: "rgba(249,115,22,0.15)",
    },
  ];

  return (
    <div className="glass-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-title-icon">🧠</span>
          AI Risk Analysis
        </h2>
        <span
          className={`risk-badge ${
            (state?.risk_level ?? "LOW") === "LOW"
              ? "risk-badge-low"
              : (state?.risk_level ?? "LOW") === "MEDIUM"
              ? "risk-badge-medium"
              : "risk-badge-high"
          }`}
        >
          {state?.risk_level ?? "LOW"}
        </span>
      </div>

      <div className="risk-bars">
        {bars.map((bar, i) => (
          <div key={i} className="risk-bar-group">
            <div className="risk-bar-header">
              <span className="risk-bar-label">{bar.label}</span>
              <span
                className="risk-bar-value"
                style={{ color: bar.color }}
              >
                {Math.round(bar.value)}%
              </span>
            </div>
            <div className="risk-bar-track" style={{ background: bar.bg }}>
              <div
                className="risk-bar-fill"
                style={{
                  width: `${Math.min(bar.value, 100)}%`,
                  background: `linear-gradient(90deg, ${bar.color}88, ${bar.color})`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
