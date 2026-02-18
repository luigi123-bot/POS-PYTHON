from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.branch import Branch
    from app.models.product import Product


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    MIXED = "mixed"


class SaleStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class DeliveryStatus(str, enum.Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class Sale(Base):
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)
    cashier_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_person_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Amounts
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Payment
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    amount_received: Mapped[float] = mapped_column(Float, default=0)
    change_given: Mapped[float] = mapped_column(Float, default=0)
    
    # Status
    status: Mapped[SaleStatus] = mapped_column(Enum(SaleStatus), default=SaleStatus.PENDING)
    
    # Delivery info
    delivery_status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.NOT_REQUIRED)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    branch: Mapped["Branch"] = relationship("Branch", back_populates="sales", lazy="selectin")
    cashier: Mapped["User"] = relationship("User", back_populates="sales", foreign_keys=[cashier_id], lazy="selectin")
    customer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[customer_id], lazy="selectin")
    delivery_person: Mapped[Optional["User"]] = relationship("User", back_populates="deliveries", foreign_keys=[delivery_person_id], lazy="selectin")
    items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="sale", lazy="selectin", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale {self.sale_number} total={self.total}>"


class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(Integer, ForeignKey("sales.id", ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Float, default=0.16)
    discount: Mapped[float] = mapped_column(Float, default=0)
    
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Snapshot of product info at time of sale
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_sku: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationships
    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_items", lazy="selectin")
    
    def __repr__(self):
        return f"<SaleItem {self.product_name} x{self.quantity}>"
