from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# Plant Schemas
class PlantBase(BaseModel):
    plant_code: str
    name: str
    location: Optional[str] = None
    timezone: Optional[str] = "UTC"
    is_active: Optional[bool] = True

class PlantCreate(PlantBase):
    pass

class PlantUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

class PlantResponse(PlantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Line Schemas
class LineBase(BaseModel):
    plant_id: int
    line_code: str
    name: str
    target_oee: Optional[Decimal] = Decimal("85.00")
    is_active: Optional[bool] = True

class LineCreate(LineBase):
    pass

class LineUpdate(BaseModel):
    plant_id: Optional[int] = None
    name: Optional[str] = None
    target_oee: Optional[Decimal] = None
    is_active: Optional[bool] = None

class LineResponse(LineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Machine Schemas
class MachineBase(BaseModel):
    line_id: int
    machine_code: str
    name: str
    model: Optional[str] = None
    current_status: Optional[str] = "IDLE"
    is_active: Optional[bool] = True

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    line_id: Optional[int] = None
    name: Optional[str] = None
    model: Optional[str] = None
    current_status: Optional[str] = None
    is_active: Optional[bool] = None

class MachineResponse(MachineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Shift Schemas
class ShiftBase(BaseModel):
    plant_id: int
    shift_code: str
    name: str
    start_time: time
    end_time: time
    planned_break_minutes: Optional[int] = 60
    is_active: Optional[bool] = True

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    plant_id: Optional[int] = None
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    planned_break_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class ShiftResponse(ShiftBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    product_code: str
    name: str
    category: Optional[str] = None
    ideal_cycle_time_seconds: Decimal
    unit_of_measure: Optional[str] = "units"
    is_active: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    ideal_cycle_time_seconds: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Downtime Reason Schemas
class DowntimeReasonBase(BaseModel):
    reason_code: str
    category: str
    name: str
    description: Optional[str] = None
    is_planned: Optional[bool] = False
    is_active: Optional[bool] = True

class DowntimeReasonCreate(DowntimeReasonBase):
    pass

class DowntimeReasonUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_planned: Optional[bool] = None
    is_active: Optional[bool] = None

class DowntimeReasonResponse(DowntimeReasonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
