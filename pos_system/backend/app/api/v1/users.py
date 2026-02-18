from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User, user_branches
from app.models.branch import Branch
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    UserDetailResponse, UserPasswordUpdate
)
from app.core.security import (
    get_current_user, 
    get_password_hash, 
    verify_password,
    require_roles
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    branch_id: Optional[int] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users with optional filters (Admin only)
    """
    query = select(User)
    
    if branch_id:
        query = query.join(user_branches).where(user_branches.c.branch_id == branch_id)
    
    if role_id:
        query = query.where(User.role_id == role_id)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (User.username.ilike(search_filter)) |
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID
    """
    # Users can only view themselves unless admin
    if current_user.id != user_id and current_user.role.name not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este usuario"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    permissions = await user.get_permissions(db)
    
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role_id=user.role_id,
        primary_branch_id=user.primary_branch_id,
        created_at=user.created_at,
        last_login=user.last_login,
        role=user.role,
        primary_branch=user.primary_branch,
        permissions=permissions
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user (Admin only)
    """
    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario o email ya existe"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role_id=user_data.role_id,
        primary_branch_id=user_data.primary_branch_id
    )
    
    db.add(user)
    await db.flush()
    
    # Assign branches
    if user_data.branch_ids:
        for branch_id in user_data.branch_ids:
            await db.execute(
                user_branches.insert().values(user_id=user.id, branch_id=branch_id)
            )
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user
    """
    # Users can only update themselves unless admin
    if current_user.id != user_id and current_user.role.name not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este usuario"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Only admins can change role and active status
    if current_user.role.name not in ["admin", "superadmin"]:
        update_data.pop("role_id", None)
        update_data.pop("is_active", None)
    
    # Handle branch_ids separately
    branch_ids = update_data.pop("branch_ids", None)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Update branches if provided
    if branch_ids is not None and current_user.role.name in ["admin", "superadmin"]:
        # Remove existing branches
        await db.execute(
            user_branches.delete().where(user_branches.c.user_id == user_id)
        )
        # Add new branches
        for branch_id in branch_ids:
            await db.execute(
                user_branches.insert().values(user_id=user_id, branch_id=branch_id)
            )
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.put("/{user_id}/password")
async def update_password(
    user_id: int,
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user password
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes cambiar tu propia contraseña"
        )
    
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate user (Admin only)
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Soft delete - deactivate instead of delete
    user.is_active = False
    await db.commit()
    
    return None
