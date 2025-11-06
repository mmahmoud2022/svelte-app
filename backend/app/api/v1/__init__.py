"""
API routes
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, doctor

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router)

# Include admin routes
api_router.include_router(admin.router)

# Include doctor routes
api_router.include_router(doctor.router)
