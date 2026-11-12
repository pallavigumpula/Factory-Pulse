import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import Machine, ProductionLine, Shift, Plant, DowntimeReason
from backend.app.models.production import MachineStateEvent, ProductionCount, ProductionOrder
from backend.app.models.user import User
from backend.app.schemas.oee import OEEDashboardKPI
from backend.app.services.oee_engine import OEEEngine, merge_time_intervals, calculate_merged_seconds
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/oee", tags=["OEE Analytics"])

def parse_date_window(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> (datetime.datetime, datetime.datetime):
    if not end_date:
        end_date = datetime.date.today()
    if not start_date:
        start_date = end_date - datetime.timedelta(days=7) # default to last 7 days
    
    start_dt = datetime.datetime.combine(start_date, datetime.time.min)
    end_dt = datetime.datetime.combine(end_date, datetime.time.max)
    return start_dt, end_dt

@router.get("/dashboard-kpis", response_model=OEEDashboardKPI)
def get_dashboard_kpis(
    plant_id: Optional[int] = None,
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    shift_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)

    machine_query = db.query(Machine).filter(Machine.is_active == True)
    if machine_id:
        machine_query = machine_query.filter(Machine.id == machine_id)
    elif line_id:
        machine_query = machine_query.filter(Machine.line_id == line_id)
    elif plant_id:
        machine_query = machine_query.join(ProductionLine).filter(ProductionLine.plant_id == plant_id)

    machines = machine_query.all()
    total_machines = len(machines)
    if total_machines == 0:
        return OEEDashboardKPI(
            overall_oee=0.0,
            availability=0.0,
            performance=0.0,
            quality=0.0,
            total_production=0,
            good_count=0,
            scrap_count=0,
            rework_count=0,
            total_downtime_minutes=0.0,
            planned_downtime_minutes=0.0,
            unplanned_downtime_minutes=0.0,
            target_oee=85.0,
            active_machines_count=0,
            total_machines_count=0,
            performance_flagged_count=0
        )

    results = []
    active_machines = 0
    flagged_machines = 0

    for m in machines:
        res = OEEEngine.calculate_machine_oee(db, m.id, start_dt, end_dt)
        results.append(res)
        if m.current_status == "RUNNING":
            active_machines += 1
        if res["performance_flagged"]:
            flagged_machines += 1

    total_ppt = sum(r["planned_production_time_minutes"] for r in results)
    total_opt = sum(r["operating_time_minutes"] for r in results)
    total_p_dt = sum(r["planned_downtime_minutes"] for r in results)
    total_u_dt = sum(r["unplanned_downtime_minutes"] for r in results)
    total_cnt = sum(r["total_count"] for r in results)
    total_good = sum(r["good_count"] for r in results)
    total_scrap = sum(r["scrap_count"] for r in results)
    total_rework = sum(r["rework_count"] for r in results)

    avail = (total_opt / total_ppt * 100.0) if total_ppt > 0 else 0.0
    qual = (total_good / total_cnt * 100.0) if total_cnt > 0 else 100.0
    perf = sum(r["performance"] for r in results) / len(results) if results else 0.0
    composite_oee = (avail / 100.0) * (min(100.0, perf) / 100.0) * (qual / 100.0) * 100.0

    return OEEDashboardKPI(
        overall_oee=round(composite_oee, 2),
        availability=round(avail, 2),
        performance=round(perf, 2),
        quality=round(qual, 2),
        total_production=total_cnt,
        good_count=total_good,
        scrap_count=total_scrap,
        rework_count=total_rework,
        total_downtime_minutes=round(total_p_dt + total_u_dt, 2),
        planned_downtime_minutes=round(total_p_dt, 2),
        unplanned_downtime_minutes=round(total_u_dt, 2),
        target_oee=85.0,
        active_machines_count=active_machines,
        total_machines_count=total_machines,
        performance_flagged_count=flagged_machines
    )

@router.get("/machine/{machine_id}")
def get_machine_oee(
    machine_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)
    return OEEEngine.calculate_machine_oee(db, machine_id, start_dt, end_dt)

@router.get("/line/{line_id}")
def get_line_oee(
    line_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)
    return OEEEngine.calculate_line_oee(db, line_id, start_dt, end_dt)

@router.get("/trend")
def get_oee_trend(
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns daily time-series of OEE, Availability, Performance, Quality."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days - 1)

    machine_query = db.query(Machine).filter(Machine.is_active == True)
    if machine_id:
        machine_query = machine_query.filter(Machine.id == machine_id)
    elif line_id:
        machine_query = machine_query.filter(Machine.line_id == line_id)
    machines = machine_query.all()

    trend = []
    current_day = start_date
    while current_day <= end_date:
        d_start = datetime.datetime.combine(current_day, datetime.time.min)
        d_end = datetime.datetime.combine(current_day, datetime.time.max)

        day_results = [
            OEEEngine.calculate_machine_oee(db, m.id, d_start, d_end)
            for m in machines
        ]

        if day_results:
            tot_ppt = sum(r["planned_production_time_minutes"] for r in day_results)
            tot_opt = sum(r["operating_time_minutes"] for r in day_results)
            tot_cnt = sum(r["total_count"] for r in day_results)
            tot_good = sum(r["good_count"] for r in day_results)
            avail = (tot_opt / tot_ppt * 100.0) if tot_ppt > 0 else 0.0
            qual = (tot_good / tot_cnt * 100.0) if tot_cnt > 0 else 100.0
            perf = sum(r["performance"] for r in day_results) / len(day_results)
            oee = (avail / 100.0) * (min(100.0, perf) / 100.0) * (qual / 100.0) * 100.0
        else:
            avail = qual = perf = oee = 0.0

        trend.append({
            "date": current_day.isoformat(),
            "availability": round(avail, 2),
            "performance": round(perf, 2),
            "quality": round(qual, 2),
            "oee": round(oee, 2)
        })
        current_day += datetime.timedelta(days=1)

    return trend

@router.get("/by-machine")
def get_oee_by_machine(
    line_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)
    query = db.query(Machine).filter(Machine.is_active == True)
    if line_id:
        query = query.filter(Machine.line_id == line_id)
    machines = query.all()

    output = []
    for m in machines:
        r = OEEEngine.calculate_machine_oee(db, m.id, start_dt, end_dt)
        output.append({
            "machine_id": m.id,
            "machine_code": m.machine_code,
            "machine_name": m.name,
            "line_id": m.line_id,
            "current_status": m.current_status,
            "oee": r["oee"],
            "availability": r["availability"],
            "performance": r["performance"],
            "quality": r["quality"],
            "performance_flagged": r["performance_flagged"]
        })
    return output

@router.get("/by-line")
def get_oee_by_line(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)
    lines = db.query(ProductionLine).filter(ProductionLine.is_active == True).all()
    output = []
    for l in lines:
        r = OEEEngine.calculate_line_oee(db, l.id, start_dt, end_dt)
        output.append({
            "line_id": l.id,
            "line_code": l.line_code,
            "name": l.name,
            "target_oee": r["target_oee"],
            "oee": r["oee"],
            "availability": r["availability"],
            "performance": r["performance"],
            "quality": r["quality"],
            "total_count": r["total_count"],
            "good_count": r["good_count"],
            "scrap_count": r["scrap_count"]
        })
    return output

@router.get("/downtime-reasons")
def get_downtime_by_reason(
    line_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt, end_dt = parse_date_window(start_date, end_date)

    query = db.query(
        DowntimeReason.reason_code,
        DowntimeReason.name,
        DowntimeReason.category,
        DowntimeReason.is_planned,
        func.count(MachineStateEvent.id).label("incident_count"),
        func.sum(MachineStateEvent.duration_seconds).label("total_seconds")
    ).join(
        MachineStateEvent, MachineStateEvent.downtime_reason_id == DowntimeReason.id
    ).filter(
        MachineStateEvent.start_time >= start_dt,
        MachineStateEvent.end_time <= end_dt
    )

    if machine_id:
        query = query.filter(MachineStateEvent.machine_id == machine_id)
    elif line_id:
        query = query.join(Machine, Machine.id == MachineStateEvent.machine_id).filter(Machine.line_id == line_id)

    query = query.group_by(
        DowntimeReason.reason_code,
        DowntimeReason.name,
        DowntimeReason.category,
        DowntimeReason.is_planned
    ).order_by(func.sum(MachineStateEvent.duration_seconds).desc())

    records = query.all()
    total_downtime_sec = sum(r.total_seconds or 0 for r in records)

    results = []
    for r in records:
        sec = float(r.total_seconds or 0)
        pct = (sec / total_downtime_sec * 100.0) if total_downtime_sec > 0 else 0.0
        results.append({
            "reason_code": r.reason_code,
            "name": r.name,
            "category": r.category,
            "is_planned": r.is_planned,
            "incident_count": r.incident_count,
            "duration_minutes": round(sec / 60.0, 2),
            "percentage": round(pct, 2)
        })
    return results
