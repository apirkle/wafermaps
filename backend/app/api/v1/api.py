from fastapi import APIRouter

from app.api.v1.endpoints import auth, wafers, inspections, defects, equipment, analytics, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wafers.router, prefix="/wafers", tags=["wafers"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(defects.router, prefix="/defects", tags=["defects"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
