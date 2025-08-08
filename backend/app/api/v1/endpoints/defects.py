from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import math

from app.core.database import get_db
from app.models.defect import Defect
from app.schemas.defect import DefectResponse, DefectListResponse

router = APIRouter()

@router.get("/", response_model=DefectListResponse)
async def get_defects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    inspection_id: Optional[str] = Query(None, description="Filter by inspection ID"),
    defect_type: Optional[str] = Query(None, description="Filter by defect type"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of defects with pagination and filtering"""
    
    # Build query
    query = select(Defect)
    count_query = select(func.count(Defect.defect_id))
    
    # Apply filters
    if inspection_id:
        query = query.where(Defect.inspection_id == inspection_id)
        count_query = count_query.where(Defect.inspection_id == inspection_id)
    
    if defect_type:
        query = query.where(Defect.defect_type.contains(defect_type))
        count_query = count_query.where(Defect.defect_type.contains(defect_type))
    
    # Get total count
    result = await db.execute(count_query)
    total_count = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Get defects
    result = await db.execute(query)
    defects = result.scalars().all()
    
    # Calculate pagination info
    total_pages = math.ceil(total_count / page_size)
    
    return DefectListResponse(
        items=[DefectResponse.from_orm(defect) for defect in defects],
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{defect_id}", response_model=DefectResponse)
async def get_defect(defect_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific defect by ID"""
    result = await db.execute(
        select(Defect).where(Defect.defect_id == defect_id)
    )
    defect = result.scalar_one_or_none()
    
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    return DefectResponse.from_orm(defect)
