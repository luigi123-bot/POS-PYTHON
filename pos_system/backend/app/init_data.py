"""
Script to initialize database with default data
Run: python -m app.init_data
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, init_db
from app.models.role import Role, Permission, role_permissions
from app.models.user import User
from app.models.branch import Branch
from app.models.product import Category, Product
from app.core.security import get_password_hash


# Default permissions
DEFAULT_PERMISSIONS = [
    # Sales
    {"code": "sales.create", "name": "Crear ventas", "module": "sales", "description": "Permite crear nuevas ventas"},
    {"code": "sales.view", "name": "Ver ventas", "module": "sales", "description": "Permite ver ventas"},
    {"code": "sales.cancel", "name": "Cancelar ventas", "module": "sales", "description": "Permite cancelar ventas"},
    {"code": "sales.refund", "name": "Reembolsar ventas", "module": "sales", "description": "Permite reembolsar ventas"},
    {"code": "sales.reports", "name": "Ver reportes de ventas", "module": "sales", "description": "Permite ver reportes de ventas"},
    
    # Products
    {"code": "products.view", "name": "Ver productos", "module": "products", "description": "Permite ver productos"},
    {"code": "products.create", "name": "Crear productos", "module": "products", "description": "Permite crear productos"},
    {"code": "products.edit", "name": "Editar productos", "module": "products", "description": "Permite editar productos"},
    {"code": "products.delete", "name": "Eliminar productos", "module": "products", "description": "Permite eliminar productos"},
    
    # Inventory
    {"code": "inventory.view", "name": "Ver inventario", "module": "inventory", "description": "Permite ver inventario"},
    {"code": "inventory.manage", "name": "Gestionar inventario", "module": "inventory", "description": "Permite gestionar inventario"},
    
    # Users
    {"code": "users.view", "name": "Ver usuarios", "module": "users", "description": "Permite ver usuarios"},
    {"code": "users.create", "name": "Crear usuarios", "module": "users", "description": "Permite crear usuarios"},
    {"code": "users.edit", "name": "Editar usuarios", "module": "users", "description": "Permite editar usuarios"},
    {"code": "users.delete", "name": "Eliminar usuarios", "module": "users", "description": "Permite eliminar usuarios"},
    
    # Roles
    {"code": "roles.view", "name": "Ver roles", "module": "roles", "description": "Permite ver roles"},
    {"code": "roles.manage", "name": "Gestionar roles", "module": "roles", "description": "Permite gestionar roles"},
    
    # Branches
    {"code": "branches.view", "name": "Ver sucursales", "module": "branches", "description": "Permite ver sucursales"},
    {"code": "branches.manage", "name": "Gestionar sucursales", "module": "branches", "description": "Permite gestionar sucursales"},
    
    # Delivery
    {"code": "delivery.view", "name": "Ver entregas", "module": "delivery", "description": "Permite ver entregas"},
    {"code": "delivery.manage", "name": "Gestionar entregas", "module": "delivery", "description": "Permite gestionar entregas"},
    {"code": "delivery.update_status", "name": "Actualizar estado de entrega", "module": "delivery", "description": "Permite actualizar estado"},
    
    # Customer
    {"code": "customer.purchase", "name": "Realizar compras", "module": "customer", "description": "Permite realizar compras"},
    {"code": "customer.history", "name": "Ver historial", "module": "customer", "description": "Permite ver historial de compras"},
    
    # Reports
    {"code": "reports.view", "name": "Ver reportes", "module": "reports", "description": "Permite ver reportes"},
    {"code": "reports.export", "name": "Exportar reportes", "module": "reports", "description": "Permite exportar reportes"},
    
    # Settings
    {"code": "settings.view", "name": "Ver configuración", "module": "settings", "description": "Permite ver configuración"},
    {"code": "settings.manage", "name": "Gestionar configuración", "module": "settings", "description": "Permite gestionar configuración"},
]

# Default roles with their permissions
DEFAULT_ROLES = [
    {
        "name": "superadmin",
        "display_name": "Super Administrador",
        "description": "Acceso total al sistema",
        "is_system": True,
        "permissions": ["*"]  # All permissions
    },
    {
        "name": "admin",
        "display_name": "Administrador",
        "description": "Administrador de sucursal",
        "is_system": True,
        "permissions": [
            "sales.create", "sales.view", "sales.cancel", "sales.reports",
            "products.view", "products.create", "products.edit",
            "inventory.view", "inventory.manage",
            "users.view", "users.create", "users.edit",
            "roles.view",
            "branches.view",
            "delivery.view", "delivery.manage",
            "reports.view", "reports.export",
            "settings.view"
        ]
    },
    {
        "name": "cashier",
        "display_name": "Cajero",
        "description": "Operador de caja",
        "is_system": True,
        "permissions": [
            "sales.create", "sales.view",
            "products.view",
            "inventory.view",
            "delivery.view"
        ]
    },
    {
        "name": "delivery",
        "display_name": "Repartidor",
        "description": "Personal de entregas",
        "is_system": True,
        "permissions": [
            "delivery.view", "delivery.update_status",
            "sales.view"
        ]
    },
    {
        "name": "customer",
        "display_name": "Cliente",
        "description": "Cliente registrado",
        "is_system": True,
        "permissions": [
            "customer.purchase", "customer.history",
            "products.view"
        ]
    }
]

# Default branch
DEFAULT_BRANCH = {
    "code": "SUC001",
    "name": "Sucursal Principal",
    "address": "Calle Principal #123",
    "city": "Ciudad de México",
    "state": "CDMX",
    "country": "México",
    "postal_code": "01000",
    "phone": "+52 55 1234 5678",
    "email": "principal@posystem.com",
    "is_main": True,
    "is_active": True
}

# Default categories
DEFAULT_CATEGORIES = [
    {"name": "Bebidas", "slug": "bebidas", "icon": "local_drink", "color": "#3B82F6", "sort_order": 1},
    {"name": "Alimentos", "slug": "alimentos", "icon": "restaurant", "color": "#10B981", "sort_order": 2},
    {"name": "Snacks", "slug": "snacks", "icon": "cookie", "color": "#F59E0B", "sort_order": 3},
    {"name": "Limpieza", "slug": "limpieza", "icon": "cleaning_services", "color": "#6366F1", "sort_order": 4},
    {"name": "Otros", "slug": "otros", "icon": "category", "color": "#8B5CF6", "sort_order": 5},
]

# Sample products
SAMPLE_PRODUCTS = [
    {"sku": "BEB001", "barcode": "7501234567890", "name": "Coca-Cola 600ml", "price": 18.00, "cost": 12.00, "category_slug": "bebidas"},
    {"sku": "BEB002", "barcode": "7501234567891", "name": "Agua Natural 1L", "price": 12.00, "cost": 6.00, "category_slug": "bebidas"},
    {"sku": "BEB003", "barcode": "7501234567892", "name": "Jugo de Naranja 500ml", "price": 25.00, "cost": 15.00, "category_slug": "bebidas"},
    {"sku": "ALI001", "barcode": "7501234567893", "name": "Sandwich Jamón y Queso", "price": 45.00, "cost": 25.00, "category_slug": "alimentos"},
    {"sku": "ALI002", "barcode": "7501234567894", "name": "Ensalada César", "price": 55.00, "cost": 30.00, "category_slug": "alimentos"},
    {"sku": "SNK001", "barcode": "7501234567895", "name": "Papas Fritas 150g", "price": 22.00, "cost": 12.00, "category_slug": "snacks"},
    {"sku": "SNK002", "barcode": "7501234567896", "name": "Galletas de Chocolate", "price": 18.00, "cost": 10.00, "category_slug": "snacks"},
    {"sku": "LIM001", "barcode": "7501234567897", "name": "Detergente 1L", "price": 35.00, "cost": 20.00, "category_slug": "limpieza"},
]


async def init_data():
    """Initialize database with default data"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if already initialized
            result = await db.execute(select(Role))
            if result.scalars().first():
                print("La base de datos ya está inicializada.")
                return
            
            print("Inicializando base de datos...")
            
            # Create permissions
            print("Creando permisos...")
            permission_map = {}
            for perm_data in DEFAULT_PERMISSIONS:
                permission = Permission(**perm_data)
                db.add(permission)
                await db.flush()
                permission_map[perm_data["code"]] = permission.id
            
            # Create roles
            print("Creando roles...")
            role_map = {}
            for role_data in DEFAULT_ROLES:
                role = Role(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data["description"],
                    is_system=role_data["is_system"]
                )
                db.add(role)
                await db.flush()
                role_map[role_data["name"]] = role.id
                
                # Assign permissions
                permissions = role_data["permissions"]
                if "*" in permissions:
                    # All permissions
                    for perm_id in permission_map.values():
                        await db.execute(
                            role_permissions.insert().values(role_id=role.id, permission_id=perm_id)
                        )
                else:
                    for perm_code in permissions:
                        if perm_code in permission_map:
                            await db.execute(
                                role_permissions.insert().values(
                                    role_id=role.id, 
                                    permission_id=permission_map[perm_code]
                                )
                            )
            
            # Create default branch
            print("Creando sucursal principal...")
            branch = Branch(**DEFAULT_BRANCH)
            db.add(branch)
            await db.flush()
            
            # Create default admin user
            print("Creando usuario administrador...")
            admin_user = User(
                email="admin@posystem.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrador del Sistema",
                phone="+52 55 1234 5678",
                role_id=role_map["superadmin"],
                primary_branch_id=branch.id,
                is_superuser=True
            )
            db.add(admin_user)
            
            # Create sample users for each role
            print("Creando usuarios de ejemplo...")
            sample_users = [
                {"username": "cajero1", "email": "cajero1@posystem.com", "full_name": "Juan Pérez (Cajero)", "role": "cashier"},
                {"username": "repartidor1", "email": "repartidor1@posystem.com", "full_name": "Carlos López (Repartidor)", "role": "delivery"},
                {"username": "cliente1", "email": "cliente1@posystem.com", "full_name": "María García (Cliente)", "role": "customer"},
            ]
            
            for user_data in sample_users:
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=get_password_hash("password123"),
                    full_name=user_data["full_name"],
                    role_id=role_map[user_data["role"]],
                    primary_branch_id=branch.id
                )
                db.add(user)
            
            # Create categories
            print("Creando categorías...")
            category_map = {}
            for cat_data in DEFAULT_CATEGORIES:
                category = Category(**cat_data)
                db.add(category)
                await db.flush()
                category_map[cat_data["slug"]] = category.id
            
            # Create sample products
            print("Creando productos de ejemplo...")
            for prod_data in SAMPLE_PRODUCTS:
                product = Product(
                    sku=prod_data["sku"],
                    barcode=prod_data["barcode"],
                    name=prod_data["name"],
                    price=prod_data["price"],
                    cost=prod_data["cost"],
                    category_id=category_map[prod_data["category_slug"]]
                )
                db.add(product)
            
            await db.commit()
            
            print("\n" + "="*50)
            print("¡Base de datos inicializada exitosamente!")
            print("="*50)
            print("\nUsuarios creados:")
            print("-" * 30)
            print("Admin:      admin / admin123")
            print("Cajero:     cajero1 / password123")
            print("Repartidor: repartidor1 / password123")
            print("Cliente:    cliente1 / password123")
            print("="*50)
            
        except Exception as e:
            await db.rollback()
            print(f"Error al inicializar: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_data())
