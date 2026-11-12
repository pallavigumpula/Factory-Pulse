from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class OEEAggregateResponse(BaseModel):
    id: Optional[int] = None
    aggregation_level: str # MACHINE, LINE, SHIFT, PRODUCT, PLANT
    entity_id: int
    entity_code: str
    date: date
    shift_id: Optional[int] = None
    planned_production_time_minutes: Decimal
    operating_time_minutes: Decimal
    planned_downtime_minutes: Decimal
    unplanned_downtime_minutes: Decimal
    ideal_cycle_time_seconds: Decimal
    total_count: int
    good_count: int
    scrap_count: int
    rework_count: int
    availability: Decimal # Percentage or ratio
    performance: Decimal
    quality: Decimal
    oee: Decimal
    performance_flagged: bool
    calculated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class OEEDashboardKPI(BaseModel):
    overall_oee: float
    availability: float
    performance: float
    quality: float
    total_production: int
    good_count: int
    scrap_count: int
    rework_count: int
    total_downtime_minutes: float
    planned_downtime_minutes: float
    unplanned_downtime_minutes: float
    target_oee: float = 85.0
    active_machines_count: int
    total_machines_count: int
    performance_flagged_count: int

class OEECalculationResult(BaseModel):
    planned_production_time_minutes: float
    operating_time_minutes: float
    planned_downtime_minutes: float
    unplanned_downtime_minutes: float
    ideal_cycle_time_seconds: float
    total_count: int
    good_count: int
    scrap_count: int
    rework_count: int
    availability: float
    performance: float
    quality: float
    oee: float
    performance_flagged: bool
    assumptions: List[str]
