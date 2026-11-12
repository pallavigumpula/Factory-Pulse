import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.app.database import Base

class DetectedAnomaly(Base):
    __tablename__ = "detected_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_code = Column(String(60), unique=True, index=True, nullable=False)
    anomaly_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False) # MACHINE, PRODUCTION_ORDER, LINE, PRODUCT
    entity_id = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True) # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    expected_value = Column(String(255), nullable=False)
    actual_value = Column(String(255), nullable=False)
    recommended_action = Column(Text, nullable=False)
    resolution_status = Column(String(30), default="OPEN", nullable=False, index=True) # OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    detected_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
