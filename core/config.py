import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "AI Interview Fraud Detection System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./interview_fraud.db"
    )

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # Vision processing
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    LOOK_AWAY_THRESHOLD_SEC: float = float(
        os.getenv("LOOK_AWAY_THRESHOLD_SEC", "3.0")
    )
    MULTI_FACE_PENALTY: int = int(os.getenv("MULTI_FACE_PENALTY", "25"))
    LOOK_AWAY_PENALTY: int = int(os.getenv("LOOK_AWAY_PENALTY", "5"))
    NO_FACE_PENALTY: int = int(os.getenv("NO_FACE_PENALTY", "10"))

    # Risk thresholds
    RISK_LOW_MAX: int = int(os.getenv("RISK_LOW_MAX", "10"))
    RISK_MEDIUM_MAX: int = int(os.getenv("RISK_MEDIUM_MAX", "25"))


settings = Settings()
