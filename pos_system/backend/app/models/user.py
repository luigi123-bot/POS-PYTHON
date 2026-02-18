from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.branch import Branch

# Association table for user branches (many-to-many)
user_branches = Table(
    'user_branches',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('branch_id', Integer, ForeignKey('branches.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    primary_branch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("branches.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    primary_branch: Mapped[Optional["Branch"]] = relationship("Branch", foreign_keys=[primary_branch_id], lazy="selectin")
    branches: Mapped[List["Branch"]] = relationship("Branch", secondary=user_branches, back_populates="users", lazy="selectin")
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="cashier", foreign_keys="Sale.cashier_id", lazy="selectin")
    deliveries: Mapped[List["Sale"]] = relationship("Sale", back_populates="delivery_person", foreign_keys="Sale.delivery_person_id", lazy="selectin")
    
    async def get_permissions(self, db: AsyncSession) -> List[str]:
        """Get all permissions for this user"""
        await db.refresh(self, ["role"])
        if self.role:
            from app.models.role import RolePermission, Permission
            result = await db.execute(
                select(Permission.code)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == self.role_id)
            )
            return [row[0] for row in result.fetchall()]
        return []
    
    def __repr__(self):
        return f"<User {self.username}>"


# Import Sale here to avoid circular imports
from app.models.sale import Sale
