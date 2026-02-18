from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.branch import Branch, BranchProduct
from app.models.product import Product
from app.schemas.branch import (
    BranchCreate, BranchUpdate, BranchResponse,
    BranchProductCreate, BranchProductUpdate, BranchProductResponse,
    StockUpdateRequest
)
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("/", response_model=List[BranchResponse])
async def get_branches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all branches
    """
    query = select(Branch)
    
    if is_active is not None:
        query = query.where(Branch.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(Branch.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get branch by ID
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    return branch


@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch_data: BranchCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new branch (Admin only)
    """
    # Check if code already exists
    result = await db.execute(select(Branch).where(Branch.code == branch_data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de sucursal ya existe"
        )
    
    branch = Branch(**branch_data.model_dump())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    
    return branch


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update branch (Admin only)
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    update_data = branch_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    
    await db.commit()
    await db.refresh(branch)
    
    return branch


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: int,
    current_user: User = Depends(require_roles("superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate branch (Superadmin only)
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    branch.is_active = False
    await db.commit()
    
    return None


# ==================== BRANCH INVENTORY ====================

@router.get("/{branch_id}/inventory", response_model=List[BranchProductResponse])
async def get_branch_inventory(
    branch_id: int,
    low_stock: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get branch inventory
    """
    query = select(BranchProduct).where(BranchProduct.branch_id == branch_id)
    
    if low_stock:
        query = query.where(BranchProduct.stock <= BranchProduct.min_stock)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{branch_id}/inventory", response_model=BranchProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product_to_branch(
    branch_id: int,
    data: BranchProductCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Add product to branch inventory
    """
    # Check if already exists
    result = await db.execute(
        select(BranchProduct).where(
            (BranchProduct.branch_id == branch_id) &
            (BranchProduct.product_id == data.product_id)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El producto ya existe en esta sucursal"
        )
    
    branch_product = BranchProduct(
        branch_id=branch_id,
        product_id=data.product_id,
        stock=data.stock,
        min_stock=data.min_stock,
        max_stock=data.max_stock,
        custom_price=data.custom_price,
        is_available=data.is_available
    )
    db.add(branch_product)
    await db.commit()
    await db.refresh(branch_product)
    
    return branch_product


@router.put("/{branch_id}/inventory/{product_id}/stock", response_model=BranchProductResponse)
async def update_stock(
    branch_id: int,
    product_id: int,
    data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update product stock in branch
    """
    result = await db.execute(
        select(BranchProduct).where(
            (BranchProduct.branch_id == branch_id) &
            (BranchProduct.product_id == product_id)
        )
    )
    branch_product = result.scalar_one_or_none()
    
    if not branch_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en esta sucursal"
        )
    
    new_stock = branch_product.stock + data.quantity
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El stock no puede ser negativo"
        )
    
    branch_product.stock = new_stock
    if data.quantity > 0:
        from datetime import datetime
        branch_product.last_restock = datetime.utcnow()
    
    await db.commit()
    await db.refresh(branch_product)
    
    return branch_product
