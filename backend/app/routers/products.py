from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.master_data import Product
from backend.app.models.user import User
from backend.app.schemas.master_data import ProductCreate, ProductUpdate, ProductResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    if db.query(Product).filter(Product.product_code == product_in.product_code).first():
        raise HTTPException(status_code=400, detail="Product code already exists")
    if product_in.ideal_cycle_time_seconds <= 0:
        raise HTTPException(status_code=400, detail="Ideal cycle time must be strictly positive")
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_in.ideal_cycle_time_seconds is not None and product_in.ideal_cycle_time_seconds <= 0:
        raise HTTPException(status_code=400, detail="Ideal cycle time must be positive")
    for field, val in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, val)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), admin: User = Depends(require_role("ADMIN"))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
