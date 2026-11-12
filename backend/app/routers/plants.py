from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import Plant
from backend.app.models.user import User
from backend.app.schemas.master_data import PlantCreate, PlantUpdate, PlantResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/plants", tags=["Plants"])

@router.get("", response_model=List[PlantResponse])
def list_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Plant).offset(skip).limit(limit).all()

@router.post("", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(plant_in: PlantCreate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    if db.query(Plant).filter(Plant.plant_code == plant_in.plant_code).first():
        raise HTTPException(status_code=400, detail="Plant code already exists")
    plant = Plant(**plant_in.model_dump())
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant

@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(plant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@router.put("/{plant_id}", response_model=PlantResponse)
def update_plant(plant_id: int, plant_in: PlantUpdate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    for field, val in plant_in.model_dump(exclude_unset=True).items():
        setattr(plant, field, val)
    db.commit()
    db.refresh(plant)
    return plant

@router.delete("/{plant_id}")
def delete_plant(plant_id: int, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return {"message": "Plant deleted successfully"}
