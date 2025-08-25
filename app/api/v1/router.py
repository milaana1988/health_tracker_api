from fastapi import APIRouter
from .endpoints import users, activities, sleeps, blood_tests, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(sleeps.router, prefix="/sleeps", tags=["sleeps"])
api_router.include_router(blood_tests.router, prefix="/blood-tests", tags=["blood-tests"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
