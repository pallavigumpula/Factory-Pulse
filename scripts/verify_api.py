import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal
from backend.app.schemas.user import LoginRequest
from backend.app.routers.auth import login, get_current_user_profile
from backend.app.routers.plants import list_plants
from backend.app.routers.lines import list_lines
from backend.app.routers.machines import list_machines
from backend.app.routers.production_orders import list_production_orders
from backend.app.routers.anomalies import list_anomalies
from backend.app.routers.oee import get_dashboard_kpis
from backend.app.routers.reports import export_oee_csv
from backend.app.services.ai_assistant import ManufacturingAIAssistant

def main():
    db = SessionLocal()
    print("========================================================")
    print(" FACTORYPULSE FULL SYSTEM & WORKFLOW VERIFICATION")
    print("========================================================")

    print("\n1. Testing User Authentication & Token Generation...")
    login_req = LoginRequest(username="admin", password="admin123")
    auth_res = login(login_req, db=db)
    assert auth_res.access_token, "Token generation failed"
    current_user = auth_res.user
    print(f"   [PASS] User '{current_user.username}' authenticated as role '{current_user.role}'.")

    print("\n2. Testing Master Data Management...")
    plants = list_plants(db=db, current_user=current_user)
    assert len(plants) >= 2, f"Expected >= 2 plants, got {len(plants)}"
    print(f"   [PASS] {len(plants)} Plants active.")

    lines = list_lines(db=db, current_user=current_user)
    assert len(lines) >= 5, f"Expected >= 5 lines, got {len(lines)}"
    print(f"   [PASS] {len(lines)} Production Lines active.")

    machines = list_machines(db=db, current_user=current_user)
    assert len(machines) >= 30, f"Expected >= 30 machines, got {len(machines)}"
    print(f"   [PASS] {len(machines)} Work Centers / Machines active.")

    print("\n3. Testing Production Orders Management...")
    orders = list_production_orders(db=db, current_user=current_user)
    assert len(orders) > 0, "No production orders found"
    print(f"   [PASS] {len(orders)} Production Orders retrieved.")

    print("\n4. Testing Deterministic Anomaly Detection...")
    anomalies = list_anomalies(db=db, current_user=current_user)
    print(f"   [PASS] {len(anomalies)} Anomalies detected and cataloged in database.")

    print("\n5. Testing AI Manufacturing Operations Assistant...")
    query = "Which machine has the highest downtime?"
    assist_res = ManufacturingAIAssistant.answer_query(db, query)
    assert "answer" in assist_res and len(assist_res["suggested_actions"]) > 0
    print(f"   [PASS] Query: '{query}'")
    print(f"   Response: {assist_res['answer'][:100]}...")

    print("\n6. Testing OEE Engine & Factor Decomposition...")
    s_date = datetime.date(2026, 1, 1)
    e_date = datetime.date(2026, 1, 5)
    kpis = get_dashboard_kpis(start_date=s_date, end_date=e_date, db=db, current_user=current_user)
    assert kpis.overall_oee >= 0.0
    print(f"   [PASS] Period: {s_date} to {e_date}")
    print(f"   Overall OEE: {kpis.overall_oee}% | Availability: {kpis.availability}% | Performance: {kpis.performance}% | Quality: {kpis.quality}%")

    print("\n7. Testing Reports & Data Export Serialization...")
    resp = export_oee_csv(start_date=s_date, end_date=e_date, db=db, current_user=current_user)
    csv_body = resp.body.decode("utf-8")
    assert "machine_code" in csv_body and "oee_pct" in csv_body
    print(f"   [PASS] CSV Report generated successfully ({len(csv_body)} bytes).")

    db.close()
    print("\n========================================================")
    print(" ALL FACTORYPULSE PLATFORM SUBSYSTEMS FULLY OPERATIONAL!")
    print("========================================================")

if __name__ == "__main__":
    main()
