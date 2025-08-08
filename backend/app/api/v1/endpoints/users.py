from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """Get list of users"""
    return {"message": "Users endpoint - coming soon"}
