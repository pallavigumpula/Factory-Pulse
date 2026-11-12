import os
import json
import csv
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.app.models.master_data import Machine, Product, Shift
from backend.app.models.production import MachineStateEvent, ProductionCount, ProductionOrder, QualityInspection
from backend.app.models.anomaly import DetectedAnomaly
from backend.app.utils.identifiers import generate_anomaly_code

class AnomalyDetector:
    """
    Deterministic Anomaly Detection Engine.
    Scans database records, flags anomalies, and measures evaluation metrics.
    """

    @staticmethod
    def run_detection(db: Session, persist: bool = True) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        counter = 1

        # -------------------------------------------------------------
        # Rule 1: Overlapping machine-state events
        # -------------------------------------------------------------
        machines = db.query(Machine).all()
        for m in machines:
            events = db.query(MachineStateEvent).filter(
                MachineStateEvent.machine_id == m.id
            ).order_by(MachineStateEvent.start_time.asc()).all()

            for i in range(len(events) - 1):
                cur = events[i]
                nxt = events[i + 1]
                if nxt.start_time < cur.end_time:
                    anom = {
                        "anomaly_code": generate_anomaly_code(counter),
                        "anomaly_type": "OVERLAPPING_MACHINE_EVENT",
                        "entity_type": "MACHINE",
                        "entity_id": m.machine_code,
                        "timestamp": nxt.start_time,
                        "severity": "HIGH",
                        "description": f"Machine {m.machine_code} has overlapping events: {cur.event_code} ({cur.state}, {cur.start_time.strftime('%H:%M:%S')}-{cur.end_time.strftime('%H:%M:%S')}) and {nxt.event_code} ({nxt.state}, {nxt.start_time.strftime('%H:%M:%S')}-{nxt.end_time.strftime('%H:%M:%S')}).",
                        "expected_value": f"Event start >= previous end ({cur.end_time.isoformat()})",
                        "actual_value": f"Event started at {nxt.start_time.isoformat()}",
                        "recommended_action": "Check PLC event logger synchronization and sensor debounce settings.",
                        "resolution_status": "OPEN"
                    }
                    anomalies.append(anom)
                    counter += 1

        # -------------------------------------------------------------
        # Rule 2: Production count decrease without a correction event
        # -------------------------------------------------------------
        pos = db.query(ProductionOrder).all()
        for po in pos:
            counts = db.query(ProductionCount).filter(
                ProductionCount.production_order_id == po.id
            ).order_by(ProductionCount.timestamp.asc()).all()

            running_total = 0
            for c in counts:
                if c.count_type in ("GOOD", "SCRAP", "REWORK"):
                    if c.quantity < 0:
                        anom = {
                            "anomaly_code": generate_anomaly_code(counter),
                            "anomaly_type": "NEGATIVE_COUNT_WITHOUT_CORRECTION",
                            "entity_type": "PRODUCTION_ORDER",
                            "entity_id": po.order_code,
                            "timestamp": c.timestamp,
                            "severity": "CRITICAL",
                            "description": f"Production order {po.order_code} recorded negative quantity ({c.quantity}) under count type '{c.count_type}'. Count reductions must use count_type 'CORRECTION'.",
                            "expected_value": "quantity >= 0 or count_type == 'CORRECTION'",
                            "actual_value": f"quantity = {c.quantity}, count_type = {c.count_type}",
                            "recommended_action": "Re-submit correction using explicit /production-counts/correct endpoint with reference_count_id.",
                            "resolution_status": "OPEN"
                        }
                        anomalies.append(anom)
                        counter += 1
                    running_total += c.quantity
                elif c.count_type == "CORRECTION":
                    if not c.reference_count_id:
                        anom = {
                            "anomaly_code": generate_anomaly_code(counter),
                            "anomaly_type": "UNLINKED_CORRECTION_EVENT",
                            "entity_type": "PRODUCTION_ORDER",
                            "entity_id": po.order_code,
                            "timestamp": c.timestamp,
                            "severity": "HIGH",
                            "description": f"Correction event {c.count_code} on order {po.order_code} does not reference an original count record.",
                            "expected_value": "reference_count_id NOT NULL",
                            "actual_value": "reference_count_id IS NULL",
                            "recommended_action": "Audit correction log and populate reference_count_id for traceability.",
                            "resolution_status": "OPEN"
                        }
                        anomalies.append(anom)
                        counter += 1
                    running_total += c.quantity

        # -------------------------------------------------------------
        # Rule 3: Scrap quantity exceeds total production quantity
        # -------------------------------------------------------------
        inspections = db.query(QualityInspection).all()
        for qc in inspections:
            if qc.failed_count > qc.sample_size:
                anom = {
                    "anomaly_code": generate_anomaly_code(counter),
                    "anomaly_type": "SCRAP_EXCEEDS_TOTAL_PRODUCTION",
                    "entity_type": "QUALITY_INSPECTION",
                    "entity_id": qc.inspection_code,
                    "timestamp": qc.timestamp,
                    "severity": "CRITICAL",
                    "description": f"Inspection {qc.inspection_code} recorded {qc.failed_count} defects out of sample size {qc.sample_size}.",
                    "expected_value": f"failed_count <= sample_size ({qc.sample_size})",
                    "actual_value": f"failed_count = {qc.failed_count}",
                    "recommended_action": "Quarantine affected lot and recalibrate optical/manual testing station.",
                    "resolution_status": "OPEN"
                }
                anomalies.append(anom)
                counter += 1

        # -------------------------------------------------------------
        # Rule 4: Incorrect ideal cycle time for a product
        # -------------------------------------------------------------
        products = db.query(Product).all()
        for p in products:
            if p.ideal_cycle_time_seconds <= 0:
                anom = {
                    "anomaly_code": generate_anomaly_code(counter),
                    "anomaly_type": "INCORRECT_IDEAL_CYCLE_TIME",
                    "entity_type": "PRODUCT",
                    "entity_id": p.product_code,
                    "timestamp": p.created_at,
                    "severity": "HIGH",
                    "description": f"Product {p.product_code} ({p.name}) has an invalid ideal cycle time of {p.ideal_cycle_time_seconds}s.",
                    "expected_value": "ideal_cycle_time_seconds > 0.0",
                    "actual_value": str(p.ideal_cycle_time_seconds),
                    "recommended_action": "Conduct engineering time study and update product ideal cycle time in Master Data.",
                    "resolution_status": "OPEN"
                }
                anomalies.append(anom)
                counter += 1

        # -------------------------------------------------------------
        # Rule 5: Downtime overlapping a planned break
        # -------------------------------------------------------------
        downtime_events = db.query(MachineStateEvent).filter(
            MachineStateEvent.state.in_(["STOPPED", "MAINTENANCE"])
        ).all()
        break_events = db.query(MachineStateEvent).filter(
            MachineStateEvent.state == "BREAK"
        ).all()

        breaks_by_machine: Dict[int, List[MachineStateEvent]] = {}
        for brk in break_events:
            breaks_by_machine.setdefault(brk.machine_id, []).append(brk)

        for dt in downtime_events:
            machine_breaks = breaks_by_machine.get(dt.machine_id, [])
            for brk in machine_breaks:
                # Check overlap
                if dt.start_time < brk.end_time and brk.start_time < dt.end_time:
                    anom = {
                        "anomaly_code": generate_anomaly_code(counter),
                        "anomaly_type": "DOWNTIME_OVERLAPPING_PLANNED_BREAK",
                        "entity_type": "MACHINE",
                        "entity_id": str(dt.machine_id),
                        "timestamp": dt.start_time,
                        "severity": "MEDIUM",
                        "description": f"Downtime event {dt.event_code} ({dt.state}) overlaps with planned break event {brk.event_code}.",
                        "expected_value": "Machine in state BREAK during statutory shift break interval",
                        "actual_value": f"Machine state recorded as {dt.state}",
                        "recommended_action": "Clip downtime duration to exclude statutory lunch/break period.",
                        "resolution_status": "OPEN"
                    }
                    anomalies.append(anom)
                    counter += 1
                    break # Flag once per downtime event

        if persist:
            # Clear old open anomalies to refresh with fresh scans
            db.query(DetectedAnomaly).delete()
            for anom_data in anomalies:
                db_anom = DetectedAnomaly(
                    anomaly_code=anom_data["anomaly_code"],
                    anomaly_type=anom_data["anomaly_type"],
                    entity_type=anom_data["entity_type"],
                    entity_id=anom_data["entity_id"],
                    timestamp=anom_data["timestamp"],
                    severity=anom_data["severity"],
                    description=anom_data["description"],
                    expected_value=anom_data["expected_value"],
                    actual_value=anom_data["actual_value"],
                    recommended_action=anom_data["recommended_action"],
                    resolution_status=anom_data["resolution_status"]
                )
                db.add(db_anom)
            db.commit()

        return anomalies

    @staticmethod
    def evaluate_against_ground_truth(detected: List[Dict[str, Any]], ground_truth_file: str) -> Dict[str, Any]:
        """
        Calculates Precision, Recall, and F1-score against ground-truth labels.
        Labels are evaluated by (anomaly_type, entity_id).
        """
        if not os.path.exists(ground_truth_file):
            return {
                "total_detected": len(detected),
                "total_ground_truth": 0,
                "true_positives": 0,
                "false_positives": len(detected),
                "false_negatives": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "by_type": {}
            }

        with open(ground_truth_file, "r", encoding="utf-8") as f:
            if ground_truth_file.endswith(".json"):
                gt_list = json.load(f)
            else:
                reader = csv.DictReader(f)
                gt_list = list(reader)

        # Build ground truth key set
        # Key: (anomaly_type, entity_id)
        gt_keys = set()
        by_type_gt: Dict[str, int] = {}
        for item in gt_list:
            k = (item["anomaly_type"], str(item["entity_id"]))
            gt_keys.add(k)
            t = item["anomaly_type"]
            by_type_gt[t] = by_type_gt.get(t, 0) + 1

        detected_keys = set()
        by_type_det: Dict[str, int] = {}
        for item in detected:
            k = (item["anomaly_type"], str(item["entity_id"]))
            detected_keys.add(k)
            t = item["anomaly_type"]
            by_type_det[t] = by_type_det.get(t, 0) + 1

        true_positives = len(detected_keys.intersection(gt_keys))
        false_positives = len(detected_keys - gt_keys)
        false_negatives = len(gt_keys - detected_keys)

        precision = (true_positives / (true_positives + false_positives)) if (true_positives + false_positives) > 0 else 0.0
        recall = (true_positives / (true_positives + false_negatives)) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        all_types = set(list(by_type_gt.keys()) + list(by_type_det.keys()))
        type_breakdown = {}
        for t in all_types:
            det_sub = {k for k in detected_keys if k[0] == t}
            gt_sub = {k for k in gt_keys if k[0] == t}
            tp_sub = len(det_sub.intersection(gt_sub))
            fp_sub = len(det_sub - gt_sub)
            fn_sub = len(gt_sub - det_sub)
            p_sub = (tp_sub / (tp_sub + fp_sub)) if (tp_sub + fp_sub) > 0 else 0.0
            r_sub = (tp_sub / (tp_sub + fn_sub)) if (tp_sub + fn_sub) > 0 else 0.0
            f1_sub = (2 * p_sub * r_sub / (p_sub + r_sub)) if (p_sub + r_sub) > 0 else 0.0
            type_breakdown[t] = {
                "detected": len(det_sub),
                "ground_truth": len(gt_sub),
                "tp": tp_sub,
                "fp": fp_sub,
                "fn": fn_sub,
                "precision": round(p_sub, 4),
                "recall": round(r_sub, 4),
                "f1_score": round(f1_sub, 4)
            }

        return {
            "total_detected": len(detected_keys),
            "total_ground_truth": len(gt_keys),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "by_type": type_breakdown
        }
