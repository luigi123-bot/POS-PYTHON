from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role_id: int
    primary_branch_id: Optional[int] = None
    branch_ids: List[int] = []


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    primary_branch_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    role_id: int
    primary_branch_id: Optional[int] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    role: Optional["RoleResponse"] = None
    primary_branch: Optional["BranchResponse"] = None
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


# Login schema
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserDetailResponse


# Forward references
from app.schemas.role import RoleResponse
from app.schemas.branch import BranchResponse

UserDetailResponse.model_rebuild()
