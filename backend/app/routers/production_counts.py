from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import Machine, Product
from backend.app.models.production import ProductionOrder, ProductionCount
from backend.app.models.user import User
from backend.app.schemas.production import (
    ProductionCountCreate,
    ProductionCountCorrectionCreate,
    ProductionCountResponse
)
from backend.app.dependencies import get_current_user, require_role
from backend.app.utils.identifiers import generate_count_code

router = APIRouter(prefix="/production-counts", tags=["Production Counts"])

VALID_COUNT_TYPES = {"GOOD", "SCRAP", "REWORK", "CORRECTION"}

@router.get("", response_model=List[ProductionCountResponse])
def list_production_counts(
    production_order_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    count_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ProductionCount)
    if production_order_id:
        query = query.filter(ProductionCount.production_order_id == production_order_id)
    if machine_id:
        query = query.filter(ProductionCount.machine_id == machine_id)
    if count_type:
        query = query.filter(ProductionCount.count_type == count_type.upper())
    if start_date:
        query = query.filter(ProductionCount.timestamp >= start_date)
    if end_date:
        query = query.filter(ProductionCount.timestamp <= end_date)
    return query.order_by(ProductionCount.timestamp.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=ProductionCountResponse, status_code=status.HTTP_201_CREATED)
def record_production_count(
    count_in: ProductionCountCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    po = db.query(ProductionOrder).filter(ProductionOrder.id == count_in.production_order_id).first()
    if not po:
        raise HTTPException(status_code=400, detail="Invalid production_order_id")
    if not db.query(Machine).filter(Machine.id == count_in.machine_id).first():
        raise HTTPException(status_code=400, detail="Invalid machine_id")
    if not db.query(Product).filter(Product.id == count_in.product_id).first():
        raise HTTPException(status_code=400, detail="Invalid product_id")

    type_upper = count_in.count_type.upper()
    if type_upper not in VALID_COUNT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid count type. Must be one of {VALID_COUNT_TYPES}")

    if type_upper != "CORRECTION" and count_in.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be non-negative for standard counts")

    count_code = count_in.count_code
    if not count_code:
        c_num = db.query(func.count(ProductionCount.id)).filter(ProductionCount.production_order_id == po.id).scalar() or 0
        count_code = generate_count_code(po.order_code, c_num + 1)
        while db.query(ProductionCount).filter(ProductionCount.count_code == count_code).first() is not None:
            c_num += 1
            count_code = generate_count_code(po.order_code, c_num + 1)

    count_rec = ProductionCount(
        count_code=count_code,
        production_order_id=po.id,
        machine_id=count_in.machine_id,
        shift_id=count_in.shift_id,
        product_id=count_in.product_id,
        count_type=type_upper,
        quantity=count_in.quantity,
        timestamp=count_in.timestamp or datetime.utcnow(),
        operator_id=user.id,
        reference_count_id=count_in.reference_count_id,
        reason=count_in.reason
    )
    db.add(count_rec)

    # If count is GOOD, increment PO produced quantity
    if type_upper == "GOOD":
        po.produced_quantity = (po.produced_quantity or 0) + count_in.quantity
        if po.status == "PLANNED":
            po.status = "IN_PROGRESS"
        if po.produced_quantity >= po.target_quantity:
            po.status = "COMPLETED"

    db.commit()
    db.refresh(count_rec)
    return count_rec

@router.post("/correct", response_model=ProductionCountResponse, status_code=status.HTTP_201_CREATED)
def correct_production_count(
    correction_in: ProductionCountCorrectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    """
    Explicit traceable correction event.
    Never overwrites historical counts, preserves full audit trail.
    """
    ref_count = db.query(ProductionCount).filter(ProductionCount.id == correction_in.reference_count_id).first()
    if not ref_count:
        raise HTTPException(status_code=404, detail="Reference production count not found")

    po = db.query(ProductionOrder).filter(ProductionOrder.id == ref_count.production_order_id).first()
    if not po:
        raise HTTPException(status_code=400, detail="Associated production order not found")

    c_num = db.query(func.count(ProductionCount.id)).filter(ProductionCount.production_order_id == po.id).scalar() or 0
    correction_code = generate_count_code(po.order_code, c_num + 1) + "-CORR"
    while db.query(ProductionCount).filter(ProductionCount.count_code == correction_code).first() is not None:
        c_num += 1
        correction_code = generate_count_code(po.order_code, c_num + 1) + "-CORR"

    correction_rec = ProductionCount(
        count_code=correction_code,
        production_order_id=po.id,
        machine_id=ref_count.machine_id,
        shift_id=ref_count.shift_id,
        product_id=ref_count.product_id,
        count_type="CORRECTION",
        quantity=correction_in.corrected_quantity_delta,
        timestamp=correction_in.timestamp or datetime.utcnow(),
        operator_id=user.id,
        reference_count_id=ref_count.id,
        reason=correction_in.reason
    )
    db.add(correction_rec)

    if ref_count.count_type == "GOOD":
        po.produced_quantity = max(0, (po.produced_quantity or 0) + correction_in.corrected_quantity_delta)

    db.commit()
    db.refresh(correction_rec)
    return correction_rec
