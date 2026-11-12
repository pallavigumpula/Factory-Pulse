from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.master_data import ProductionLine, Product
from backend.app.models.production import ProductionOrder
from backend.app.models.user import User
from backend.app.schemas.production import ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse
from backend.app.dependencies import get_current_user, require_role
from backend.app.utils.identifiers import generate_po_code

router = APIRouter(prefix="/production-orders", tags=["Production Orders"])

@router.get("", response_model=List[ProductionOrderResponse])
def list_production_orders(
    line_id: Optional[int] = None,
    product_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ProductionOrder)
    if line_id:
        query = query.filter(ProductionOrder.line_id == line_id)
    if product_id:
        query = query.filter(ProductionOrder.product_id == product_id)
    if status_filter:
        query = query.filter(ProductionOrder.status == status_filter.upper())
    return query.order_by(ProductionOrder.id.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
def create_production_order(
    order_in: ProductionOrderCreate,
    db: Session = Depends(get_db),
    planner: User = Depends(require_role("ADMIN", "PLANNER"))
):
    if not db.query(ProductionLine).filter(ProductionLine.id == order_in.line_id).first():
        raise HTTPException(status_code=400, detail="Invalid line_id")
    if not db.query(Product).filter(Product.id == order_in.product_id).first():
        raise HTTPException(status_code=400, detail="Invalid product_id")
    
    order_code = order_in.order_code
    if not order_code:
        count = db.query(func.count(ProductionOrder.id)).scalar() or 0
        order_code = generate_po_code(count + 1)
    
    if db.query(ProductionOrder).filter(ProductionOrder.order_code == order_code).first():
        raise HTTPException(status_code=400, detail="Production order code already exists")
    
    po = ProductionOrder(
        order_code=order_code,
        line_id=order_in.line_id,
        product_id=order_in.product_id,
        target_quantity=order_in.target_quantity,
        produced_quantity=order_in.produced_quantity or 0,
        status=(order_in.status or "PLANNED").upper(),
        start_time=order_in.start_time or datetime.utcnow(),
        end_time=order_in.end_time
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po

@router.get("/{order_id}", response_model=ProductionOrderResponse)
def get_production_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    po = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Production order not found")
    return po

@router.put("/{order_id}", response_model=ProductionOrderResponse)
def update_production_order(
    order_id: int,
    order_in: ProductionOrderUpdate,
    db: Session = Depends(get_db),
    planner: User = Depends(require_role("ADMIN", "PLANNER"))
):
    po = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Production order not found")
    for field, val in order_in.model_dump(exclude_unset=True).items():
        if field == "status" and val:
            val = val.upper()
        setattr(po, field, val)
    db.commit()
    db.refresh(po)
    return po
