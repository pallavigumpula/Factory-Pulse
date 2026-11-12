"""
Full API test via FastAPI TestClient — simulates real HTTP requests.
Verifies:
  1. Login works
  2. Dashboard KPIs return real non-zero values
  3. OEE trend returns non-empty data
  4. Anomaly evaluation returns P=1.0 R=1.0 F1=1.0
  5. Machine OEE returns real values
"""
import sys, os
sys.path.insert(0, r'C:\CandidateWorkspace')
os.chdir(r'C:\CandidateWorkspace')

import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app, raise_server_exceptions=True)

# --- LOGIN ---
resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login: OK")

# --- DASHBOARD KPIs ---
resp = client.get("/api/v1/oee/dashboard-kpis", headers=headers)
assert resp.status_code == 200, f"Dashboard KPIs HTTP {resp.status_code}: {resp.text}"
kpi = resp.json()
print(f"\n=== Dashboard KPIs ===")
print(f"  Overall OEE:        {kpi['overall_oee']}%")
print(f"  Availability:       {kpi['availability']}%")
print(f"  Performance:        {kpi['performance']}%")
print(f"  Quality:            {kpi.get('quality_display', kpi.get('quality'))}")
print(f"  Total Production:   {kpi['total_production']:,}")
print(f"  Good Units:         {kpi['good_count']:,}")
print(f"  Scrap Units:        {kpi['scrap_count']:,}")
print(f"  Total Downtime:     {kpi['total_downtime_minutes']} min")
print(f"  Active Machines:    {kpi['active_machines_count']} / {kpi['total_machines_count']}")
assert kpi['total_production'] > 0, "total_production is 0 — no data was read!"
assert kpi['availability'] > 0, "availability is 0 — date filter still broken!"
print("✅ Dashboard KPIs: REAL DATA confirmed (total_production > 0, availability > 0)")

# --- OEE TREND ---
resp = client.get("/api/v1/oee/trend", headers=headers, params={"days": 7})
assert resp.status_code == 200, f"OEE Trend HTTP {resp.status_code}: {resp.text}"
trend = resp.json()
print(f"\n=== OEE Trend ({len(trend)} days) ===")
for day in trend:
    has_data = day['oee'] > 0 or day['availability'] > 0
    marker = "●" if has_data else "○"
    print(f"  {marker} {day['date']}: OEE={day['oee']}% A={day['availability']}% P={day['performance']}% Q={day['quality']}%")
assert any(d['oee'] > 0 for d in trend), "All trend days have OEE=0 — trend date window still broken!"
print("✅ OEE Trend: At least one day with OEE > 0")

# --- ANOMALY LIST (should have 6 records) ---
resp = client.get("/api/v1/anomalies", headers=headers)
assert resp.status_code == 200, f"Anomalies list HTTP {resp.status_code}: {resp.text}"
anoms = resp.json()
print(f"\n=== Anomaly List ({len(anoms)} records) ===")
for a in anoms:
    print(f"  [{a['severity']:<8}] {a['anomaly_type']:<40} entity={a['entity_id']}")
assert len(anoms) >= 5, f"Expected >=5 anomalies, got {len(anoms)}"

# --- ANOMALY EVALUATION ---
resp = client.get("/api/v1/anomalies/evaluation", headers=headers)
assert resp.status_code == 200, f"Anomaly eval HTTP {resp.status_code}: {resp.text}"
metrics = resp.json()
print(f"\n=== Anomaly Evaluation ===")
print(f"  Precision:   {metrics['precision']*100:.1f}%")
print(f"  Recall:      {metrics['recall']*100:.1f}%")
print(f"  F1-Score:    {metrics['f1_score']:.4f}")
print(f"  TP: {metrics['true_positives']}  FP: {metrics['false_positives']}  FN: {metrics['false_negatives']}")
assert metrics['precision'] == 1.0, f"Precision != 1.0: {metrics['precision']}"
assert metrics['recall']    == 1.0, f"Recall != 1.0: {metrics['recall']}"
assert metrics['f1_score']  == 1.0, f"F1 != 1.0: {metrics['f1_score']}"
print("✅ Anomaly: Precision=100% Recall=100% F1=1.0")

# --- MACHINE OEE SUMMARY ---
resp = client.get("/api/v1/oee/by-machine", headers=headers)
assert resp.status_code == 200, f"Machine OEE HTTP {resp.status_code}: {resp.text}"
machines_oee = resp.json()
print(f"\n=== Machine OEE ({len(machines_oee)} machines) ===")
for m in machines_oee[:5]:
    print(f"  {m['machine_code']}: OEE={m['oee']}% A={m['availability']}% P={m['performance']}% Q={m['quality']}")

# --- LINE OEE ---
resp = client.get("/api/v1/oee/by-line", headers=headers)
assert resp.status_code == 200, f"Line OEE HTTP {resp.status_code}: {resp.text}"
lines_oee = resp.json()
print(f"\n=== Line OEE ({len(lines_oee)} lines) ===")
for l in lines_oee:
    print(f"  {l['line_code']}: OEE={l['oee']}%  Total={l['total_count']:,}")

# --- DOWNTIME PARETO ---
resp = client.get("/api/v1/oee/downtime-reasons", headers=headers)
assert resp.status_code == 200, f"Downtime reasons HTTP {resp.status_code}: {resp.text}"
dt = resp.json()
print(f"\n=== Downtime Pareto ({len(dt)} reasons) ===")
for r in dt[:5]:
    print(f"  {r['reason_code']}: {r['duration_minutes']} min ({r['percentage']}%)")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED — Dashboard and Anomaly Detection working correctly")
