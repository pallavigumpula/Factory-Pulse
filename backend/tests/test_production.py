import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from backend.app.schemas.production import (
    ProductionOrderCreate, MachineStateEventCreate,
    ProductionCountCreate, ProductionCountCorrectionCreate,
    QualityInspectionCreate
)
from backend.app.routers.production_orders import create_production_order, list_production_orders
from backend.app.routers.machine_events import create_machine_event
from backend.app.routers.production_counts import record_production_count, correct_production_count, list_production_counts
from backend.app.routers.quality_inspections import create_quality_inspection

def test_production_order_creation(db, planner_user):
    po_in = ProductionOrderCreate(
        line_id=1,
        product_id=1,
        target_quantity=500
    )
    po = create_production_order(po_in, db=db, planner=planner_user)
    assert po.id is not None
    assert po.target_quantity == 500
    assert po.order_code.startswith("PO-")

def test_machine_event_validation_and_status_update(db, operator_user):
    now = datetime.utcnow()
    past = now - timedelta(minutes=20)

    # Invalid timestamp: start > end
    inv_in = MachineStateEventCreate(
        machine_id=1,
        state="RUNNING",
        start_time=now,
        end_time=past
    )
    with pytest.raises(HTTPException) as excinfo:
        create_machine_event(inv_in, db=db, user=operator_user)
    assert excinfo.value.status_code == 400

    # Valid event updates machine current_status
    val_in = MachineStateEventCreate(
        machine_id=1,
        state="STOPPED",
        start_time=past,
        end_time=now,
        notes="Testing machine stop"
    )
    evt = create_machine_event(val_in, db=db, user=operator_user)
    assert evt.duration_seconds == 1200
    assert evt.state == "STOPPED"

def test_traceable_count_correction(db, operator_user):
    # 1. Record normal GOOD count
    count_in = ProductionCountCreate(
        production_order_id=1,
        machine_id=1,
        product_id=1,
        count_type="GOOD",
        quantity=100,
        timestamp=datetime.utcnow()
    )
    orig = record_production_count(count_in, db=db, user=operator_user)
    assert orig.quantity == 100

    # 2. Record explicit traceable correction
    corr_in = ProductionCountCorrectionCreate(
        reference_count_id=orig.id,
        corrected_quantity_delta=-10,
        reason="Sensor reflection bounce duplicate"
    )
    corr = correct_production_count(corr_in, db=db, user=operator_user)
    assert corr.count_type == "CORRECTION"
    assert corr.quantity == -10
    assert corr.reference_count_id == orig.id

    # 3. Verify original count was NOT modified
    counts = list_production_counts(production_order_id=1, db=db, current_user=operator_user)
    checked_orig = next(c for c in counts if c.id == orig.id)
    assert checked_orig.quantity == 100 # Preserved for full audit trail!

def test_quality_inspection_validation(db, qc_user):
    # Failed + Passed > Sample Size must raise 400
    inv_qc = QualityInspectionCreate(
        production_order_id=1,
        machine_id=1,
        sample_size=30,
        passed_count=20,
        failed_count=20, # 20 + 20 = 40 > 30
        status="FAILED",
        timestamp=datetime.utcnow()
    )
    with pytest.raises(HTTPException) as excinfo:
        create_quality_inspection(inv_qc, db=db, user=qc_user)
    assert excinfo.value.status_code == 400
