from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.role import Role, Permission, role_permissions
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleDetailResponse,
    PermissionCreate, PermissionResponse, RolePermissionUpdate
)
from app.core.security import require_roles

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


# ==================== PERMISSIONS ====================

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all permissions
    """
    result = await db.execute(select(Permission).order_by(Permission.module, Permission.name))
    return result.scalars().all()


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_roles("superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new permission (Superadmin only)
    """
    # Check if code already exists
    result = await db.execute(
        select(Permission).where(Permission.code == permission_data.code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de permiso ya existe"
        )
    
    permission = Permission(**permission_data.model_dump())
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    
    return permission


# ==================== ROLES ====================

@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all roles
    """
    result = await db.execute(select(Role).order_by(Role.name))
    return result.scalars().all()


@router.get("/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get role by ID with permissions
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new role
    """
    # Check if name already exists
    result = await db.execute(select(Role).where(Role.name == role_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del rol ya existe"
        )
    
    # Create role
    role = Role(
        name=role_data.name,
        display_name=role_data.display_name,
        description=role_data.description
    )
    db.add(role)
    await db.flush()
    
    # Assign permissions
    if role_data.permission_ids:
        for perm_id in role_data.permission_ids:
            await db.execute(
                role_permissions.insert().values(role_id=role.id, permission_id=perm_id)
            )
    
    await db.commit()
    await db.refresh(role)
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update role
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden modificar roles del sistema"
        )
    
    update_data = role_data.model_dump(exclude_unset=True)
    permission_ids = update_data.pop("permission_ids", None)
    
    for field, value in update_data.items():
        setattr(role, field, value)
    
    # Update permissions if provided
    if permission_ids is not None:
        await db.execute(
            role_permissions.delete().where(role_permissions.c.role_id == role_id)
        )
        for perm_id in permission_ids:
            await db.execute(
                role_permissions.insert().values(role_id=role_id, permission_id=perm_id)
            )
    
    await db.commit()
    await db.refresh(role)
    
    return role


@router.put("/{role_id}/permissions", response_model=RoleDetailResponse)
async def update_role_permissions(
    role_id: int,
    data: RolePermissionUpdate,
    current_user: User = Depends(require_roles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update role permissions
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Clear existing permissions
    await db.execute(
        role_permissions.delete().where(role_permissions.c.role_id == role_id)
    )
    
    # Add new permissions
    for perm_id in data.permission_ids:
        await db.execute(
            role_permissions.insert().values(role_id=role_id, permission_id=perm_id)
        )
    
    await db.commit()
    await db.refresh(role)
    
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_roles("superadmin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete role (Superadmin only)
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden eliminar roles del sistema"
        )
    
    # Check if role is in use
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un rol que tiene usuarios asignados"
        )
    
    await db.delete(role)
    await db.commit()
    
    return None
