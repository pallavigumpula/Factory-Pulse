from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import Machine
from backend.app.models.production import MachineStateEvent
from backend.app.models.user import User
from backend.app.schemas.production import MachineStateEventCreate, MachineStateEventResponse
from backend.app.dependencies import get_current_user, require_role
from backend.app.utils.identifiers import generate_event_code

router = APIRouter(prefix="/machine-events", tags=["Machine State Events"])

VALID_STATES = {"RUNNING", "STOPPED", "IDLE", "CHANGEOVER", "MAINTENANCE", "BREAK"}

@router.get("", response_model=List[MachineStateEventResponse])
def list_machine_events(
    machine_id: Optional[int] = None,
    state: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MachineStateEvent)
    if machine_id:
        query = query.filter(MachineStateEvent.machine_id == machine_id)
    if state:
        query = query.filter(MachineStateEvent.state == state.upper())
    if start_date:
        query = query.filter(MachineStateEvent.start_time >= start_date)
    if end_date:
        query = query.filter(MachineStateEvent.end_time <= end_date)
    return query.order_by(MachineStateEvent.start_time.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=MachineStateEventResponse, status_code=status.HTTP_201_CREATED)
def create_machine_event(
    event_in: MachineStateEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "OPERATOR", "MAINTENANCE"))
):
    machine = db.query(Machine).filter(Machine.id == event_in.machine_id).first()
    if not machine:
        raise HTTPException(status_code=400, detail="Invalid machine_id: machine not found")
    
    state_upper = event_in.state.upper()
    if state_upper not in VALID_STATES:
        raise HTTPException(status_code=400, detail=f"Invalid machine state. Must be one of {VALID_STATES}")
    
    if event_in.start_time > event_in.end_time:
        raise HTTPException(status_code=400, detail="start_time cannot be after end_time")
    
    duration = int((event_in.end_time - event_in.start_time).total_seconds())
    
    event_code = event_in.event_code
    if not event_code:
        count = db.query(func.count(MachineStateEvent.id)).filter(MachineStateEvent.machine_id == machine.id).scalar() or 0
        event_code = generate_event_code(machine.machine_code, count + 1)
        
    event = MachineStateEvent(
        event_code=event_code,
        machine_id=machine.id,
        production_order_id=event_in.production_order_id,
        shift_id=event_in.shift_id,
        state=state_upper,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        duration_seconds=duration,
        downtime_reason_id=event_in.downtime_reason_id,
        notes=event_in.notes
    )
    
    # Update machine's current status
    machine.current_status = state_upper
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/{event_id}", response_model=MachineStateEventResponse)
def get_machine_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(MachineStateEvent).filter(MachineStateEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Machine state event not found")
    return event
