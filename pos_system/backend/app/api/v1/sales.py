from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.sale import Sale, SaleItem, SaleStatus, DeliveryStatus, PaymentMethod
from app.models.product import Product
from app.models.branch import Branch, BranchProduct
from app.schemas.sale import (
    SaleCreate, SaleUpdate, SaleResponse, SaleDetailResponse,
    DeliveryAssignRequest, DeliveryUpdateRequest,
    SaleStatusEnum, DeliveryStatusEnum
)
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/sales", tags=["Sales"])


def generate_sale_number(branch_code: str) -> str:
    """Generate unique sale number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:4].upper()
    return f"{branch_code}-{timestamp}-{unique_id}"


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    branch_id: Optional[int] = None,
    cashier_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    status: Optional[SaleStatusEnum] = None,
    delivery_status: Optional[DeliveryStatusEnum] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sales with filters
    """
    query = select(Sale)
    
    # Filter by user role
    if current_user.role.name == "cashier":
        query = query.where(Sale.cashier_id == current_user.id)
    elif current_user.role.name == "delivery":
        query = query.where(Sale.delivery_person_id == current_user.id)
    elif current_user.role.name == "customer":
        query = query.where(Sale.customer_id == current_user.id)
    else:
        # Admin can filter by any field
        if branch_id:
            query = query.where(Sale.branch_id == branch_id)
        if cashier_id:
            query = query.where(Sale.cashier_id == cashier_id)
        if customer_id:
            query = query.where(Sale.customer_id == customer_id)
    
    if status:
        query = query.where(Sale.status == status.value)
    
    if delivery_status:
        query = query.where(Sale.delivery_status == delivery_status.value)
    
    if date_from:
        query = query.where(Sale.created_at >= date_from)
    
    if date_to:
        query = query.where(Sale.created_at <= date_to)
    
    query = query.offset(skip).limit(limit).order_by(Sale.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{sale_id}", response_model=SaleDetailResponse)
async def get_sale(
    sale_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sale by ID with details
    """
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    # Check access
    if current_user.role.name not in ["admin", "superadmin"]:
        if current_user.role.name == "cashier" and sale.cashier_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta venta")
        if current_user.role.name == "delivery" and sale.delivery_person_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta venta")
        if current_user.role.name == "customer" and sale.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta venta")
    
    return SaleDetailResponse(
        id=sale.id,
        sale_number=sale.sale_number,
        branch_id=sale.branch_id,
        cashier_id=sale.cashier_id,
        customer_id=sale.customer_id,
        delivery_person_id=sale.delivery_person_id,
        subtotal=sale.subtotal,
        tax_amount=sale.tax_amount,
        discount_amount=sale.discount_amount,
        total=sale.total,
        payment_method=sale.payment_method,
        amount_received=sale.amount_received,
        change_given=sale.change_given,
        status=sale.status,
        delivery_status=sale.delivery_status,
        delivery_address=sale.delivery_address,
        delivery_notes=sale.delivery_notes,
        notes=sale.notes,
        created_at=sale.created_at,
        completed_at=sale.completed_at,
        delivered_at=sale.delivered_at,
        items=sale.items,
        branch_name=sale.branch.name if sale.branch else None,
        cashier_name=sale.cashier.full_name if sale.cashier else None,
        customer_name=sale.customer.full_name if sale.customer else None,
        delivery_person_name=sale.delivery_person.full_name if sale.delivery_person else None
    )


@router.post("/", response_model=SaleDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new sale
    """
    # Verify branch exists
    branch_result = await db.execute(select(Branch).where(Branch.id == sale_data.branch_id))
    branch = branch_result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    # Process items and calculate totals
    subtotal = 0
    tax_amount = 0
    discount_amount = 0
    sale_items = []
    
    for item_data in sale_data.items:
        # Get product
        product_result = await db.execute(select(Product).where(Product.id == item_data.product_id))
        product = product_result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item_data.product_id} no encontrado"
            )
        
        # Get branch-specific stock
        bp_result = await db.execute(
            select(BranchProduct).where(
                (BranchProduct.branch_id == sale_data.branch_id) &
                (BranchProduct.product_id == item_data.product_id)
            )
        )
        branch_product = bp_result.scalar_one_or_none()
        
        # Check stock
        if branch_product and branch_product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para {product.name}. Disponible: {branch_product.stock}"
            )
        
        # Calculate item totals
        unit_price = branch_product.custom_price if (branch_product and branch_product.custom_price) else product.price
        item_subtotal = unit_price * item_data.quantity
        item_tax = item_subtotal * product.tax_rate
        item_discount = item_data.discount
        item_total = item_subtotal + item_tax - item_discount
        
        subtotal += item_subtotal
        tax_amount += item_tax
        discount_amount += item_discount
        
        # Create sale item
        sale_item = SaleItem(
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            tax_rate=product.tax_rate,
            discount=item_discount,
            subtotal=item_subtotal,
            tax_amount=item_tax,
            total=item_total,
            product_name=product.name,
            product_sku=product.sku
        )
        sale_items.append(sale_item)
        
        # Update stock
        if branch_product:
            branch_product.stock -= int(item_data.quantity)
    
    total = subtotal + tax_amount - discount_amount
    
    # Create sale
    sale = Sale(
        sale_number=generate_sale_number(branch.code),
        branch_id=sale_data.branch_id,
        cashier_id=current_user.id,
        customer_id=sale_data.customer_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total=total,
        payment_method=PaymentMethod(sale_data.payment_method.value),
        amount_received=sale_data.amount_received,
        change_given=max(0, sale_data.amount_received - total),
        status=SaleStatus.COMPLETED,
        completed_at=datetime.utcnow(),
        delivery_status=DeliveryStatus.PENDING if sale_data.requires_delivery else DeliveryStatus.NOT_REQUIRED,
        delivery_address=sale_data.delivery_address,
        delivery_notes=sale_data.delivery_notes,
        notes=sale_data.notes
    )
    
    db.add(sale)
    await db.flush()
    
    # Link items to sale
    for item in sale_items:
        item.sale_id = sale.id
        db.add(item)
    
    await db.commit()
    await db.refresh(sale)
    
    return SaleDetailResponse(
        id=sale.id,
        sale_number=sale.sale_number,
        branch_id=sale.branch_id,
        cashier_id=sale.cashier_id,
        customer_id=sale.customer_id,
        delivery_person_id=sale.delivery_person_id,
        subtotal=sale.subtotal,
        tax_amount=sale.tax_amount,
        discount_amount=sale.discount_amount,
        total=sale.total,
        payment_method=sale.payment_method,
        amount_received=sale.amount_received,
        change_given=sale.change_given,
        status=sale.status,
        delivery_status=sale.delivery_status,
        delivery_address=sale.delivery_address,
        delivery_notes=sale.delivery_notes,
        notes=sale.notes,
        created_at=sale.created_at,
        completed_at=sale.completed_at,
        delivered_at=sale.delivered_at,
        items=sale.items,
        branch_name=branch.name,
        cashier_name=current_user.full_name
    )


