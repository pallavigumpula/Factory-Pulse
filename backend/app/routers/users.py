from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.app.dependencies import require_role
from backend.app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    return db.query(User).offset(skip).limit(limit).all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role.upper(),
        is_active=user_in.is_active if user_in.is_active is not None else True,
        password_hash=hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.email is not None and user_in.email != user.email:
        if db.query(User).filter(User.email == user_in.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_in.email
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.role is not None:
        user.role = user_in.role.upper()
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None and user_in.password.strip():
        user.password_hash = hash_password(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
