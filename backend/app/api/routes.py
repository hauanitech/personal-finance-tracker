from fastapi import APIRouter

from app.api.users.routes import router

api_router = APIRouter(prefix="/api")

api_router.include_router(router=router)
