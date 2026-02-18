from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.branch import BranchProduct
    from app.models.sale import SaleItem


class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)  # Icon name for UI
    color: Mapped[str] = mapped_column(String(20), default="#3B82F6")  # Hex color
    
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", lazy="selectin")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent", lazy="selectin")
    parent: Mapped[Optional["Category"]] = relationship("Category", back_populates="children", remote_side=[id])
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, default=0)  # Cost price
    tax_rate: Mapped[float] = mapped_column(Float, default=0.16)  # 16% IVA default
    
    # Product details
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="pieza")  # pieza, kg, litro, etc.
    
    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_decimal_qty: Mapped[bool] = mapped_column(Boolean, default=False)  # For products sold by weight
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products", lazy="selectin")
    branch_stocks: Mapped[List["BranchProduct"]] = relationship("BranchProduct", back_populates="product", lazy="selectin")
    sale_items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="product", lazy="selectin")
    
    @property
    def price_with_tax(self) -> float:
        return self.price * (1 + self.tax_rate)
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
