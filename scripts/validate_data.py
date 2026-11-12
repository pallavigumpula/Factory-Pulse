"""
FactoryPulse Data Validation Runner
====================================
Executes the comprehensive data validation pipeline and outputs structured results.
"""

import sys
import json
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.services.data_validator import DataValidator

def main():
    print("================================================================================")
    print(" FACTORYPULSE DATA INTEGRITY & VALIDATION PIPELINE")
    print("================================================================================")

    db = SessionLocal()
    try:
        report = DataValidator.run_full_validation(db)

        print("\n--- ENTITY INVENTORY ---")
        for entity, count in report["entity_counts"].items():
            print(f"  {entity:<25}: {count:,}")

        print("\n--- VALIDATION CHECKS ---")
        print(f"  Total Checks Run    : {report['checks_run']}")
        print(f"  Checks Passed       : {report['checks_passed']}")
        print(f"  Checks Failed       : {report['checks_failed']}")
        print(f"  Pass Rate           : {report['summary']['pass_rate']}")
        print(f"  Overall Status      : {report['overall_status']}")

        if report["issues"]:
            print("\n--- ISSUES DETECTED ---")
            for issue in report["issues"]:
                print(f"  [FAIL] {issue['check']}: {issue['details']}")
        else:
            print("\n  [ALL CHECKS PASSED] No relational, chronometric, or arithmetic defects found.")

        # Save report to docs/
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        out_file = docs_dir / "validation_report.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport written to {out_file}")

        return 0 if report["checks_failed"] == 0 else 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
