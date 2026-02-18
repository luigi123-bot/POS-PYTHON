from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class BranchBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "México"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_time: str = "09:00"
    closing_time: str = "21:00"


class BranchCreate(BranchBase):
    is_main: bool = False


class BranchUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_active: Optional[bool] = None
    is_main: Optional[bool] = None


class BranchResponse(BranchBase):
    id: int
    is_active: bool
    is_main: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BranchProductBase(BaseModel):
    branch_id: int
    product_id: int
    stock: int = 0
    min_stock: int = 5
    max_stock: int = 100
    custom_price: Optional[float] = None
    is_available: bool = True


class BranchProductCreate(BranchProductBase):
    pass


class BranchProductUpdate(BaseModel):
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    custom_price: Optional[float] = None
    is_available: Optional[bool] = None


class BranchProductResponse(BranchProductBase):
    id: int
    last_restock: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockUpdateRequest(BaseModel):
    quantity: int = Field(..., description="Cantidad a agregar (positivo) o quitar (negativo)")
    reason: Optional[str] = None
