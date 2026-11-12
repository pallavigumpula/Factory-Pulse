from typing import Optional, List, Any
from datetime import date
from pydantic import BaseModel

class ReportFilterParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    plant_id: Optional[int] = None
    line_id: Optional[int] = None
    machine_id: Optional[int] = None
    shift_id: Optional[int] = None
    product_id: Optional[int] = None
    production_order_id: Optional[int] = None

class ProductionSummaryItem(BaseModel):
    date: date
    order_code: str
    product_name: str
    line_name: str
    target_quantity: int
    good_quantity: int
    scrap_quantity: int
    rework_quantity: int
    completion_rate: float

class DowntimeSummaryItem(BaseModel):
    reason_code: str
    reason_name: str
    category: str
    is_planned: bool
    incident_count: int
    total_minutes: float
    percentage_of_downtime: float

class AIAssistantQuery(BaseModel):
    question: str

class AIAssistantResponse(BaseModel):
    question: str
    answer: str
    source_metrics: dict
    insights: List[str]
    suggested_actions: List[str]
