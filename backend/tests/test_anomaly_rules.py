import pytest
import datetime
from backend.app.services.anomaly_detector import AnomalyDetector
from backend.app.models.production import MachineStateEvent, ProductionCount, QualityInspection
from backend.app.models.master_data import Product, Machine, ProductionLine, Plant

def test_rule1_overlapping_event_detected(db):
    """Rule 1: Overlapping state intervals on the same machine must be detected."""
    m = db.query(Machine).first()
    t1 = datetime.datetime(2026, 6, 1, 8, 0, 0)
    t2 = datetime.datetime(2026, 6, 1, 9, 0, 0)
    t_overlap_start = datetime.datetime(2026, 6, 1, 8, 30, 0)
    t_overlap_end = datetime.datetime(2026, 6, 1, 9, 30, 0)

    e1 = MachineStateEvent(
        event_code=f"EVT-TEST-001-{m.id}",
        machine_id=m.id,
        state="RUNNING",
        start_time=t1,
        end_time=t2,
        duration_seconds=3600
    )
    e2 = MachineStateEvent(
        event_code=f"EVT-TEST-002-{m.id}",
        machine_id=m.id,
        state="STOPPED",
        start_time=t_overlap_start,
        end_time=t_overlap_end,
        duration_seconds=3600
    )
    db.add_all([e1, e2])
    db.commit()

    try:
        anomalies = AnomalyDetector.run_detection(db, persist=False)
        types = [a["anomaly_type"] for a in anomalies]
        assert "OVERLAPPING_MACHINE_EVENT" in types
    finally:
        db.delete(e1)
        db.delete(e2)
        db.commit()

def test_rule2_negative_count_without_correction_detected(db):
    """Rule 2: Negative count quantity under non-CORRECTION type is anomalous."""
    m = db.query(Machine).first()
    p = db.query(Product).first()

    bad_count = ProductionCount(
        count_code="CNT-TEST-NEG-001",
        production_order_id=1,
        machine_id=m.id,
        product_id=p.id,
        count_type="GOOD",
        quantity=-20,
        timestamp=datetime.datetime(2026, 6, 1, 12, 0, 0)
    )
    db.add(bad_count)
    db.commit()

    try:
        anomalies = AnomalyDetector.run_detection(db, persist=False)
        matching = [a for a in anomalies if a["anomaly_type"] == "NEGATIVE_COUNT_WITHOUT_CORRECTION"]
        assert len(matching) >= 1
        assert any(a["severity"] == "CRITICAL" for a in matching)
    finally:
        db.delete(bad_count)
        db.commit()

def test_rule3_scrap_exceeds_sample_detected(db):
    """Rule 3: Quality inspection failed_count > sample_size must be flagged."""
    m = db.query(Machine).first()

    bad_qc = QualityInspection(
        inspection_code="QC-TEST-ARITHMETIC-001",
        production_order_id=1,
        machine_id=m.id,
        sample_size=20,
        passed_count=0,
        failed_count=35, # 35 > 20
        defect_type="Crack",
        timestamp=datetime.datetime(2026, 6, 1, 14, 0, 0),
        status="FAILED"
    )
    db.add(bad_qc)
    db.commit()

    try:
        anomalies = AnomalyDetector.run_detection(db, persist=False)
        matching = [a for a in anomalies if a["anomaly_type"] == "SCRAP_EXCEEDS_TOTAL_PRODUCTION"]
        assert len(matching) >= 1
    finally:
        db.delete(bad_qc)
        db.commit()

def test_rule4_incorrect_ideal_cycle_time_detected(db):
    """Rule 4: Ideal cycle time <= 0 must be flagged as anomalous."""
    p_anom = Product(
        product_code="PROD-TEST-NEG-CYC",
        name="Negative Cycle Widget",
        category="Test",
        ideal_cycle_time_seconds=-3.50,
        is_active=True
    )
    db.add(p_anom)
    db.commit()

    try:
        anomalies = AnomalyDetector.run_detection(db, persist=False)
        matching = [a for a in anomalies if a["anomaly_type"] == "INCORRECT_IDEAL_CYCLE_TIME"]
        assert len(matching) >= 1
    finally:
        db.delete(p_anom)
        db.commit()

def test_rule5_downtime_overlapping_break_detected(db):
    """Rule 5: Equipment breakdown reported inside planned BREAK window must be detected."""
    m = db.query(Machine).first()
    brk_start = datetime.datetime(2026, 6, 2, 11, 30, 0)
    brk_end = datetime.datetime(2026, 6, 2, 12, 30, 0)
    dt_start = datetime.datetime(2026, 6, 2, 11, 45, 0)
    dt_end = datetime.datetime(2026, 6, 2, 12, 15, 0)

    e_brk = MachineStateEvent(
        event_code=f"EVT-TEST-BRK-{m.id}",
        machine_id=m.id,
        state="BREAK",
        start_time=brk_start,
        end_time=brk_end,
        duration_seconds=3600
    )
    e_dt = MachineStateEvent(
        event_code=f"EVT-TEST-DT-{m.id}",
        machine_id=m.id,
        state="STOPPED",
        start_time=dt_start,
        end_time=dt_end,
        duration_seconds=1800
    )
    db.add_all([e_brk, e_dt])
    db.commit()

    try:
        anomalies = AnomalyDetector.run_detection(db, persist=False)
        matching = [a for a in anomalies if a["anomaly_type"] == "DOWNTIME_OVERLAPPING_PLANNED_BREAK"]
        assert len(matching) >= 1
    finally:
        db.delete(e_brk)
        db.delete(e_dt)
        db.commit()

def test_no_duplicate_detections(db):
    """Ensures each detected anomaly instance is uniquely cataloged without duplicates."""
    anomalies = AnomalyDetector.run_detection(db, persist=False)
    keys = [(a["anomaly_type"], a["entity_id"], a["timestamp"]) for a in anomalies]
    assert len(keys) == len(set(keys)), "Duplicate anomaly detected in scan output"
