from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AnomalyBase(BaseModel):
    anomaly_code: Optional[str] = None
    anomaly_type: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    expected_value: str
    actual_value: str
    recommended_action: str
    resolution_status: Optional[str] = "OPEN"

class AnomalyCreate(AnomalyBase):
    pass

class AnomalyUpdate(BaseModel):
    resolution_status: str # OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE

class AnomalyResponse(AnomalyBase):
    id: int
    anomaly_code: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AnomalyMetrics(BaseModel):
    total_detected: int
    total_ground_truth: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    by_type: dict
