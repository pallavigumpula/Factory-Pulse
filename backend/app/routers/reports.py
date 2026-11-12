import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import Machine, ProductionLine, DowntimeReason
from backend.app.models.production import ProductionOrder, MachineStateEvent
from backend.app.models.anomaly import DetectedAnomaly
from backend.app.models.user import User
from backend.app.services.report_service import ReportService
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])

def parse_report_dates(start_date: Optional[datetime.date], end_date: Optional[datetime.date]):
    if not end_date:
        end_date = datetime.date.today()
    if not start_date:
        start_date = end_date - datetime.timedelta(days=7)
    return start_date, end_date

@router.get("/oee")
def get_oee_report(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s_date, e_date = parse_report_dates(start_date, end_date)
    return ReportService.generate_oee_report_data(db, s_date, e_date, line_id, machine_id)

@router.get("/oee/export/csv")
def export_oee_csv(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s_date, e_date = parse_report_dates(start_date, end_date)
    data = ReportService.generate_oee_report_data(db, s_date, e_date, line_id, machine_id)
    csv_content = ReportService.export_csv(data)
    filename = f"factorypulse_oee_report_{s_date}_{e_date}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/oee/export/json")
def export_oee_json(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s_date, e_date = parse_report_dates(start_date, end_date)
    data = ReportService.generate_oee_report_data(db, s_date, e_date, line_id, machine_id)
    json_content = ReportService.export_json(data)
    filename = f"factorypulse_oee_report_{s_date}_{e_date}.json"
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/anomalies/export/csv")
def export_anomalies_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomalies = db.query(DetectedAnomaly).order_by(DetectedAnomaly.detected_at.desc()).all()
    rows = [
        {
            "anomaly_code": a.anomaly_code,
            "anomaly_type": a.anomaly_type,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "severity": a.severity,
            "timestamp": a.timestamp.isoformat(),
            "description": a.description,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "recommended_action": a.recommended_action,
            "resolution_status": a.resolution_status,
            "detected_at": a.detected_at.isoformat()
        }
        for a in anomalies
    ]
    csv_content = ReportService.export_csv(rows)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=factorypulse_anomalies_report.csv"}
    )

@router.get("/anomalies/export/json")
def export_anomalies_json(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomalies = db.query(DetectedAnomaly).order_by(DetectedAnomaly.detected_at.desc()).all()
    rows = [
        {
            "anomaly_code": a.anomaly_code,
            "anomaly_type": a.anomaly_type,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "severity": a.severity,
            "timestamp": a.timestamp.isoformat(),
            "description": a.description,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "recommended_action": a.recommended_action,
            "resolution_status": a.resolution_status,
            "detected_at": a.detected_at.isoformat()
        }
        for a in anomalies
    ]
    json_content = ReportService.export_json(rows)
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=factorypulse_anomalies_report.json"}
    )

@router.get("/production-summary")
def get_production_summary(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(ProductionOrder).order_by(ProductionOrder.created_at.desc()).limit(100).all()
    res = []
    for o in orders:
        comp_rate = round((o.produced_quantity / o.target_quantity * 100.0), 1) if o.target_quantity > 0 else 0.0
        res.append({
            "order_code": o.order_code,
            "line_code": o.line.line_code if o.line else "N/A",
            "product_name": o.product.name if o.product else "N/A",
            "target_quantity": o.target_quantity,
            "produced_quantity": o.produced_quantity,
            "status": o.status,
            "completion_rate": min(100.0, comp_rate),
            "start_time": o.start_time.isoformat() if o.start_time else None,
            "end_time": o.end_time.isoformat() if o.end_time else None
        })
    return res

@router.get("/downtime-summary")
def get_downtime_summary(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        DowntimeReason.reason_code,
        DowntimeReason.name,
        DowntimeReason.category,
        DowntimeReason.is_planned,
        func.count(MachineStateEvent.id).label("incidents"),
        func.sum(MachineStateEvent.duration_seconds).label("seconds")
    ).join(
        MachineStateEvent, MachineStateEvent.downtime_reason_id == DowntimeReason.id
    )

    if start_date or end_date:
        s_date, e_date = parse_report_dates(start_date, end_date)
        s_dt = datetime.datetime.combine(s_date, datetime.time.min)
        e_dt = datetime.datetime.combine(e_date, datetime.time.max)
        query = query.filter(
            MachineStateEvent.start_time >= s_dt,
            MachineStateEvent.end_time <= e_dt
        )

    records = query.group_by(
        DowntimeReason.reason_code,
        DowntimeReason.name,
        DowntimeReason.category,
        DowntimeReason.is_planned
    ).order_by(func.sum(MachineStateEvent.duration_seconds).desc()).all()

    tot_sec = sum(r.seconds or 0 for r in records)
    out = []
    for r in records:
        sec = float(r.seconds or 0)
        pct = (sec / tot_sec * 100.0) if tot_sec > 0 else 0.0
        out.append({
            "reason_code": r.reason_code,
            "name": r.name,
            "category": r.category,
            "is_planned": r.is_planned,
            "incidents": r.incidents,
            "duration_minutes": round(sec / 60.0, 1),
            "percentage": round(pct, 1)
        })
    return out
