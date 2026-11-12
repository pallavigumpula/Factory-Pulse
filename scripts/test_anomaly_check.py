import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.services.anomaly_detector import AnomalyDetector

def main():
    db = SessionLocal()
    detected = AnomalyDetector.run_detection(db, persist=True)
    print(f"Detected {len(detected)} anomalies.")
    for a in detected:
        print(f" - [{a['severity']}] {a['anomaly_type']}: {a['description']}")

    eval_res = AnomalyDetector.evaluate_against_ground_truth(detected, "data/ground_truth.json")
    print("\nEvaluation Metrics Against Ground Truth:")
    print(" Total Ground Truth Anomalies:", eval_res["total_ground_truth"])
    print(" Total Detected Anomalies:    ", eval_res["total_detected"])
    print(" True Positives:              ", eval_res["true_positives"])
    print(" False Positives:             ", eval_res["false_positives"])
    print(" False Negatives:             ", eval_res["false_negatives"])
    print(" Precision:                   ", eval_res["precision"])
    print(" Recall:                      ", eval_res["recall"])
    print(" F1-Score:                    ", eval_res["f1_score"])
    print("\nPer-Type Breakdown:")
    for t, m in eval_res["by_type"].items():
        print(f"  {t}: P={m['precision']}, R={m['recall']}, F1={m['f1_score']}")
    db.close()

if __name__ == "__main__":
    main()
