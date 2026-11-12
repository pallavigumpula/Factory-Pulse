import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.anomaly import DetectedAnomaly
from backend.app.models.user import User
from backend.app.schemas.anomaly import AnomalyResponse, AnomalyUpdate, AnomalyMetrics
from backend.app.services.anomaly_detector import AnomalyDetector
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])

@router.get("", response_model=List[AnomalyResponse])
def list_anomalies(
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DetectedAnomaly)
    if severity:
        query = query.filter(DetectedAnomaly.severity == severity.upper())
    if anomaly_type:
        query = query.filter(DetectedAnomaly.anomaly_type == anomaly_type)
    if status_filter:
        query = query.filter(DetectedAnomaly.resolution_status == status_filter.upper())
    return query.order_by(DetectedAnomaly.detected_at.desc()).offset(skip).limit(limit).all()

@router.post("/scan", response_model=List[AnomalyResponse])
def trigger_anomaly_scan(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "QUALITY", "MAINTENANCE"))
):
    """Triggers complete anomaly scan across all operational data."""
    AnomalyDetector.run_detection(db, persist=True)
    return db.query(DetectedAnomaly).order_by(DetectedAnomaly.detected_at.desc()).all()

@router.put("/{anomaly_id}/status", response_model=AnomalyResponse)
def update_anomaly_status(
    anomaly_id: int,
    update_in: AnomalyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "QUALITY", "MAINTENANCE"))
):
    anom = db.query(DetectedAnomaly).filter(DetectedAnomaly.id == anomaly_id).first()
    if not anom:
        raise HTTPException(status_code=404, detail="Anomaly record not found")
    
    anom.resolution_status = update_in.resolution_status.upper()
    if anom.resolution_status in ("RESOLVED", "FALSE_POSITIVE"):
        import datetime
        anom.resolved_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(anom)
    return anom

@router.get("/evaluation", response_model=AnomalyMetrics)
def evaluate_anomaly_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates detected anomalies against the independent ground truth file.
    Calculates precision, recall, and F1-score.
    """
    detected_records = db.query(DetectedAnomaly).all()
    detected_list = [
        {
            "anomaly_type": a.anomaly_type,
            "entity_id": a.entity_id,
            "severity": a.severity
        }
        for a in detected_records
    ]
    
    # Check for ground_truth file in data/
    gt_file = "data/ground_truth.json"
    if not os.path.exists(gt_file):
        gt_file = "data/starter/ground_truth.json"
    if not os.path.exists(gt_file):
        gt_file = "data/ground_truth.csv"

    metrics = AnomalyDetector.evaluate_against_ground_truth(detected_list, gt_file)
    return metrics
