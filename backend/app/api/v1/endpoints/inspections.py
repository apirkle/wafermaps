from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from typing import List, Optional
import math

from app.core.database import get_db
from app.models.inspection import Inspection
from app.models.wafer import Wafer
from app.models.equipment import Equipment
from app.schemas.inspection import InspectionResponse, InspectionListResponse

router = APIRouter()

@router.get("/", response_model=InspectionListResponse)
async def get_inspections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    wafer_id: Optional[str] = Query(None, description="Filter by wafer ID"),
    equipment_id: Optional[str] = Query(None, description="Filter by equipment ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of inspections with pagination and filtering"""
    
    # Build query
    query = select(Inspection)
    count_query = select(func.count(Inspection.inspection_id))
    
    # Apply filters
    if wafer_id:
        query = query.where(Inspection.wafer_id.contains(wafer_id))
        count_query = count_query.where(Inspection.wafer_id.contains(wafer_id))
    
    if equipment_id:
        query = query.where(Inspection.equipment_id.contains(equipment_id))
        count_query = count_query.where(Inspection.equipment_id.contains(equipment_id))
    
    # Get total count
    result = await db.execute(count_query)
    total_count = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Get inspections
    result = await db.execute(query)
    inspections = result.scalars().all()
    
    # Calculate pagination info
    total_pages = math.ceil(total_count / page_size)
    
    return InspectionListResponse(
        items=[InspectionResponse.from_orm(inspection) for inspection in inspections],
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(inspection_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific inspection by ID"""
    result = await db.execute(
        select(Inspection).where(Inspection.inspection_id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return InspectionResponse.from_orm(inspection)
