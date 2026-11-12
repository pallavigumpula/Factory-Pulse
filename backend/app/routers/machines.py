from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import Machine, ProductionLine
from backend.app.models.user import User
from backend.app.schemas.master_data import MachineCreate, MachineUpdate, MachineResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/machines", tags=["Machines"])

@router.get("", response_model=List[MachineResponse])
def list_machines(
    line_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Machine)
    if line_id:
        query = query.filter(Machine.line_id == line_id)
    if status_filter:
        query = query.filter(Machine.current_status == status_filter.upper())
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(machine_in: MachineCreate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    if not db.query(ProductionLine).filter(ProductionLine.id == machine_in.line_id).first():
        raise HTTPException(status_code=400, detail="Invalid line_id: line does not exist")
    if db.query(Machine).filter(Machine.machine_code == machine_in.machine_code).first():
        raise HTTPException(status_code=400, detail="Machine code already exists")
    machine = Machine(**machine_in.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine

@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: int, machine_in: MachineUpdate, db: Session = Depends(get_db), user: User = Depends(require_role("ADMIN", "OPERATOR", "MAINTENANCE"))):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    if machine_in.line_id and not db.query(ProductionLine).filter(ProductionLine.id == machine_in.line_id).first():
        raise HTTPException(status_code=400, detail="Invalid line_id")
    for field, val in machine_in.model_dump(exclude_unset=True).items():
        setattr(machine, field, val)
    db.commit()
    db.refresh(machine)
    return machine

@router.delete("/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
    return {"message": "Machine deleted successfully"}
