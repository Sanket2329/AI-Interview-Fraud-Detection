import { getVideoFeedUrl } from "../services/api";

export default function LiveVideoFeed({ state }) {
  const headDir = state?.head_direction ?? "N/A";
  const eyeDir = state?.eye_direction ?? "N/A";
  const faces = state?.faces_detected ?? 0;

  return (
    <div className="glass-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-title-icon">🎥</span>
          Live Candidate Feed
        </h2>
        <div className="live-badge">
          <span className="live-dot" />
          LIVE
        </div>
      </div>

      <div className="video-container">
        <img
          src={getVideoFeedUrl()}
          alt="Live Candidate Feed"
          className="video-frame"
          onError={(e) => {
            e.target.style.display = "none";
            e.target.nextSibling.style.display = "flex";
          }}
        />
        <div className="video-placeholder" style={{ display: "none" }}>
          <span className="placeholder-icon">📷</span>
          <p>Camera feed unavailable</p>
          <p className="placeholder-hint">
            Start the backend: <code>uvicorn main:app --reload</code>
          </p>
        </div>
      </div>

      <div className="feed-stats">
        <div className="feed-stat-item">
          <span className="feed-stat-label">Head Pose</span>
          <span className="feed-stat-value text-yellow-400">{headDir}</span>
        </div>
        <div className="feed-stat-item">
          <span className="feed-stat-label">Eye Gaze</span>
          <span className="feed-stat-value text-cyan-400">{eyeDir}</span>
        </div>
        <div className="feed-stat-item">
          <span className="feed-stat-label">Faces</span>
          <span
            className={`feed-stat-value ${
              faces > 1 ? "text-red-400" : "text-green-400"
            }`}
          >
            {faces}
          </span>
        </div>
      </div>
    </div>
  );
}
