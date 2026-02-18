from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.sale import Sale


class Branch(Base):
    __tablename__ = "branches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="México")
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)  # Main/HQ branch
    
    # Operating hours (stored as JSON string or separate fields)
    opening_time: Mapped[str] = mapped_column(String(10), default="09:00")
    closing_time: Mapped[str] = mapped_column(String(10), default="21:00")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User", 
        secondary="user_branches", 
        back_populates="branches"
    )
    products: Mapped[List["BranchProduct"]] = relationship("BranchProduct", back_populates="branch", lazy="selectin")
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="branch", lazy="selectin")
    
    def __repr__(self):
        return f"<Branch {self.code}: {self.name}>"


class BranchProduct(Base):
    """Inventory per branch - tracks stock and prices per branch"""
    __tablename__ = "branch_products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id", ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete='CASCADE'), nullable=False)
    
    stock: Mapped[int] = mapped_column(Integer, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, default=5)  # Alert threshold
    max_stock: Mapped[int] = mapped_column(Integer, default=100)
    
    # Branch-specific pricing (optional, falls back to product price)
    custom_price: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    last_restock: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branch: Mapped["Branch"] = relationship("Branch", back_populates="products")
    product: Mapped["Product"] = relationship("Product", back_populates="branch_stocks", lazy="selectin")
    
    def __repr__(self):
        return f"<BranchProduct branch={self.branch_id} product={self.product_id} stock={self.stock}>"
