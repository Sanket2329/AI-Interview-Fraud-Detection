<div align="center">

<img src="https://img.shields.io/badge/AI%20Interview%20Fraud%20Detection-v2.0.0-blueviolet?style=for-the-badge&logo=opencv&logoColor=white" alt="Project Badge" />

![AI Interview Fraud Detection Logo](https://github.com/Sanket2329/AI-Interview-Fraud-Detection/blob/main/logo.png)

# AI Interview Fraud Detection System

**Enterprise-grade real-time proctoring powered by Computer Vision & AI**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?style=flat-square&logo=opencv)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00?style=flat-square&logo=google)](https://mediapipe.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)

</div>

---

## Overview

The **AI Interview Fraud Detection System** is a full-stack, enterprise-grade proctoring platform that monitors interview candidates in real time using computer vision. It detects suspicious behaviors — like looking away, multiple faces on screen, or a candidate going off-camera — and assigns a live fraud risk score streamed directly to a React dashboard.

Built with **FastAPI** on the backend and a **React + Tailwind CSS** dashboard on the frontend, the system is suitable for remote hiring pipelines, online assessments, and compliance-driven interview environments.

---

## Features

- **Live MJPEG Video Feed** — Real-time webcam stream with CV overlays rendered server-side
- **Head Pose Estimation** — Uses MediaPipe + OpenCV `solvePnP` to detect head direction (Left, Right, Up, Down, Forward)
- **Eye Gaze Tracking** — Iris landmark tracking to determine where the candidate is looking
- **Multi-Face Detection** — Zero-tolerance policy; detects additional faces via both Haar Cascades and MediaPipe with a hard penalty of 25 points
- **Candidate Absence Detection** — Triggers after 3 seconds with no face in frame
- **Look-Away Grace Period** — First 10 look-aways issue warnings only; beyond 10 each occurrence adds to the fraud score
- **Live Fraud Score** — Dynamically calculated 0–100 risk score streamed via Server-Sent Events (SSE)
- **Risk Level Classification** — `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` based on cumulative fraud score
- **Session Persistence** — All fraud events are stored in SQLite and accessible via REST API
- **Configurable Penalties** — All thresholds and score penalties are environment-variable driven

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.115, Python 3.10+ |
| Computer Vision | OpenCV 4.10, MediaPipe 0.10 |
| Frontend | React 18, Vite, Tailwind CSS |
| Database | SQLite via SQLAlchemy 2.0 |
| Streaming | MJPEG (video), Server-Sent Events (state) |
| Config | python-dotenv, Pydantic |

---

## Project Structure

```
AI-Interview-Fraud-Detection/
├── main.py                    # FastAPI app, routes, SSE stream
├── models.py                  # SQLAlchemy ORM models (FraudLog, Session)
├── database.py                # DB engine and session factory
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
│
├── core/
│   └── config.py              # Settings loaded from .env
│
├── services/
│   └── vision_service.py      # Full CV pipeline (head pose, gaze, multi-face)
│
└── ai-dashboard/              # React frontend
    ├── src/
    │   ├── App.jsx             # Root layout, tab routing, SSE connection
    │   ├── components/
    │   │   ├── Sidebar.jsx
    │   │   ├── DashboardMetrics.jsx
    │   │   ├── LiveVideoFeed.jsx
    │   │   ├── RiskAnalysis.jsx
    │   │   └── ActivityLogs.jsx
    │   └── services/
    │       └── api.js          # SSE client, REST helpers
    └── vite.config.js
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A connected webcam

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI-Interview-Fraud-Detection.git
cd AI-Interview-Fraud-Detection
```

### 2. Set up the Python backend

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the `.env` file and adjust values as needed:

```env
DATABASE_URL=sqlite:///./interview_fraud.db
CAMERA_INDEX=0
LOOK_AWAY_THRESHOLD_SEC=3.0
MULTI_FACE_PENALTY=25
LOOK_AWAY_PENALTY=5
NO_FACE_PENALTY=10
RISK_LOW_MAX=10
RISK_MEDIUM_MAX=25
DEBUG=true
```

### 4. Start the backend

```bash
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### 5. Start the frontend

```bash
cd ai-dashboard
npm install
npm run dev
```

Dashboard runs at: `http://localhost:5173`

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/video-feed` | Live MJPEG webcam stream with overlays |
| `GET` | `/stream` | Server-Sent Events — fraud state & events |
| `GET` | `/fraud-score` | Current fraud analytics snapshot |
| `GET` | `/logs` | All fraud events from current session |
| `POST` | `/reset-score` | Persist session to DB and reset state |
| `GET` | `/history` | Last 100 persisted fraud logs from DB |

Interactive docs available at `http://localhost:8000/docs`

---

## Fraud Scoring Logic

| Trigger | Penalty | Severity |
|---|---|---|
| Look-away (1st–10th time) | 0 pts (Warning only) | Warning |
| Look-away (11th+ time) | +5 pts per offence | High |
| Multiple faces detected | +25 pts per detection | Critical |
| Candidate absent for 3s+ | +10 pts per interval | High |

**Risk Levels:**

```
Fraud Score  0–10   → LOW
Fraud Score 11–25   → MEDIUM
Fraud Score 26–40   → HIGH
Fraud Score  41+    → CRITICAL
```

Fraud probability is capped at 100% (score of 50 = 100%).

---

## Dashboard Views

| Tab | Description |
|---|---|
| Dashboard | Full overview — metrics, live feed, risk chart, activity log |
| Monitoring | Full-screen live camera feed |
| Analytics | Metrics and risk analysis panels |
| Logs | Complete activity event log |
| Reports | Session summary with duration and final risk designation |

---

## Screenshots

> Run the app and open `http://localhost:5173` to see the live dashboard.

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with React + FastAPI + OpenCV + MediaPipe

</div>
python -m uvicorn main:app --reload 

