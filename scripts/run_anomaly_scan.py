"""
Bootstrap script: runs the anomaly detector against the existing DB and
verifies that all 5 expected anomaly types are found.
"""
import sys
import os
sys.path.insert(0, r'C:\CandidateWorkspace')
os.chdir(r'C:\CandidateWorkspace')

from backend.app.database import SessionLocal
from backend.app.services.anomaly_detector import AnomalyDetector
from backend.app.models.anomaly import DetectedAnomaly

db = SessionLocal()

print("Running anomaly scan (persist=True) ...")
anomalies = AnomalyDetector.run_detection(db, persist=True)
print(f"  → Detected {len(anomalies)} anomalies")

# Verify DB state
count = db.query(DetectedAnomaly).count()
print(f"  → DB detected_anomalies rows: {count}")

print("\nAnomaly types found:")
types_seen = set()
for a in anomalies:
    types_seen.add(a["anomaly_type"])
    print(f"  [{a['severity']:<8}] {a['anomaly_type']:<40} entity={a['entity_id']}")

expected_types = {
    "OVERLAPPING_MACHINE_EVENT",
    "NEGATIVE_COUNT_WITHOUT_CORRECTION",
    "SCRAP_EXCEEDS_TOTAL_PRODUCTION",
    "INCORRECT_IDEAL_CYCLE_TIME",
    "DOWNTIME_OVERLAPPING_PLANNED_BREAK",
}
missing = expected_types - types_seen
if missing:
    print(f"\n⚠ MISSING ANOMALY TYPES: {missing}")
else:
    print(f"\n✅ All 5 anomaly type categories detected.")

# Evaluate against ground truth
import json
gt_path = r"C:\CandidateWorkspace\data\ground_truth.json"
detected_list = [
    {"anomaly_type": a["anomaly_type"], "entity_id": a["entity_id"], "severity": a["severity"]}
    for a in anomalies
]
metrics = AnomalyDetector.evaluate_against_ground_truth(detected_list, gt_path)
print("\n--- Ground Truth Evaluation ---")
print(f"  Total detected (unique keys): {metrics['total_detected']}")
print(f"  Total ground truth:           {metrics['total_ground_truth']}")
print(f"  True Positives:               {metrics['true_positives']}")
print(f"  False Positives:              {metrics['false_positives']}")
print(f"  False Negatives:              {metrics['false_negatives']}")
print(f"  Precision:                    {metrics['precision']:.4f}")
print(f"  Recall:                       {metrics['recall']:.4f}")
print(f"  F1-score:                     {metrics['f1_score']:.4f}")

for t, v in metrics["by_type"].items():
    tp, fp, fn = v["tp"], v["fp"], v["fn"]
    status = "✅" if tp >= 1 and fn == 0 else "❌"
    print(f"  {status} {t}: TP={tp} FP={fp} FN={fn}")

db.close()
