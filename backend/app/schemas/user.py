from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    is_active: Optional[bool] = True

    @field_validator("email")
    def validate_email_simple(cls, v: str) -> str:
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("email")
    def validate_email_opt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if "@" not in v or "." not in v.split("@")[-1]:
                raise ValueError("Invalid email format")
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str
