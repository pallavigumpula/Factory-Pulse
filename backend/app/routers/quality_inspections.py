from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import Machine
from backend.app.models.production import ProductionOrder, QualityInspection
from backend.app.models.user import User
from backend.app.schemas.production import QualityInspectionCreate, QualityInspectionResponse
from backend.app.dependencies import get_current_user, require_role
from backend.app.utils.identifiers import generate_qc_code

router = APIRouter(prefix="/quality-inspections", tags=["Quality Inspections"])

VALID_QC_STATUS = {"PASSED", "FAILED", "CONDITIONAL"}

@router.get("", response_model=List[QualityInspectionResponse])
def list_quality_inspections(
    production_order_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(QualityInspection)
    if production_order_id:
        query = query.filter(QualityInspection.production_order_id == production_order_id)
    if machine_id:
        query = query.filter(QualityInspection.machine_id == machine_id)
    if status_filter:
        query = query.filter(QualityInspection.status == status_filter.upper())
    return query.order_by(QualityInspection.timestamp.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=QualityInspectionResponse, status_code=status.HTTP_201_CREATED)
def create_quality_inspection(
    qc_in: QualityInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "QUALITY"))
):
    po = db.query(ProductionOrder).filter(ProductionOrder.id == qc_in.production_order_id).first()
    if not po:
        raise HTTPException(status_code=400, detail="Invalid production_order_id")
    if not db.query(Machine).filter(Machine.id == qc_in.machine_id).first():
        raise HTTPException(status_code=400, detail="Invalid machine_id")

    status_upper = qc_in.status.upper()
    if status_upper not in VALID_QC_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_QC_STATUS}")

    if qc_in.passed_count + qc_in.failed_count > qc_in.sample_size:
        raise HTTPException(status_code=400, detail="Passed count + Failed count cannot exceed sample size")

    qc_code = qc_in.inspection_code
    if not qc_code:
        count = db.query(func.count(QualityInspection.id)).scalar() or 0
        qc_code = generate_qc_code(count + 1)

    qc = QualityInspection(
        inspection_code=qc_code,
        production_order_id=qc_in.production_order_id,
        machine_id=qc_in.machine_id,
        shift_id=qc_in.shift_id,
        sample_size=qc_in.sample_size,
        passed_count=qc_in.passed_count,
        failed_count=qc_in.failed_count,
        defect_type=qc_in.defect_type,
        inspector_id=user.id,
        timestamp=qc_in.timestamp or datetime.utcnow(),
        status=status_upper,
        notes=qc_in.notes
    )
    db.add(qc)
    db.commit()
    db.refresh(qc)
    return qc
