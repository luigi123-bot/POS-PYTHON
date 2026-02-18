from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.session import get_db
from app.models.user import User
from app.models.product import Product, Category
from app.models.branch import BranchProduct
from app.schemas.product import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductDetailResponse, ProductWithStockResponse
)
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/products", tags=["Products"])


# ==================== CATEGORIES ====================

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all categories
    """
    query = select(Category)
    
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    
    query = query.order_by(Category.sort_order, Category.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new category (Admin only)
    """
    # Check if slug exists
    result = await db.execute(select(Category).where(Category.slug == category_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El slug de categoría ya existe"
        )
    
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update category (Admin only)
    """
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate category (Admin only)
    """
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    category.is_active = False
    await db.commit()
    
    return None


# ==================== PRODUCTS ====================

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all products
    """
    query = select(Product)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    
    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_filter),
                Product.sku.ilike(search_filter),
                Product.barcode.ilike(search_filter)
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(Product.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/by-barcode/{barcode}", response_model=ProductDetailResponse)
async def get_product_by_barcode(
    barcode: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get product by barcode (for scanner)
    """
    result = await db.execute(
        select(Product).where(
            or_(Product.barcode == barcode, Product.sku == barcode)
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return ProductDetailResponse(
        **product.__dict__,
        price_with_tax=product.price_with_tax
    )


@router.get("/branch/{branch_id}", response_model=List[ProductWithStockResponse])
async def get_products_with_stock(
    branch_id: int,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    available_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get products with stock info for specific branch
    """
    query = select(Product, BranchProduct).outerjoin(
        BranchProduct,
        (Product.id == BranchProduct.product_id) & (BranchProduct.branch_id == branch_id)
    ).where(Product.is_active == True)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_filter),
                Product.sku.ilike(search_filter),
                Product.barcode.ilike(search_filter)
            )
        )
    
    if available_only:
        query = query.where(
            or_(
                BranchProduct.is_available == True,
                BranchProduct.id == None
            )
        )
    
    result = await db.execute(query)
    products = []
    
    for product, branch_product in result.fetchall():
        products.append(ProductWithStockResponse(
            id=product.id,
            sku=product.sku,
            barcode=product.barcode,
            name=product.name,
            description=product.description,
            price=product.price,
            cost=product.cost,
            tax_rate=product.tax_rate,
            category_id=product.category_id,
            unit=product.unit,
            image_url=product.image_url,
            allow_decimal_qty=product.allow_decimal_qty,
            is_active=product.is_active,
            is_featured=product.is_featured,
            created_at=product.created_at,
            updated_at=product.updated_at,
            category=product.category,
            price_with_tax=product.price_with_tax,
            stock=branch_product.stock if branch_product else 0,
            branch_price=branch_product.custom_price if branch_product else None,
            is_available=branch_product.is_available if branch_product else True
        ))
    
    return products


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get product by ID
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return ProductDetailResponse(
        **product.__dict__,
        price_with_tax=product.price_with_tax
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new product (Admin only)
    """
    # Check if SKU exists
    result = await db.execute(select(Product).where(Product.sku == product_data.sku))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El SKU ya existe"
        )
    
    # Check barcode if provided
    if product_data.barcode:
        result = await db.execute(select(Product).where(Product.barcode == product_data.barcode))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de barras ya existe"
            )
    
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update product (Admin only)
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate product (Admin only)
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    product.is_active = False
    await db.commit()
    
    return None
