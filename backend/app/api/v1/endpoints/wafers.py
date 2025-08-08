from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import math

from app.core.database import get_db
from app.models.wafer import Wafer
from app.schemas.wafer import WaferResponse, WaferListResponse

router = APIRouter()

@router.get("/", response_model=WaferListResponse)
async def get_wafers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    wafer_id: Optional[str] = Query(None, description="Filter by wafer ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of wafers with pagination and filtering"""
    
    # Build query
    query = select(Wafer)
    count_query = select(func.count(Wafer.wafer_id))
    
    # Apply filters
    if wafer_id:
        query = query.where(Wafer.wafer_id.contains(wafer_id))
        count_query = count_query.where(Wafer.wafer_id.contains(wafer_id))
    
    # Get total count
    result = await db.execute(count_query)
    total_count = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Get wafers
    result = await db.execute(query)
    wafers = result.scalars().all()
    
    # Calculate pagination info
    total_pages = math.ceil(total_count / page_size)
    
    return WaferListResponse(
        items=[WaferResponse.from_orm(wafer) for wafer in wafers],
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{wafer_id}", response_model=WaferResponse)
async def get_wafer(wafer_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific wafer by ID"""
    result = await db.execute(select(Wafer).where(Wafer.wafer_id == wafer_id))
    wafer = result.scalar_one_or_none()
    
    if not wafer:
        raise HTTPException(status_code=404, detail="Wafer not found")
    
    return WaferResponse.from_orm(wafer)
