"""
Unified Vision Processor — Professional Proctoring Engine
Rules:
  - Looking away ≤ 10 times: issues a WARNING, no fraud score added.
  - Looking away > 10 times: each additional look-away adds fraud score.
  - Multiple faces (≥ 2): ZERO TOLERANCE — immediately adds hard penalty.
  - No face detected for > 3s: fraud score added.
  - Fraud probability: 0–100%, where fraud_score of 50 = 100%.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from core.config import settings


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class FraudEvent:
    """Represents a single event logged by the proctoring system."""
    event: str
    severity: str        # "Warning", "Low", "Medium", "High", "Critical"
    is_warning: bool     # True = no score impact, just a caution
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%I:%M:%S %p"))
    score_impact: int = 0


@dataclass
class VisionState:
    """Current live state snapshot of the proctoring session."""
    fraud_score: int = 0
    attention_score: float = 100.0
    head_direction: str = "Forward"
    eye_direction: str = "Center"
    faces_detected: int = 0
    identity_confidence: float = 100.0
    head_suspicion: float = 0.0
    fraud_probability: float = 0.0
    risk_level: str = "LOW"
    look_away_count: int = 0      # total times the candidate looked away
    warning_count: int = 0         # warnings issued (first 10 look-aways)
    session_start: float = field(default_factory=time.time)
    is_active: bool = False


# ─── Main Processor ─────────────────────────────────────────────────────────

class VisionProcessor:
    """
    Professional proctoring vision pipeline:
    - Head pose estimation (MediaPipe solvePnP)
    - Eye gaze tracking (MediaPipe iris landmarks)
    - Multi-face detection (Haar Cascades) — ZERO TOLERANCE
    - Look-away counter with 10-warning grace period
    """

    # Grace period: first N look-aways only get warnings, no score impact
    LOOK_AWAY_WARNING_LIMIT = 10

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            max_num_faces=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.state = VisionState()
        self.events: List[FraudEvent] = []
        self._lock = threading.Lock()

        # Timing trackers
        self._looking_away_start: Optional[float] = None
        self._no_face_start: Optional[float] = None

        # Attention frame counters
        self._total_attentive_frames = 0
        self._total_frames = 0

        # Multi-face cooldown: avoid spamming events on same detection
        self._multi_face_last_event: float = 0.0

        self.camera: Optional[cv2.VideoCapture] = None

    # ─── Lifecycle ───────────────────────────────────────────────────────────

    def start(self):
        """Initialize camera and begin session."""
        self.camera = cv2.VideoCapture(settings.CAMERA_INDEX, cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.state.is_active = True
        self.state.session_start = time.time()

    def stop(self):
        """Release camera resources."""
        self.state.is_active = False
        if self.camera:
            self.camera.release()
            self.camera = None

    def reset(self):
        """Reset all state for a new session."""
        with self._lock:
            self.state = VisionState()
            self.state.is_active = True
            self.state.session_start = time.time()
            self.events.clear()
            self._looking_away_start = None
            self._no_face_start = None
            self._total_attentive_frames = 0
            self._total_frames = 0
            self._multi_face_last_event = 0.0

    # ─── Event Helpers ───────────────────────────────────────────────────────

    def _add_warning(self, event_text: str):
        """Log a warning — visible in logs but does NOT affect fraud score."""
        with self._lock:
            self.events.append(FraudEvent(
                event=event_text,
                severity="Warning",
                is_warning=True,
                score_impact=0
            ))
            self.state.warning_count += 1

    def _add_fraud_event(self, event_text: str, severity: str, score_impact: int):
        """Log a confirmed fraud event — adds to fraud score."""
        with self._lock:
            self.events.append(FraudEvent(
                event=event_text,
                severity=severity,
                is_warning=False,
                score_impact=score_impact
            ))
            self.state.fraud_score += score_impact

    # ─── CV Algorithms ───────────────────────────────────────────────────────

    def _compute_eye_direction(self, face_landmarks, fw, fh) -> str:
        """Compute gaze direction from iris landmarks. Wide tolerances for natural movement."""
        iris = face_landmarks.landmark[468]
        left_corner = face_landmarks.landmark[33]
        right_corner = face_landmarks.landmark[133]
        top_eye = face_landmarks.landmark[159]
        bottom_eye = face_landmarks.landmark[145]

        h_ratio = (iris.x - left_corner.x) / max(right_corner.x - left_corner.x, 1e-6)
        v_ratio = (iris.y - top_eye.y) / max(bottom_eye.y - top_eye.y, 1e-6)

        # Very wide tolerances — only flag when gaze is clearly off-center
        if h_ratio < 0.25:
            return "Looking Left"
        elif h_ratio > 0.75:
            return "Looking Right"
        elif v_ratio < 0.25:
            return "Looking Up"
        elif v_ratio > 0.75:
            return "Looking Down"
        return "Center"

    def _compute_head_pose(self, face_landmarks, img_w, img_h) -> str:
        """Estimate head direction using solvePnP. Relaxed for natural webcam angles."""
        key_indices = [33, 263, 1, 61, 291, 199]
        face_2d, face_3d = [], []

        for idx in key_indices:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = img_w
        cam_matrix = np.array([
            [focal_length, 0, img_h / 2],
            [0, focal_length, img_w / 2],
            [0, 0, 1]
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        success, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        if not success:
            return "Unknown"

        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        x_angle = angles[0] * 360  # pitch (up/down)
        y_angle = angles[1] * 360  # yaw   (left/right)

        # Pitch threshold higher (±35°) because webcams are often below eye level
        if y_angle < -25:
            return "Looking Left"
        elif y_angle > 25:
            return "Looking Right"
        elif x_angle < -35:
            return "Looking Down"
        elif x_angle > 35:
            return "Looking Up"
        return "Forward"

    # ─── Per-Frame Pipeline ──────────────────────────────────────────────────

    def process_frame(self, frame):
        """Run full detection pipeline on one frame. Returns annotated frame."""
        self._total_frames += 1
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]

        # ── MEDIAPIPE: primary processing ─────────────────────────────────
        results = self.face_mesh.process(rgb)

        mp_faces = 0
        if results.multi_face_landmarks:
            mp_faces = len(results.multi_face_landmarks)

        # ── HAAR: fallback face detection ────────────────────────────────
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Stricter Haar parameters to avoid false positives (background noise)
        faces_haar = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=7, minSize=(60, 60)
        )
        haar_faces = len(faces_haar)
        
        # Use whichever detected more faces for the most accurate multi-face detection
        num_faces = max(mp_faces, haar_faces)
        self.state.faces_detected = num_faces

        now = time.time()
        if num_faces > 1:
            # Zero tolerance: fire event max once every 5 seconds to avoid spam
            if now - self._multi_face_last_event > 5.0:
                self._add_fraud_event(
                    f"Multiple Faces Detected ({num_faces} faces) — ZERO TOLERANCE",
                    "Critical",
                    settings.MULTI_FACE_PENALTY  # Hard penalty of 25
                )
                self._multi_face_last_event = now

        if results.multi_face_landmarks:
            self._no_face_start = None
            face_lm = results.multi_face_landmarks[0]

            eye_dir = self._compute_eye_direction(face_lm, w, h)
            self.state.eye_direction = eye_dir

            head_dir = self._compute_head_pose(face_lm, w, h)
            self.state.head_direction = head_dir

            # Attentive = head is pointing forward (eye movement alone is acceptable)
            is_attentive = (head_dir == "Forward")

            if is_attentive:
                self._total_attentive_frames += 1
                self._looking_away_start = None
            else:
                # Start timer when they first look away
                if self._looking_away_start is None:
                    self._looking_away_start = now

                elapsed = now - self._looking_away_start
                # Trigger after they've been looking away for the threshold duration
                if elapsed > settings.LOOK_AWAY_THRESHOLD_SEC:
                    self.state.look_away_count += 1
                    self._looking_away_start = now  # reset timer for next interval

                    if self.state.look_away_count <= self.LOOK_AWAY_WARNING_LIMIT:
                        # ── WARNING PHASE: first 10 look-aways ──
                        remaining = self.LOOK_AWAY_WARNING_LIMIT - self.state.look_away_count
                        self._add_warning(
                            f"⚠ Warning {self.state.look_away_count}/10: Looking Away "
                            f"({head_dir}) — {remaining} warnings remaining"
                        )
                    else:
                        # ── FRAUD PHASE: >10 look-aways, score increases ──
                        self._add_fraud_event(
                            f"Repeated Look-Away #{self.state.look_away_count} "
                            f"({head_dir}) — Exceeds 10-attempt limit",
                            "High",
                            settings.LOOK_AWAY_PENALTY  # 5 per offence
                        )

            # Draw iris dot
            iris = face_lm.landmark[468]
            cv2.circle(frame, (int(iris.x * w), int(iris.y * h)), 4, (0, 255, 0), -1)

        else:
            # No face in frame
            self.state.eye_direction = "N/A"
            self.state.head_direction = "N/A"

            if self._no_face_start is None:
                self._no_face_start = now
            elif now - self._no_face_start > 3.0:
                self._add_fraud_event(
                    "Candidate Not Visible — Face absent for 3+ seconds",
                    "High",
                    settings.NO_FACE_PENALTY  # 10 pts
                )
                self._no_face_start = now

        # ── Derived metrics ──────────────────────────────────────────────────
        raw_attention = (self._total_attentive_frames / max(self._total_frames, 1)) * 100
        self.state.attention_score = min(round(raw_attention, 1), 100.0)

        # fraud_probability: score 50 → 100%
        self.state.fraud_probability = min(
            round(self.state.fraud_score * 2.0, 1), 100.0
        )
        self.state.head_suspicion = round(100 - self.state.attention_score, 1)
        self.state.identity_confidence = max(
            100 - (num_faces - 1) * 50 if num_faces >= 1 else 0, 0
        )

        # Risk level based on fraud_score (max useful = 50)
        score = self.state.fraud_score
        if score <= 10:
            self.state.risk_level = "LOW"
        elif score <= 25:
            self.state.risk_level = "MEDIUM"
        elif score <= 40:
            self.state.risk_level = "HIGH"
        else:
            self.state.risk_level = "CRITICAL"

        frame = self._draw_overlays(frame, faces_haar)
        return frame

    # ─── Overlay Rendering ───────────────────────────────────────────────────

    def _draw_overlays(self, frame, faces_haar):
        """Draw face boxes and HUD on frame."""
        h, w = frame.shape[:2]

        color_map = {
            "LOW": (0, 220, 80),
            "MEDIUM": (0, 180, 255),
            "HIGH": (0, 80, 255),
            "CRITICAL": (0, 0, 255),
        }
        risk_color = color_map.get(self.state.risk_level, (0, 220, 80))

        for (x, y, bw, bh) in faces_haar:
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), risk_color, 2)
            cv2.putText(frame, "FACE", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, risk_color, 2)

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 65), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        cv2.putText(frame, f"Score: {self.state.fraud_score}",
                    (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, risk_color, 2)
        cv2.putText(frame, f"Warnings: {self.state.look_away_count}/10",
                    (10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Head: {self.state.head_direction}",
                    (200, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Faces: {self.state.faces_detected}",
                    (200, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Risk: {self.state.risk_level}",
                    (430, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, risk_color, 2)

        return frame

    # ─── State Export ────────────────────────────────────────────────────────

    def get_state_dict(self) -> dict:
        """Return current state as a JSON-serializable dict."""
        elapsed = time.time() - self.state.session_start
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        with self._lock:
            return {
                "fraud_score": self.state.fraud_score,
                "attention_score": self.state.attention_score,
                "session_duration": f"{minutes}m {seconds}s",
                "risk_level": self.state.risk_level,
                "head_direction": self.state.head_direction,
                "eye_direction": self.state.eye_direction,
                "faces_detected": self.state.faces_detected,
                "identity_confidence": self.state.identity_confidence,
                "head_suspicion": self.state.head_suspicion,
                "fraud_probability": self.state.fraud_probability,
                "look_away_count": self.state.look_away_count,
                "warning_count": self.state.warning_count,
                "is_active": self.state.is_active,
            }

    def get_events(self) -> list:
        """Return all events as dicts."""
        with self._lock:
            return [
                {
                    "event": e.event,
                    "severity": e.severity,
                    "is_warning": e.is_warning,
                    "timestamp": e.timestamp,
                    "score_impact": e.score_impact,
                }
                for e in self.events
            ]

    # ─── MJPEG Stream ────────────────────────────────────────────────────────

    def generate_frames(self):
        """Generator that yields MJPEG frames for /video-feed endpoint."""
        while self.state.is_active and self.camera and self.camera.isOpened():
            success, frame = self.camera.read()
            if not success:
                continue

            frame = self.process_frame(frame)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if ret:
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n'
                    + buffer.tobytes() +
                    b'\r\n'
                )
