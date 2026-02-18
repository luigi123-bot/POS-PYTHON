from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    MIXED = "mixed"


class SaleStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class DeliveryStatusEnum(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


# Sale Item schemas
class SaleItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    discount: float = Field(default=0, ge=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit_price: float
    tax_rate: float
    discount: float
    subtotal: float
    tax_amount: float
    total: float
    product_name: str
    product_sku: str
    
    class Config:
        from_attributes = True


# Sale schemas
class SaleBase(BaseModel):
    branch_id: int
    customer_id: Optional[int] = None
    payment_method: PaymentMethodEnum = PaymentMethodEnum.CASH
    delivery_address: Optional[str] = None
    delivery_notes: Optional[str] = None
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]
    amount_received: float = Field(default=0, ge=0)
    requires_delivery: bool = False


class SaleUpdate(BaseModel):
    payment_method: Optional[PaymentMethodEnum] = None
    status: Optional[SaleStatusEnum] = None
    delivery_status: Optional[DeliveryStatusEnum] = None
    delivery_person_id: Optional[int] = None
    delivery_address: Optional[str] = None
    delivery_notes: Optional[str] = None
    notes: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    sale_number: str
    branch_id: int
    cashier_id: int
    customer_id: Optional[int] = None
    delivery_person_id: Optional[int] = None
    subtotal: float
    tax_amount: float
    discount_amount: float
    total: float
    payment_method: PaymentMethodEnum
    amount_received: float
    change_given: float
    status: SaleStatusEnum
    delivery_status: DeliveryStatusEnum
    delivery_address: Optional[str] = None
    delivery_notes: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SaleDetailResponse(SaleResponse):
    items: List[SaleItemResponse] = []
    branch_name: Optional[str] = None
    cashier_name: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_person_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Delivery specific schemas
class DeliveryAssignRequest(BaseModel):
    delivery_person_id: int


class DeliveryUpdateRequest(BaseModel):
    delivery_status: DeliveryStatusEnum
    notes: Optional[str] = None


# Cart schemas (for frontend use)
class CartItem(BaseModel):
    product_id: int
    product_name: str
    product_sku: str
    unit_price: float
    quantity: float
    discount: float = 0
    subtotal: float
    tax_amount: float
    total: float


class CartSummary(BaseModel):
    items: List[CartItem]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total: float
    item_count: int
