from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import Shift, Plant
from backend.app.models.user import User
from backend.app.schemas.master_data import ShiftCreate, ShiftUpdate, ShiftResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/shifts", tags=["Shifts"])

@router.get("", response_model=List[ShiftResponse])
def list_shifts(
    plant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Shift)
    if plant_id:
        query = query.filter(Shift.plant_id == plant_id)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
def create_shift(shift_in: ShiftCreate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    if not db.query(Plant).filter(Plant.id == shift_in.plant_id).first():
        raise HTTPException(status_code=400, detail="Invalid plant_id: plant does not exist")
    shift = Shift(**shift_in.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

@router.get("/{shift_id}", response_model=ShiftResponse)
def get_shift(shift_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.put("/{shift_id}", response_model=ShiftResponse)
def update_shift(shift_id: int, shift_in: ShiftUpdate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, val in shift_in.model_dump(exclude_unset=True).items():
        setattr(shift, field, val)
    db.commit()
    db.refresh(shift)
    return shift

@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    db.delete(shift)
    db.commit()
    return {"message": "Shift deleted successfully"}
