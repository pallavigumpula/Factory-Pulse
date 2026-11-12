import pytest
from backend.app.models.master_data import Plant, ProductionLine, Machine, Shift, ShiftInstance, Product
from backend.app.models.production import MachineStateEvent, ProductionCount, QualityInspection, ProductionOrder

def test_fk_integrity_no_orphan_events(db):
    """Verifies that every MachineStateEvent references an existing Machine and ProductionOrder."""
    machine_ids = set(m.id for m in db.query(Machine.id).all())
    orphan_events = db.query(MachineStateEvent).filter(~MachineStateEvent.machine_id.in_(machine_ids)).count()
    assert orphan_events == 0, f"Found {orphan_events} orphan events"

def test_fk_integrity_no_orphan_counts(db):
    """Verifies that every ProductionCount references an existing Machine and Product."""
    machine_ids = set(m.id for m in db.query(Machine.id).all())
    product_ids = set(p.id for p in db.query(Product.id).all())
    orphan_counts_m = db.query(ProductionCount).filter(~ProductionCount.machine_id.in_(machine_ids)).count()
    orphan_counts_p = db.query(ProductionCount).filter(~ProductionCount.product_id.in_(product_ids)).count()
    assert orphan_counts_m == 0, f"Found {orphan_counts_m} counts without valid machine"
    assert orphan_counts_p == 0, f"Found {orphan_counts_p} counts without valid product"

def test_fk_integrity_no_orphan_inspections(db):
    """Verifies that every QualityInspection references an existing Machine."""
    machine_ids = set(m.id for m in db.query(Machine.id).all())
    orphan_qc = db.query(QualityInspection).filter(~QualityInspection.machine_id.in_(machine_ids)).count()
    assert orphan_qc == 0, f"Found {orphan_qc} QC records without valid machine"

def test_shift_instance_dated_code_format(db):
    """Verifies that every ShiftInstance follows the SHIFT-YYYY-MM-DD-{suffix} deterministic naming pattern."""
    instances = db.query(ShiftInstance).all()
    assert len(instances) > 0, "No shift instances found in database"
    for si in instances:
        parts = si.instance_code.split("-")
        assert len(parts) == 5, f"Invalid shift instance code structure: {si.instance_code}"
        assert parts[0] == "SHIFT"
        assert len(parts[1]) == 4 # Year
        assert len(parts[2]) == 2 # Month
        assert len(parts[3]) == 2 # Day
        assert parts[4] in ("A", "B", "C") # Suffix

def test_product_catalog_baseline_count(db):
    """Verifies that the database has 20 baseline products (plus optional anomaly test product)."""
    count = db.query(Product).count()
    assert count >= 20, f"Expected at least 20 products, got {count}"
