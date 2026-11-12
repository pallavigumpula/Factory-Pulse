import pytest
import datetime
from backend.app.services.oee_engine import OEEEngine
from backend.app.services.data_validator import DataValidator
from backend.app.models.production import MachineStateEvent, ProductionCount, QualityInspection, ProductionOrder
from backend.app.models.master_data import Machine, Shift, Plant, Product, ShiftInstance

def test_data_validation_pipeline_passes(db):
    """Runs the full DataValidator on the database and verifies pass rate."""
    report = DataValidator.run_full_validation(db)
    assert report["checks_run"] >= 15
    assert report["summary"]["pass_rate"] == "100.0%"
    assert len(report["issues"]) == 0

def test_oee_zero_production_returns_na_quality(db):
    """When operating time > 0 but total production is 0, quality must be None / N/A, not 100%."""
    m = db.query(Machine).first()
    t_start = datetime.datetime(2026, 7, 1, 6, 0, 0)
    t_end = datetime.datetime(2026, 7, 1, 14, 0, 0)

    # Add a RUNNING event
    evt = MachineStateEvent(
        event_code=f"EVT-TEST-RUN-{m.id}",
        machine_id=m.id,
        state="RUNNING",
        start_time=t_start,
        end_time=t_end,
        duration_seconds=28800
    )
    db.add(evt)
    db.commit()

    try:
        res = OEEEngine.calculate_machine_oee(db, m.id, t_start, t_end)
        assert res["total_count"] == 0
        # Must NOT show 100% quality when production is zero
        assert res["quality"] is None
        assert res["quality_display"] == "N/A"
        assert res["oee"] == 0.0
    finally:
        db.delete(evt)
        db.commit()

def test_oee_zero_operating_time_handled_safely(db):
    """When machine has zero operating time, availability, performance, and OEE must be 0 without division error."""
    m = db.query(Machine).first()
    t_start = datetime.datetime(2026, 7, 2, 6, 0, 0)
    t_end = datetime.datetime(2026, 7, 2, 14, 0, 0)

    # Entire shift in STOPPED state
    evt = MachineStateEvent(
        event_code=f"EVT-TEST-STOP-{m.id}",
        machine_id=m.id,
        state="STOPPED",
        start_time=t_start,
        end_time=t_end,
        duration_seconds=28800
    )
    db.add(evt)
    db.commit()

    try:
        res = OEEEngine.calculate_machine_oee(db, m.id, t_start, t_end)
        assert res["operating_time_minutes"] == 0.0
        assert res["availability"] == 0.0
        assert res["performance"] == 0.0
        assert res["oee"] == 0.0
    finally:
        db.delete(evt)
        db.commit()

def test_oee_performance_capping_and_flag(db):
    """When production exceeds theoretical speed, performance > 100% is preserved but flagged and capped in OEE."""
    m = db.query(Machine).first()
    p = db.query(Product).first()
    po = db.query(ProductionOrder).first()

    t_start = datetime.datetime(2026, 7, 3, 8, 0, 0)
    t_end = datetime.datetime(2026, 7, 3, 9, 0, 0) # 1 hour = 3600 sec

    # 1 hour running
    evt = MachineStateEvent(
        event_code=f"EVT-TEST-PERF-{m.id}",
        machine_id=m.id,
        state="RUNNING",
        start_time=t_start,
        end_time=t_end,
        duration_seconds=3600
    )
    db.add(evt)

    cnt = ProductionCount(
        count_code="CNT-TEST-OVERPERF-001",
        production_order_id=po.id,
        machine_id=m.id,
        product_id=p.id,
        count_type="GOOD",
        quantity=500,
        timestamp=t_start + datetime.timedelta(minutes=30)
    )
    db.add(cnt)
    db.commit()

    try:
        res = OEEEngine.calculate_machine_oee(db, m.id, t_start, t_end)
        assert res["performance"] > 100.0
        assert res["performance_flagged"] is True
        # Composite OEE must not exceed 100%
        assert 0.0 <= res["oee"] <= 100.0
    finally:
        db.delete(cnt)
        db.delete(evt)
        db.commit()

def test_shift_oee_aggregation(db):
    """Tests that calculate_shift_oee aggregates correctly across machines."""
    shift = db.query(Shift).first()
    t_start = datetime.datetime(2026, 1, 1, 0, 0, 0)
    t_end = datetime.datetime(2026, 1, 5, 23, 59, 59)

    res = OEEEngine.calculate_shift_oee(db, shift.id, t_start, t_end)
    assert "oee" in res
    assert "availability" in res
    assert "performance" in res
    assert res["shift_id"] == shift.id
    assert 0.0 <= res["oee"] <= 100.0

def test_plant_oee_aggregation(db):
    """Tests that calculate_plant_oee aggregates lines correctly."""
    plant = db.query(Plant).first()
    t_start = datetime.datetime(2026, 1, 1, 0, 0, 0)
    t_end = datetime.datetime(2026, 1, 5, 23, 59, 59)

    res = OEEEngine.calculate_plant_oee(db, plant.id, t_start, t_end)
    assert "oee" in res
    assert "lines" in res
    assert res["plant_id"] == plant.id
    assert 0.0 <= res["oee"] <= 100.0

def test_product_oee_aggregation(db):
    """Tests that calculate_product_oee computes product-level efficiency."""
    prod = db.query(Product).filter(Product.product_code != "PROD-ANOM").first()
    t_start = datetime.datetime(2026, 1, 1, 0, 0, 0)
    t_end = datetime.datetime(2026, 1, 5, 23, 59, 59)

    res = OEEEngine.calculate_product_oee(db, prod.id, t_start, t_end)
    assert "oee" in res
    assert res["product_code"] == prod.product_code
    assert 0.0 <= res["oee"] <= 100.0
