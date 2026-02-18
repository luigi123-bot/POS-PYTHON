# Sistema POS Multi-Sucursal

Sistema de Punto de Venta completo con backend FastAPI y frontend Flutter, diseñado para gestionar múltiples sucursales con roles y permisos configurables.

## 🚀 Características

### Backend (FastAPI)
- ✅ API REST con FastAPI 0.109+
- ✅ Autenticación JWT con expiración configurable
- ✅ Sistema de roles y permisos granular
- ✅ Base de datos SQLite (desarrollo) / PostgreSQL (producción)
- ✅ ORM async con SQLAlchemy 2.0
- ✅ Validación de datos con Pydantic
- ✅ CORS configurado para desarrollo

### Frontend (Flutter)
- ✅ UI moderna y responsiva con Material Design 3
- ✅ Gestión de estado con Riverpod
- ✅ Navegación con GoRouter
- ✅ Cliente HTTP con Dio y manejo de errores
- ✅ Almacenamiento seguro de tokens
- ✅ Dashboards personalizados por rol

### Roles del Sistema
| Rol | Descripción |
|-----|-------------|
| **Super Admin** | Acceso total al sistema |
| **Administrador** | Gestión de sucursal asignada |
| **Cajero** | Operaciones de venta en caja |
| **Repartidor** | Gestión de entregas |
| **Cliente** | Consulta de pedidos y catálogo |

---

## 📋 Requisitos Previos

### Backend
- Python 3.10 o superior
- pip (gestor de paquetes Python)

### Frontend
- Flutter SDK 3.0 o superior
- Dart SDK 3.0 o superior

---

## 🛠️ Instalación

### 1. Clonar/Descargar el Proyecto

```bash
cd c:\Users\Monitor Mañana\Downloads\python\pos_system
```

### 2. Configurar el Backend

```powershell
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
copy .env.example .env
```

#### Configuración del archivo `.env`:

```env
# Base de datos (SQLite para desarrollo)
DATABASE_URL=sqlite+aiosqlite:///./pos_database.db

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura-cambiar-en-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080

# Entorno
ENVIRONMENT=development
DEBUG=true
```

### 3. Configurar el Frontend

```powershell
# Navegar al directorio frontend
cd ..\frontend

# Obtener dependencias
flutter pub get
```

---

## ▶️ Ejecución

### Paso 1: Iniciar el Backend

```powershell
# Desde el directorio backend con el entorno virtual activado
cd c:\Users\Monitor Mañana\Downloads\python\pos_system\backend
.\venv\Scripts\Activate.ps1

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

### Paso 2: Iniciar el Frontend

```powershell
# En otra terminal, desde el directorio frontend
cd c:\Users\Monitor Mañana\Downloads\python\pos_system\frontend

# Ejecutar en modo debug
flutter run -d windows

# O para web
flutter run -d chrome
```

---

## 🔐 Credenciales de Prueba

El sistema inicializa automáticamente los siguientes usuarios:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Super Administrador |
| `cajero1` | `password123` | Cajero |
| `repartidor1` | `password123` | Repartidor |
| `cliente1` | `password123` | Cliente |

---

## 📚 Documentación de la API

Una vez iniciado el backend, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints Principales

#### Autenticación
```
POST /api/v1/auth/login          # Iniciar sesión
POST /api/v1/auth/register       # Registrar usuario
GET  /api/v1/auth/me             # Obtener usuario actual
```

#### Usuarios
```
GET    /api/v1/users/            # Listar usuarios
POST   /api/v1/users/            # Crear usuario
GET    /api/v1/users/{id}        # Obtener usuario
PUT    /api/v1/users/{id}        # Actualizar usuario
DELETE /api/v1/users/{id}        # Eliminar usuario
```

#### Productos
```
GET    /api/v1/products/         # Listar productos
POST   /api/v1/products/         # Crear producto
GET    /api/v1/products/{id}     # Obtener producto
PUT    /api/v1/products/{id}     # Actualizar producto
DELETE /api/v1/products/{id}     # Eliminar producto
```

#### Ventas
```
GET    /api/v1/sales/            # Listar ventas
POST   /api/v1/sales/            # Crear venta
GET    /api/v1/sales/{id}        # Obtener venta
PUT    /api/v1/sales/{id}/status # Actualizar estado
```

#### Sucursales
```
GET    /api/v1/branches/         # Listar sucursales
POST   /api/v1/branches/         # Crear sucursal
GET    /api/v1/branches/{id}     # Obtener sucursal
PUT    /api/v1/branches/{id}     # Actualizar sucursal
```

---

## 📁 Estructura del Proyecto

```
pos_system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── roles.py
│   │   │       ├── branches.py
│   │   │       ├── products.py
│   │   │       └── sales.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── branch.py
│   │   │   ├── product.py
│   │   │   └── sale.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── branch.py
│   │   │   ├── product.py
│   │   │   └── sale.py
│   │   ├── init_data.py
│   │   └── main.py
│   ├── .env.example
│   └── requirements.txt
│
└── frontend/
    ├── lib/
    │   ├── core/
    │   │   ├── network/
    │   │   ├── router/
    │   │   └── theme/
    │   ├── features/
    │   │   ├── auth/
    │   │   ├── dashboard/
    │   │   ├── pos/
    │   │   ├── products/
    │   │   ├── sales/
    │   │   └── users/
    │   ├── shared/
    │   │   └── widgets/
    │   └── main.dart
    └── pubspec.yaml
```

---

## 🧪 Pruebas

### Backend
```powershell
# Ejecutar pruebas
pytest

# Con cobertura
pytest --cov=app
```

### Frontend
```powershell
# Ejecutar pruebas
flutter test

# Con cobertura
flutter test --coverage
```

---

## 🚀 Despliegue en Producción

### Backend (Docker)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables de Entorno para Producción

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/pos_db
SECRET_KEY=clave-super-secreta-generada-aleatoriamente
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://tu-dominio.com
```

---

## 📝 Notas Adicionales

### Migración de Base de Datos
Para aplicar migraciones cuando uses PostgreSQL:

```powershell
# Instalar alembic
pip install alembic

# Inicializar
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Initial"

# Aplicar migraciones
alembic upgrade head
```

### Regenerar Datos Iniciales
Si necesitas reiniciar los datos:

```powershell
# Eliminar la base de datos SQLite
Remove-Item pos_database.db

# Reiniciar el servidor (se recreará automáticamente)
uvicorn app.main:app --reload
```

---

## 🤝 Soporte

Para reportar problemas o solicitar nuevas características, por favor crea un issue en el repositorio.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
