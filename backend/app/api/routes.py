from fastapi import APIRouter

from api.users.routes import router as user_router
from api.accounts.routes import router as account_router
from api.orders.routes import router as order_router

api_router = APIRouter(prefix="/api")

api_router.include_router(router=user_router)
api_router.include_router(router=account_router)
api_router.include_router(router=order_router)
