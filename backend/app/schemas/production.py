from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Production Order
class ProductionOrderBase(BaseModel):
    order_code: Optional[str] = None
    line_id: int
    product_id: int
    target_quantity: int
    produced_quantity: Optional[int] = 0
    status: Optional[str] = "PLANNED"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ProductionOrderCreate(ProductionOrderBase):
    pass

class ProductionOrderUpdate(BaseModel):
    target_quantity: Optional[int] = None
    produced_quantity: Optional[int] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ProductionOrderResponse(ProductionOrderBase):
    id: int
    order_code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Machine State Event
class MachineStateEventBase(BaseModel):
    event_code: Optional[str] = None
    machine_id: int
    production_order_id: Optional[int] = None
    shift_id: Optional[int] = None
    state: str # RUNNING, STOPPED, IDLE, CHANGEOVER, MAINTENANCE, BREAK
    start_time: datetime
    end_time: datetime
    duration_seconds: Optional[int] = None
    downtime_reason_id: Optional[int] = None
    notes: Optional[str] = None

class MachineStateEventCreate(MachineStateEventBase):
    pass

class MachineStateEventResponse(MachineStateEventBase):
    id: int
    event_code: str
    duration_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Production Count
class ProductionCountBase(BaseModel):
    count_code: Optional[str] = None
    production_order_id: int
    machine_id: int
    shift_id: Optional[int] = None
    product_id: int
    count_type: str # GOOD, SCRAP, REWORK, CORRECTION
    quantity: int
    timestamp: datetime
    operator_id: Optional[int] = None
    reference_count_id: Optional[int] = None
    reason: Optional[str] = None

class ProductionCountCreate(ProductionCountBase):
    pass

class ProductionCountCorrectionCreate(BaseModel):
    reference_count_id: int
    corrected_quantity_delta: int
    reason: str
    operator_id: Optional[int] = None
    timestamp: Optional[datetime] = None

class ProductionCountResponse(ProductionCountBase):
    id: int
    count_code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Quality Inspection
class QualityInspectionBase(BaseModel):
    inspection_code: Optional[str] = None
    production_order_id: int
    machine_id: int
    shift_id: Optional[int] = None
    sample_size: int
    passed_count: int
    failed_count: int
    defect_type: Optional[str] = None
    inspector_id: Optional[int] = None
    timestamp: datetime
    status: str # PASSED, FAILED, CONDITIONAL
    notes: Optional[str] = None

class QualityInspectionCreate(QualityInspectionBase):
    pass

class QualityInspectionResponse(QualityInspectionBase):
    id: int
    inspection_code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
