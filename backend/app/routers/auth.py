from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.user import User
from backend.app.schemas.user import LoginRequest, TokenResponse, UserResponse
from backend.app.utils.security import verify_password, create_access_token
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    token = create_access_token(
        payload={"sub": user.username, "role": user.role, "id": user.id},
        secret_key=settings.SECRET_KEY,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
