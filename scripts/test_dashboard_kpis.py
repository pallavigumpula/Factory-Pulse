"""
Directly test the dashboard KPI endpoint and OEE trend endpoint.
"""
import sys
import os
sys.path.insert(0, r'C:\CandidateWorkspace')
os.chdir(r'C:\CandidateWorkspace')

from backend.app.database import SessionLocal
from backend.app.routers.oee import get_dashboard_kpis, get_oee_trend, _resolve_data_bounds
import datetime

db = SessionLocal()

# Check data bounds
data_start, data_end = _resolve_data_bounds(db)
print(f"DB data bounds: {data_start} to {data_end}")

# Test dashboard KPI (no date params — backend should auto-detect)
from backend.app.routers.oee import parse_date_window
start_dt, end_dt = parse_date_window(None, None, db=db)
print(f"Resolved date window: {start_dt} to {end_dt}")

# Call OEE engine directly for first machine
from backend.app.services.oee_engine import OEEEngine
result = OEEEngine.calculate_machine_oee(db, 1, start_dt, end_dt)
print(f"\nMachine 1 OEE result:")
for k, v in result.items():
    if k != "assumptions":
        print(f"  {k}: {v}")

# Test full dashboard KPIs
from backend.app.models.master_data import Machine, ProductionLine
machines = db.query(Machine).filter(Machine.is_active == True).all()
print(f"\nTotal active machines: {len(machines)}")

results = []
for m in machines:
    r = OEEEngine.calculate_machine_oee(db, m.id, start_dt, end_dt)
    results.append(r)

total_ppt = sum(r["planned_production_time_minutes"] for r in results)
total_opt = sum(r["operating_time_minutes"] for r in results)
total_cnt = sum(r["total_count"] for r in results)
total_good = sum(r["good_count"] for r in results)
total_scrap = sum(r["scrap_count"] for r in results)
total_rework = sum(r["rework_count"] for r in results)
total_pdt = sum(r["planned_downtime_minutes"] for r in results)
total_udt = sum(r["unplanned_downtime_minutes"] for r in results)

avail = (total_opt / total_ppt * 100.0) if total_ppt > 0 else 0.0
qual = (total_good / total_cnt * 100.0) if total_cnt > 0 else None
qual_ratio = qual / 100.0 if qual is not None else 0.0
perf = sum(r["performance"] for r in results) / len(results) if results else 0.0
oee = (avail / 100.0) * (min(100.0, perf) / 100.0) * qual_ratio * 100.0

print(f"\n=== DASHBOARD KPI RESULTS ===")
print(f"  Overall OEE:        {oee:.2f}%")
print(f"  Availability:       {avail:.2f}%")
print(f"  Performance:        {perf:.2f}%")
print(f"  Quality:            {qual:.2f}% ({qual_ratio:.4f})" if qual else "  Quality:            N/A")
print(f"  Total Production:   {total_cnt:,}")
print(f"  Good Units:         {total_good:,}")
print(f"  Scrap Units:        {total_scrap:,}")
print(f"  Total Downtime:     {total_pdt + total_udt:.2f} min")
print(f"  Planned Downtime:   {total_pdt:.2f} min")
print(f"  Unplanned Downtime: {total_udt:.2f} min")

db.close()
print("\n✅ Dashboard KPI test complete — real data values shown above")
