from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

from database import Base


class FraudLog(Base):
    """Persisted fraud event log."""

    __tablename__ = "fraud_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event = Column(String, nullable=False)
    severity = Column(String, default="Medium")
    score_impact = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    """Interview session metadata."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_name = Column(String, default="Unknown")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    final_fraud_score = Column(Integer, default=0)
    final_risk_level = Column(String, default="LOW")
    final_attention_score = Column(Float, default=100.0)