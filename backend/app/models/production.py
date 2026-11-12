import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(50), unique=True, index=True, nullable=False)
    line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    target_quantity = Column(Integer, nullable=False)
    produced_quantity = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="PLANNED", nullable=False) # PLANNED, IN_PROGRESS, COMPLETED, ON_HOLD, CANCELLED
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    line = relationship("ProductionLine", back_populates="production_orders")
    product = relationship("Product")
    counts = relationship("ProductionCount", back_populates="production_order", cascade="all, delete-orphan")
    events = relationship("MachineStateEvent", back_populates="production_order")
    inspections = relationship("QualityInspection", back_populates="production_order", cascade="all, delete-orphan")


class MachineStateEvent(Base):
    __tablename__ = "machine_state_events"

    id = Column(Integer, primary_key=True, index=True)
    event_code = Column(String(60), unique=True, index=True, nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True, index=True)
    state = Column(String(20), nullable=False) # RUNNING, STOPPED, IDLE, CHANGEOVER, MAINTENANCE, BREAK
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    downtime_reason_id = Column(Integer, ForeignKey("downtime_reasons.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    machine = relationship("Machine", back_populates="events")
    production_order = relationship("ProductionOrder", back_populates="events")
    shift = relationship("Shift")
    downtime_reason = relationship("DowntimeReason")


class ProductionCount(Base):
    __tablename__ = "production_counts"

    id = Column(Integer, primary_key=True, index=True)
    count_code = Column(String(60), unique=True, index=True, nullable=False)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    count_type = Column(String(20), nullable=False) # GOOD, SCRAP, REWORK, CORRECTION
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reference_count_id = Column(Integer, ForeignKey("production_counts.id"), nullable=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    production_order = relationship("ProductionOrder", back_populates="counts")
    machine = relationship("Machine", back_populates="counts")
    shift = relationship("Shift")
    product = relationship("Product")
    operator = relationship("User")
    reference_count = relationship("ProductionCount", remote_side=[id])


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_code = Column(String(60), unique=True, index=True, nullable=False)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True, index=True)
    sample_size = Column(Integer, nullable=False)
    passed_count = Column(Integer, nullable=False)
    failed_count = Column(Integer, nullable=False)
    defect_type = Column(String(100), nullable=True)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False) # PASSED, FAILED, CONDITIONAL
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    production_order = relationship("ProductionOrder", back_populates="inspections")
    machine = relationship("Machine", back_populates="inspections")
    shift = relationship("Shift")
    inspector = relationship("User")


class OEEAggregate(Base):
    __tablename__ = "oee_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    aggregation_level = Column(String(20), nullable=False, index=True) # MACHINE, LINE, SHIFT, PRODUCT, PLANT
    entity_id = Column(Integer, nullable=False, index=True)
    entity_code = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    shift_id = Column(Integer, nullable=True, index=True)
    planned_production_time_minutes = Column(Numeric(10, 2), default=0.00, nullable=False)
    operating_time_minutes = Column(Numeric(10, 2), default=0.00, nullable=False)
    planned_downtime_minutes = Column(Numeric(10, 2), default=0.00, nullable=False)
    unplanned_downtime_minutes = Column(Numeric(10, 2), default=0.00, nullable=False)
    ideal_cycle_time_seconds = Column(Numeric(10, 4), default=0.0000, nullable=False)
    total_count = Column(Integer, default=0, nullable=False)
    good_count = Column(Integer, default=0, nullable=False)
    scrap_count = Column(Integer, default=0, nullable=False)
    rework_count = Column(Integer, default=0, nullable=False)
    availability = Column(Numeric(6, 4), default=0.0000, nullable=False) # ratio 0.0 - 1.0
    performance = Column(Numeric(6, 4), default=0.0000, nullable=False)
    quality = Column(Numeric(6, 4), default=0.0000, nullable=False)
    oee = Column(Numeric(6, 4), default=0.0000, nullable=False)
    performance_flagged = Column(Boolean, default=False, nullable=False)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
