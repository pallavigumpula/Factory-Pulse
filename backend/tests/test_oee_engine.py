import pytest
from datetime import datetime, timedelta
from backend.app.services.oee_engine import OEEEngine, merge_time_intervals, calculate_merged_seconds

def test_interval_merging_logic():
    base = datetime(2026, 1, 1, 10, 0, 0)
    # Overlapping spans: 10:00-10:30 and 10:15-10:45 -> merged 10:00-10:45 (45 min = 2700 sec)
    intervals = [
        (base, base + timedelta(minutes=30)),
        (base + timedelta(minutes=15), base + timedelta(minutes=45))
    ]
    merged = merge_time_intervals(intervals)
    assert len(merged) == 1
    assert merged[0] == (base, base + timedelta(minutes=45))
    assert calculate_merged_seconds(intervals) == 2700.0

def test_machine_oee_calculation(db):
    start = datetime(2026, 1, 1, 6, 0, 0)
    end = datetime(2026, 1, 2, 6, 0, 0)
    res = OEEEngine.calculate_machine_oee(db, machine_id=1, start_time=start, end_time=end)

    assert "availability" in res
    assert "performance" in res
    assert "quality" in res
    assert "oee" in res
    assert 0.0 <= res["availability"] <= 100.0
    assert 0.0 <= res["quality"] <= 100.0
    assert 0.0 <= res["oee"] <= 100.0
    # OEE must equal Availability * Performance * Quality (with internal decimal bounding)
    expected_oee = round((res["availability"] / 100.0) * (min(100.0, res["performance"]) / 100.0) * (res["quality"] / 100.0) * 100.0, 2)
    assert abs(res["oee"] - expected_oee) <= 0.05

def test_division_by_zero_handling(db):
    # Empty 0-second time window
    now = datetime(2026, 1, 1, 12, 0, 0)
    res = OEEEngine.calculate_machine_oee(db, machine_id=1, start_time=now, end_time=now)
    assert res["availability"] == 0.0
    assert res["performance"] == 0.0
    assert res["oee"] == 0.0

def test_line_oee_aggregation(db):
    start = datetime(2026, 1, 1, 6, 0, 0)
    end = datetime(2026, 1, 2, 6, 0, 0)
    res = OEEEngine.calculate_line_oee(db, line_id=1, start_time=start, end_time=end)
    assert res["line_code"] == "LINE-01"
    assert res["machines_count"] == 6
    assert 0.0 <= res["oee"] <= 100.0
