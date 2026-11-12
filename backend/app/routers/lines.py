from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import ProductionLine, Plant
from backend.app.models.user import User
from backend.app.schemas.master_data import LineCreate, LineUpdate, LineResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/lines", tags=["Production Lines"])

@router.get("", response_model=List[LineResponse])
def list_lines(
    plant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ProductionLine)
    if plant_id:
        query = query.filter(ProductionLine.plant_id == plant_id)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=LineResponse, status_code=status.HTTP_201_CREATED)
def create_line(line_in: LineCreate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    if not db.query(Plant).filter(Plant.id == line_in.plant_id).first():
        raise HTTPException(status_code=400, detail="Invalid plant_id: plant does not exist")
    if db.query(ProductionLine).filter(ProductionLine.line_code == line_in.line_code).first():
        raise HTTPException(status_code=400, detail="Line code already exists")
    line = ProductionLine(**line_in.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line

@router.get("/{line_id}", response_model=LineResponse)
def get_line(line_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Production line not found")
    return line

@router.put("/{line_id}", response_model=LineResponse)
def update_line(line_id: int, line_in: LineUpdate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Production line not found")
    if line_in.plant_id and not db.query(Plant).filter(Plant.id == line_in.plant_id).first():
        raise HTTPException(status_code=400, detail="Invalid plant_id")
    for field, val in line_in.model_dump(exclude_unset=True).items():
        setattr(line, field, val)
    db.commit()
    db.refresh(line)
    return line

@router.delete("/{line_id}")
def delete_line(line_id: int, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Production line not found")
    db.delete(line)
    db.commit()
    return {"message": "Production line deleted successfully"}