@router.put("/{sale_id}/cancel", response_model=SaleResponse)
async def cancel_sale(
    sale_id: int,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel sale (Admin only)
    """
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    if sale.status == SaleStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La venta ya está cancelada"
        )
    
    # Restore stock
    for item in sale.items:
        bp_result = await db.execute(
            select(BranchProduct).where(
                (BranchProduct.branch_id == sale.branch_id) &
                (BranchProduct.product_id == item.product_id)
            )
        )
        branch_product = bp_result.scalar_one_or_none()
        if branch_product:
            branch_product.stock += int(item.quantity)
    
    sale.status = SaleStatus.CANCELLED
    await db.commit()
    await db.refresh(sale)
    
    return sale


# ==================== DELIVERY ENDPOINTS ====================

@router.get("/delivery/pending", response_model=List[SaleResponse])
async def get_pending_deliveries(
    branch_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending deliveries
    """
    query = select(Sale).where(
        Sale.delivery_status.in_([DeliveryStatus.PENDING, DeliveryStatus.ASSIGNED])
    )
    
    if branch_id:
        query = query.where(Sale.branch_id == branch_id)
    
    # Delivery person sees only assigned deliveries
    if current_user.role.name == "delivery":
        query = query.where(
            (Sale.delivery_person_id == current_user.id) |
            (Sale.delivery_status == DeliveryStatus.PENDING)
        )
    
    query = query.order_by(Sale.created_at.asc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/{sale_id}/assign-delivery", response_model=SaleResponse)
async def assign_delivery(
    sale_id: int,
    data: DeliveryAssignRequest,
    current_user: User = Depends(require_roles("admin", "superadmin", "cashier")),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign delivery person to sale
    """
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    if sale.delivery_status == DeliveryStatus.NOT_REQUIRED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta venta no requiere entrega"
        )
    
    # Verify delivery person exists and has delivery role
    delivery_result = await db.execute(select(User).where(User.id == data.delivery_person_id))
    delivery_person = delivery_result.scalar_one_or_none()
    
    if not delivery_person or delivery_person.role.name != "delivery":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es un repartidor válido"
        )
    
    sale.delivery_person_id = data.delivery_person_id
    sale.delivery_status = DeliveryStatus.ASSIGNED
    
    await db.commit()
    await db.refresh(sale)
    
    return sale


@router.put("/{sale_id}/delivery-status", response_model=SaleResponse)
async def update_delivery_status(
    sale_id: int,
    data: DeliveryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update delivery status (Delivery person)
    """
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    # Verify access
    if current_user.role.name == "delivery" and sale.delivery_person_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta entrega"
        )
    
    sale.delivery_status = DeliveryStatus(data.delivery_status.value)
    
    if data.notes:
        sale.delivery_notes = data.notes
    
    if data.delivery_status == DeliveryStatusEnum.DELIVERED:
        sale.delivered_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(sale)
    
    return sale


# ==================== REPORTS ====================

@router.get("/reports/summary")
async def get_sales_summary(
    branch_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sales summary report
    """
    query = select(
        func.count(Sale.id).label("total_sales"),
        func.sum(Sale.total).label("total_revenue"),
        func.sum(Sale.tax_amount).label("total_tax"),
        func.sum(Sale.discount_amount).label("total_discounts"),
        func.avg(Sale.total).label("average_sale")
    ).where(Sale.status == SaleStatus.COMPLETED)
    
    if branch_id:
        query = query.where(Sale.branch_id == branch_id)
    
    if date_from:
        query = query.where(Sale.created_at >= date_from)
    
    if date_to:
        query = query.where(Sale.created_at <= date_to)
    
    result = await db.execute(query)
    row = result.fetchone()
    
    return {
        "total_sales": row.total_sales or 0,
        "total_revenue": float(row.total_revenue or 0),
        "total_tax": float(row.total_tax or 0),
        "total_discounts": float(row.total_discounts or 0),
        "average_sale": float(row.average_sale or 0)
    }
