from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: str = "#3B82F6"
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=50)
    barcode: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    cost: float = Field(default=0, ge=0)
    tax_rate: float = Field(default=0.16, ge=0, le=1)
    category_id: int
    unit: str = "pieza"
    image_url: Optional[str] = None
    allow_decimal_qty: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    tax_rate: Optional[float] = None
    category_id: Optional[int] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    allow_decimal_qty: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    category: Optional[CategoryResponse] = None
    price_with_tax: float = 0
    
    class Config:
        from_attributes = True


class ProductWithStockResponse(ProductDetailResponse):
    stock: int = 0
    branch_price: Optional[float] = None
    is_available: bool = True
