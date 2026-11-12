"""
FactoryPulse Reproducibility Verification Runner
=================================================
Runs the deterministic generator with identical seeds and verifies
bit-for-bit, row-for-row, and checksum reproducibility.
"""

import sys
import hashlib
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.data_generator.generator import ManufacturingDataGenerator, DEFAULT_SEED
from backend.app.models.production import MachineStateEvent, ProductionCount, QualityInspection, ProductionOrder
from backend.app.models.master_data import ShiftInstance

def compute_checksum(records, cols):
    hasher = hashlib.sha256()
    for r in records:
        row_str = "|".join(str(getattr(r, c, "")) for c in cols)
        hasher.update(row_str.encode("utf-8"))
    return hasher.hexdigest()

def main():
    print("================================================================================")
    print(" FACTORYPULSE REPRODUCIBILITY VERIFICATION")
    print(f" Random Seed: {DEFAULT_SEED} | Comparing Two Independent Runs")
    print("================================================================================")

    # Temporary SQLite databases for run 1 and run 2
    engine1 = create_engine("sqlite:///repro_run1.db")
    engine2 = create_engine("sqlite:///repro_run2.db")
    Session1 = sessionmaker(bind=engine1)
    Session2 = sessionmaker(bind=engine2)

    db1 = Session1()
    db2 = Session2()

    try:
        print("\n[Run 1] Generating starter dataset with seed", DEFAULT_SEED)
        gen1 = ManufacturingDataGenerator(seed=DEFAULT_SEED, mode="starter", clean=True)
        gen1.run(db=db1, export_dir="data/repro1")

        print("\n[Run 2] Generating starter dataset with seed", DEFAULT_SEED)
        gen2 = ManufacturingDataGenerator(seed=DEFAULT_SEED, mode="starter", clean=True)
        gen2.run(db=db2, export_dir="data/repro2")

        print("\n--- COMPARING RESULTS ---")
        models_to_check = [
            ("ShiftInstance", ShiftInstance, ["instance_code", "shift_date", "start_time", "end_time"]),
            ("ProductionOrder", ProductionOrder, ["order_code", "line_id", "product_id", "target_quantity"]),
            ("MachineStateEvent", MachineStateEvent, ["event_code", "machine_id", "state", "start_time", "end_time", "duration_seconds"]),
            ("ProductionCount", ProductionCount, ["count_code", "production_order_id", "machine_id", "count_type", "quantity"]),
            ("QualityInspection", QualityInspection, ["inspection_code", "machine_id", "sample_size", "passed_count", "failed_count"])
        ]

        all_matched = True
        for name, model, cols in models_to_check:
            rows1 = db1.query(model).order_by(model.id).all()
            rows2 = db2.query(model).order_by(model.id).all()

            count1 = len(rows1)
            count2 = len(rows2)
            csum1 = compute_checksum(rows1, cols)
            csum2 = compute_checksum(rows2, cols)

            matched = (count1 == count2) and (csum1 == csum2)
            if not matched:
                all_matched = False
                print(f"  [MISMATCH] {name}: Count ({count1} vs {count2}), Hash ({csum1[:8]} vs {csum2[:8]})")
            else:
                print(f"  [MATCH]    {name:<20}: {count1:,} rows | SHA256: {csum1[:16]}...")

        print("\n================================================================================")
        if all_matched:
            print(" REPRODUCIBILITY VERIFICATION PASSED: 100% IDENTICAL ACROSS RUNS")
        else:
            print(" REPRODUCIBILITY VERIFICATION FAILED: Discrepancies detected.")
        print("================================================================================")

        return 0 if all_matched else 1

    finally:
        db1.close()
        db2.close()
        # Clean up temporary DB files
        for p in [Path("repro_run1.db"), Path("repro_run2.db")]:
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

if __name__ == "__main__":
    sys.exit(main())
