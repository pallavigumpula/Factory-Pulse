import pytest
import datetime
from backend.app.services.report_service import ReportService
from backend.app.services.ai_assistant import ManufacturingAIAssistant
from backend.app.routers.reports import get_production_summary, get_downtime_summary

def test_oee_report_generation(db):
    s_date = datetime.date(2026, 1, 1)
    e_date = datetime.date(2026, 1, 3)
    rows = ReportService.generate_oee_report_data(db, s_date, e_date)
    assert len(rows) > 0
    assert "machine_code" in rows[0]
    assert "oee_pct" in rows[0]

def test_csv_and_json_export_serialization(db):
    s_date = datetime.date(2026, 1, 1)
    e_date = datetime.date(2026, 1, 3)
    rows = ReportService.generate_oee_report_data(db, s_date, e_date)

    csv_data = ReportService.export_csv(rows)
    assert "machine_code" in csv_data
    assert "\n" in csv_data

    json_data = ReportService.export_json(rows)
    assert json_data.startswith("[")
    assert "oee_pct" in json_data

def test_production_and_downtime_summaries(db, admin_user):
    prod_summary = get_production_summary(db=db, current_user=admin_user)
    assert len(prod_summary) > 0

    dt_summary = get_downtime_summary(db=db, current_user=admin_user)
    assert len(dt_summary) > 0

def test_ai_assistant_query_handling(db):
    res = ManufacturingAIAssistant.answer_query(db, "Which machine has the highest downtime?")
    assert "highest downtime" in res["answer"].lower()
    assert len(res["suggested_actions"]) > 0

    res_loss = ManufacturingAIAssistant.answer_query(db, "What are the major causes of production loss?")
    assert "downtime" in res_loss["answer"].lower()
