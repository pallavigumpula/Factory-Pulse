import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Numeric, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    plant_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    lines = relationship("ProductionLine", back_populates="plant", cascade="all, delete-orphan")
    shifts = relationship("Shift", back_populates="plant", cascade="all, delete-orphan")
    shift_instances = relationship("ShiftInstance", back_populates="plant")


class ProductionLine(Base):
    __tablename__ = "production_lines"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, index=True)
    line_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    target_oee = Column(Numeric(5, 2), default=85.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plant = relationship("Plant", back_populates="lines")
    machines = relationship("Machine", back_populates="line", cascade="all, delete-orphan")
    production_orders = relationship("ProductionOrder", back_populates="line")


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False, index=True)
    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=True)
    current_status = Column(String(20), default="IDLE", nullable=False) # RUNNING, STOPPED, IDLE, CHANGEOVER, MAINTENANCE, BREAK
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    line = relationship("ProductionLine", back_populates="machines")
    events = relationship("MachineStateEvent", back_populates="machine", cascade="all, delete-orphan")
    counts = relationship("ProductionCount", back_populates="machine")
    inspections = relationship("QualityInspection", back_populates="machine")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, index=True)
    shift_code = Column(String(50), nullable=False) # e.g. SHIFT-A
    name = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    planned_break_minutes = Column(Integer, default=60, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("plant_id", "shift_code", name="uq_plant_shift"),)

    plant = relationship("Plant", back_populates="shifts")
    instances = relationship("ShiftInstance", back_populates="shift_template")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    ideal_cycle_time_seconds = Column(Numeric(10, 4), nullable=False)
    unit_of_measure = Column(String(20), default="units", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    production_orders = relationship("Product", secondary="production_orders", viewonly=True)


class DowntimeReason(Base):
    __tablename__ = "downtime_reasons"

    id = Column(Integer, primary_key=True, index=True)
    reason_code = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False) # UNPLANNED_DOWNTIME, PLANNED_DOWNTIME, BREAK, CHANGEOVER, MAINTENANCE
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_planned = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

class ShiftInstance(Base):
    __tablename__ = "shift_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_code = Column(String(60), unique=True, index=True, nullable=False)
    shift_template_id = Column(Integer, ForeignKey("shifts.id"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, index=True)
    shift_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    planned_break_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    shift_template = relationship("Shift", back_populates="instances")
    plant = relationship("Plant", back_populates="shift_instances")

