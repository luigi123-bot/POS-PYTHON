from fastapi import APIRouter
from app.api.v1 import auth, users, roles, branches, products, sales

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(branches.router)
api_router.include_router(products.router)
api_router.include_router(sales.router)
