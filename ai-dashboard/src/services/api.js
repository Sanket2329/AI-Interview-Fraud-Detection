const API_BASE = "http://localhost:8000";

/**
 * API client for the AI Interview Fraud Detection backend.
 */

export async function fetchFraudScore() {
  const res = await fetch(`${API_BASE}/fraud-score`);
  return res.json();
}

export async function fetchLogs() {
  const res = await fetch(`${API_BASE}/logs`);
  return res.json();
}

export async function resetSession() {
  const res = await fetch(`${API_BASE}/reset-score`, { method: "POST" });
  return res.json();
}

export async function fetchHistory() {
  const res = await fetch(`${API_BASE}/history`);
  return res.json();
}

export function getVideoFeedUrl() {
  return `${API_BASE}/video-feed`;
}

/**
 * Connect to the Server-Sent Events stream.
 * @param {function} onData - Callback receiving parsed { state, events } objects.
 * @returns {EventSource} - The EventSource instance (call .close() to disconnect).
 */
export function connectSSE(onData) {
  const es = new EventSource(`${API_BASE}/stream`);

  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onData(data);
    } catch (err) {
      console.error("SSE parse error:", err);
    }
  };

  es.onerror = () => {
    console.warn("SSE connection error — will auto-reconnect.");
  };

  return es;
}
