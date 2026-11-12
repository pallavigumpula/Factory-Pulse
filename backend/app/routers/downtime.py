from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import DowntimeReason
from backend.app.models.user import User
from backend.app.schemas.master_data import DowntimeReasonCreate, DowntimeReasonUpdate, DowntimeReasonResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/downtime-reasons", tags=["Downtime Reasons"])

@router.get("", response_model=List[DowntimeReasonResponse])
def list_downtime_reasons(
    category: Optional[str] = None,
    is_planned: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DowntimeReason)
    if category:
        query = query.filter(DowntimeReason.category == category.upper())
    if is_planned is not None:
        query = query.filter(DowntimeReason.is_planned == is_planned)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=DowntimeReasonResponse, status_code=status.HTTP_201_CREATED)
def create_downtime_reason(
    reason_in: DowntimeReasonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "MAINTENANCE"))
):
    if db.query(DowntimeReason).filter(DowntimeReason.reason_code == reason_in.reason_code).first():
        raise HTTPException(status_code=400, detail="Reason code already exists")
    reason = DowntimeReason(**reason_in.model_dump())
    db.add(reason)
    db.commit()
    db.refresh(reason)
    return reason

@router.get("/{reason_id}", response_model=DowntimeReasonResponse)
def get_downtime_reason(reason_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reason = db.query(DowntimeReason).filter(DowntimeReason.id == reason_id).first()
    if not reason:
        raise HTTPException(status_code=404, detail="Downtime reason not found")
    return reason

@router.put("/{reason_id}", response_model=DowntimeReasonResponse)
def update_downtime_reason(
    reason_id: int,
    reason_in: DowntimeReasonUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "MAINTENANCE"))
):
    reason = db.query(DowntimeReason).filter(DowntimeReason.id == reason_id).first()
    if not reason:
        raise HTTPException(status_code=404, detail="Downtime reason not found")
    for field, val in reason_in.model_dump(exclude_unset=True).items():
        setattr(reason, field, val)
    db.commit()
    db.refresh(reason)
    return reason

@router.delete("/{reason_id}")
def delete_downtime_reason(
    reason_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "MAINTENANCE"))
):
    reason = db.query(DowntimeReason).filter(DowntimeReason.id == reason_id).first()
    if not reason:
        raise HTTPException(status_code=404, detail="Downtime reason not found")
    db.delete(reason)
    db.commit()
    return {"message": "Downtime reason deleted successfully"}
