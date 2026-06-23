from fastapi import APIRouter
from app.v1.endpoints import auth, health

api_router = APIRouter()

# Mount auth routes at /api/v1/auth/...
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Mount health status routes at /api/v1/health/...
api_router.include_router(health.router, prefix="/health", tags=["Health"])
