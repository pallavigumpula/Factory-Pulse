import pytest
import os
from backend.app.services.anomaly_detector import AnomalyDetector

def test_anomaly_scanner_and_evaluation(db):
    detected = AnomalyDetector.run_detection(db, persist=True)
    assert len(detected) >= 5

    types = {a["anomaly_type"] for a in detected}
    # Verify the 5 core required anomaly types are detected
    assert "OVERLAPPING_MACHINE_EVENT" in types
    assert "NEGATIVE_COUNT_WITHOUT_CORRECTION" in types
    assert "SCRAP_EXCEEDS_TOTAL_PRODUCTION" in types
    assert "INCORRECT_IDEAL_CYCLE_TIME" in types
    assert "DOWNTIME_OVERLAPPING_PLANNED_BREAK" in types

    # Evaluate against ground truth
    gt_file = "data/ground_truth.json"
    if os.path.exists(gt_file):
        eval_metrics = AnomalyDetector.evaluate_against_ground_truth(detected, gt_file)
        assert eval_metrics["precision"] > 0.0
        assert eval_metrics["recall"] > 0.0
        assert eval_metrics["f1_score"] > 0.0
