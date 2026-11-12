import csv
import io
import json
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.master_data import Machine, ProductionLine, Product
from backend.app.models.production import ProductionOrder, MachineStateEvent, ProductionCount
from backend.app.models.anomaly import DetectedAnomaly
from backend.app.services.oee_engine import OEEEngine

class ReportService:

    @staticmethod
    def generate_oee_report_data(
        db: Session,
        start_date: datetime.date,
        end_date: datetime.date,
        line_id: Optional[int] = None,
        machine_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)

        q = db.query(Machine).filter(Machine.is_active == True)
        if machine_id:
            q = q.filter(Machine.id == machine_id)
        elif line_id:
            q = q.filter(Machine.line_id == line_id)
        machines = q.all()

        report_rows = []
        for m in machines:
            res = OEEEngine.calculate_machine_oee(db, m.id, start_dt, end_dt)
            report_rows.append({
                "machine_code": m.machine_code,
                "machine_name": m.name,
                "line_code": m.line.line_code if m.line else "N/A",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "planned_production_time_min": res["planned_production_time_minutes"],
                "operating_time_min": res["operating_time_minutes"],
                "planned_downtime_min": res["planned_downtime_minutes"],
                "unplanned_downtime_min": res["unplanned_downtime_minutes"],
                "total_produced": res["total_count"],
                "good_count": res["good_count"],
                "scrap_count": res["scrap_count"],
                "availability_pct": res["availability"],
                "performance_pct": res["performance"],
                "quality_pct": res["quality"],
                "oee_pct": res["oee"],
                "performance_flagged": "YES" if res["performance_flagged"] else "NO"
            })
        return report_rows

    @staticmethod
    def export_csv(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    @staticmethod
    def export_json(rows: List[Dict[str, Any]]) -> str:
        return json.dumps(rows, indent=2, default=str)
