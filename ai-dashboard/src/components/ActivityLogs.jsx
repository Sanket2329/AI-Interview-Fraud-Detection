import { resetSession } from "../services/api";

export default function ActivityLogs({ events, onReset }) {
  const handleReset = async () => {
    await resetSession();
    if (onReset) onReset();
  };

  const warnings = events.filter((e) => e.is_warning);
  const fraudEvents = events.filter((e) => !e.is_warning);

  return (
    <div className="glass-card activity-logs-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-title-icon">📋</span>
          Proctoring Activity Log
        </h2>
        <div className="logs-header-actions">
          <span className="log-count" style={{ color: "var(--accent-amber)" }}>
            ⚠ {warnings.length}/10 warnings
          </span>
          <span className="log-count" style={{ color: "var(--accent-red)" }}>
            🚨 {fraudEvents.length} fraud events
          </span>
          <button className="btn-reset" onClick={handleReset}>
            <span>🔄</span> Reset Session
          </button>
        </div>
      </div>

      <div className="logs-table-wrap">
        <table className="logs-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Activity</th>
              <th>Type</th>
              <th>Score Impact</th>
              <th>Timestamp</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="6" className="logs-empty">
                  <span className="empty-icon">✅</span>
                  No suspicious activity detected yet
                </td>
              </tr>
            ) : (
              [...events].reverse().map((ev, i) => (
                <tr
                  key={i}
                  className="log-row"
                  style={{
                    background: ev.is_warning
                      ? "rgba(245, 158, 11, 0.04)"
                      : "transparent",
                  }}
                >
                  <td className="log-index">{events.length - i}</td>
                  <td className="log-event">{ev.event}</td>
                  <td>
                    <span
                      className={`severity-badge ${
                        ev.is_warning ? "severity-warning" : `severity-${ev.severity?.toLowerCase()}`
                      }`}
                    >
                      {ev.is_warning ? "⚠ Warning" : ev.severity}
                    </span>
                  </td>
                  <td className="log-impact">
                    {ev.is_warning ? (
                      <span style={{ color: "var(--accent-amber)", fontWeight: 600 }}>
                        No Impact
                      </span>
                    ) : (
                      <span style={{ color: "var(--accent-red)", fontWeight: 700 }}>
                        +{ev.score_impact}
                      </span>
                    )}
                  </td>
                  <td className="log-time">{ev.timestamp}</td>
                  <td>
                    {ev.is_warning ? (
                      <span style={{ color: "var(--accent-amber)", fontSize: "0.8rem", fontWeight: 600 }}>
                        ⚠ Cautioned
                      </span>
                    ) : (
                      <span style={{ color: "var(--accent-red)", fontSize: "0.8rem", fontWeight: 600 }}>
                        🚨 Flagged
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
