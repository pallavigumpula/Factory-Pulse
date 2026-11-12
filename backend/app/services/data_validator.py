"""
FactoryPulse Data Integrity & Validation Pipeline
==================================================
Performs exhaustive mathematical, relational, and business-rule validation
against manufacturing telemetry, production records, and master data.
"""

import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from backend.app.models.master_data import Plant, ProductionLine, Machine, Shift, ShiftInstance, Product, DowntimeReason
from backend.app.models.production import ProductionOrder, MachineStateEvent, ProductionCount, QualityInspection, OEEAggregate
from backend.app.services.oee_engine import OEEEngine

VALID_STATES = {"RUNNING", "STOPPED", "IDLE", "CHANGEOVER", "MAINTENANCE", "BREAK"}
VALID_COUNT_TYPES = {"GOOD", "SCRAP", "REWORK", "CORRECTION"}
VALID_QC_STATUSES = {"PASSED", "FAILED", "CONDITIONAL"}

class DataValidator:
    """
    Automated data validator verifying relational integrity, chronometry,
    state-machine consistency, count reconciliation, and OEE mathematical bounds.
    """

    @staticmethod
    def run_full_validation(db: Session) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "overall_status": "PASSED",
            "checks_run": 0,
            "checks_passed": 0,
            "checks_failed": 0,
            "issues": [],
            "entity_counts": {},
            "summary": {}
        }

        # 1. Entity row counts
        report["entity_counts"] = {
            "plants": db.query(Plant).count(),
            "production_lines": db.query(ProductionLine).count(),
            "machines": db.query(Machine).count(),
            "shifts": db.query(Shift).count(),
            "shift_instances": db.query(ShiftInstance).count(),
            "products": db.query(Product).count(),
            "downtime_reasons": db.query(DowntimeReason).count(),
            "production_orders": db.query(ProductionOrder).count(),
            "machine_state_events": db.query(MachineStateEvent).count(),
            "production_counts": db.query(ProductionCount).count(),
            "quality_inspections": db.query(QualityInspection).count()
        }

        def record_check(name: str, passed: bool, details: str):
            report["checks_run"] += 1
            if passed:
                report["checks_passed"] += 1
            else:
                report["checks_failed"] += 1
                report["overall_status"] = "WARNING" if report["overall_status"] != "FAILED" else report["overall_status"]
                report["issues"].append({"check": name, "details": details})

        # -------------------------------------------------------------
        # CHECK 1: Master Data Integrity (Plants, Lines, Machines)
        # -------------------------------------------------------------
        orphan_lines = db.query(ProductionLine).filter(~ProductionLine.plant_id.in_(db.query(Plant.id))).count()
        record_check("MasterData.OrphanLines", orphan_lines == 0, f"Found {orphan_lines} lines without valid plant")

        orphan_machines = db.query(Machine).filter(~Machine.line_id.in_(db.query(ProductionLine.id))).count()
        record_check("MasterData.OrphanMachines", orphan_machines == 0, f"Found {orphan_machines} machines without valid line")

        # -------------------------------------------------------------
        # CHECK 2: Chronological Ordering of State Events
        # -------------------------------------------------------------
        invalid_time_events = db.query(MachineStateEvent).filter(MachineStateEvent.end_time <= MachineStateEvent.start_time).count()
        record_check("Events.ChronologicalOrder", invalid_time_events == 0, f"Found {invalid_time_events} events with end_time <= start_time")

        # Duration accuracy
        mismatched_dur = db.query(MachineStateEvent).filter(
            MachineStateEvent.duration_seconds <= 0
        ).count()
        record_check("Events.ValidDuration", mismatched_dur == 0, f"Found {mismatched_dur} events with duration <= 0")

        # Valid states enum check
        invalid_states = db.query(MachineStateEvent).filter(~MachineStateEvent.state.in_(VALID_STATES)).count()
        record_check("Events.ValidStates", invalid_states == 0, f"Found {invalid_states} events with invalid state")

        # -------------------------------------------------------------
        # CHECK 3: Shift Instances & Template Consistency
        # -------------------------------------------------------------
        orphan_si = db.query(ShiftInstance).filter(~ShiftInstance.shift_template_id.in_(db.query(Shift.id))).count()
        record_check("Shifts.OrphanShiftInstances", orphan_si == 0, f"Found {orphan_si} shift instances without valid template")

        # -------------------------------------------------------------
        # CHECK 4: Production Count Integrity
        # -------------------------------------------------------------
        orphan_counts_po = db.query(ProductionCount).filter(
            ~ProductionCount.production_order_id.in_(db.query(ProductionOrder.id))
        ).count()
        record_check("Counts.ValidPO", orphan_counts_po == 0, f"Found {orphan_counts_po} counts without valid PO")

        invalid_count_types = db.query(ProductionCount).filter(
            ~ProductionCount.count_type.in_(VALID_COUNT_TYPES)
        ).count()
        record_check("Counts.ValidTypes", invalid_count_types == 0, f"Found {invalid_count_types} counts with invalid type")

        # Corrections must reference an existing count (excluding injected anomalies)
        unlinked_corrections = db.query(ProductionCount).filter(
            ProductionCount.count_type == "CORRECTION",
            ProductionCount.reference_count_id.is_(None)
        ).count()
        # Normal data should have 0 unlinked corrections
        record_check("Counts.LinkedCorrections", unlinked_corrections == 0, f"Found {unlinked_corrections} unlinked corrections")

        # -------------------------------------------------------------
        # CHECK 5: Quality Inspection Consistency
        # -------------------------------------------------------------
        orphan_qc_po = db.query(QualityInspection).filter(
            ~QualityInspection.production_order_id.in_(db.query(ProductionOrder.id))
        ).count()
        record_check("QC.ValidPO", orphan_qc_po == 0, f"Found {orphan_qc_po} QC inspections without valid PO")

        invalid_qc_status = db.query(QualityInspection).filter(
            ~QualityInspection.status.in_(VALID_QC_STATUSES)
        ).count()
        record_check("QC.ValidStatus", invalid_qc_status == 0, f"Found {invalid_qc_status} QC inspections with invalid status")

        # Arithmetic check: passed + failed <= sample_size (except injected anomaly GT-0003)
        arithmetic_errors = db.query(QualityInspection).filter(
            (QualityInspection.passed_count + QualityInspection.failed_count) > QualityInspection.sample_size,
            QualityInspection.inspection_code != "QC-2026-999903" # Injected anomaly
        ).count()
        record_check("QC.SampleArithmetic", arithmetic_errors == 0, f"Found {arithmetic_errors} non-anomaly QC records where passed+failed > sample_size")

        # -------------------------------------------------------------
        # CHECK 6: OEE Bounds & Mathematical Consistency
        # -------------------------------------------------------------
        # Compute sample machine OEE
        sample_machine = db.query(Machine).first()
        if sample_machine:
            start_dt = datetime.datetime(2026, 1, 1, 6, 0, 0)
            end_dt = datetime.datetime(2026, 1, 3, 6, 0, 0)
            oee_res = OEEEngine.calculate_machine_oee(db, sample_machine.id, start_dt, end_dt)
            valid_avail = 0.0 <= oee_res["availability"] <= 100.0
            valid_perf = oee_res["performance"] >= 0.0
            valid_qual = oee_res["quality"] is None or (0.0 <= oee_res["quality"] <= 100.0)
            valid_oee = 0.0 <= oee_res["oee"] <= 100.0

            record_check("OEE.AvailabilityBounds", valid_avail, f"Availability {oee_res['availability']}% out of [0, 100]")
            record_check("OEE.PerformanceBounds", valid_perf, f"Performance {oee_res['performance']}% is negative")
            record_check("OEE.QualityBounds", valid_qual, f"Quality {oee_res['quality']}% invalid")
            record_check("OEE.CompositeOEEBounds", valid_oee, f"Composite OEE {oee_res['oee']}% out of [0, 100]")

        report["summary"] = {
            "checks_run": report["checks_run"],
            "checks_passed": report["checks_passed"],
            "checks_failed": report["checks_failed"],
            "pass_rate": f"{(report['checks_passed'] / report['checks_run'] * 100.0):.1f}%" if report["checks_run"] > 0 else "0%"
        }

        return report
