"""
AI Interview Fraud Detection System - FastAPI Backend
Enterprise-grade API with real-time video streaming and Server-Sent Events.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from core.config import settings
from database import engine, get_db
from models import Base, FraudLog
from services.vision_service import VisionProcessor

import asyncio
import json

# ---------------------------------------------------------------------------
# Create database tables
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI-powered interview fraud detection with real-time "
                "computer vision analytics."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Vision processor singleton
# ---------------------------------------------------------------------------
vision = VisionProcessor()


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """Start the camera when the server boots."""
    vision.start()


@app.on_event("shutdown")
def shutdown_event():
    """Release camera on server shutdown."""
    vision.stop()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/video-feed", tags=["Streaming"])
def video_feed():
    """Live MJPEG webcam feed with CV overlays."""
    return StreamingResponse(
        vision.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/stream", tags=["Streaming"])
async def event_stream():
    """
    Server-Sent Events endpoint.
    Streams real-time fraud state and events to the frontend.
    """
    async def generate():
        while True:
            state = vision.get_state_dict()
            events = vision.get_events()
            payload = json.dumps({
                "state": state,
                "events": events[-50:]  # Last 50 events
            })
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/fraud-score", tags=["Analytics"])
def get_fraud_score():
    """Get current fraud analytics snapshot."""
    return vision.get_state_dict()


@app.get("/logs", tags=["Analytics"])
def get_logs():
    """Get all fraud events from current session."""
    return vision.get_events()


@app.post("/reset-score", tags=["Control"])
def reset_score(db: DBSession = Depends(get_db)):
    """
    Reset the fraud detection system.
    Persists current session events to the database before clearing.
    """
    # Persist current events to DB
    for ev in vision.get_events():
        log = FraudLog(
            event=ev["event"],
            severity=ev["severity"],
            score_impact=ev["score_impact"]
        )
        db.add(log)
    db.commit()

    # Reset vision state
    vision.reset()

    return {"message": "System Reset Complete"}


@app.get("/history", tags=["Analytics"])
def get_history(db: DBSession = Depends(get_db)):
    """Get persisted fraud logs from previous sessions."""
    logs = db.query(FraudLog).order_by(FraudLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "event": log.event,
            "severity": log.severity,
            "score_impact": log.score_impact,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
            if log.timestamp else ""
        }
        for log in logs
    ]