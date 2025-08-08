from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import math

from app.core.database import get_db
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentResponse, EquipmentListResponse

router = APIRouter()

@router.get("/", response_model=EquipmentListResponse)
async def get_equipment(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of equipment with pagination and filtering"""
    
    # Build query
    query = select(Equipment)
    count_query = select(func.count(Equipment.equipment_id))
    
    # Apply filters
    if equipment_type:
        query = query.where(Equipment.equipment_type.contains(equipment_type))
        count_query = count_query.where(Equipment.equipment_type.contains(equipment_type))
    
    if status:
        query = query.where(Equipment.status.contains(status))
        count_query = count_query.where(Equipment.status.contains(status))
    
    # Get total count
    result = await db.execute(count_query)
    total_count = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Get equipment
    result = await db.execute(query)
    equipment_list = result.scalars().all()
    
    # Calculate pagination info
    total_pages = math.ceil(total_count / page_size)
    
    return EquipmentListResponse(
        items=[EquipmentResponse.from_orm(equipment) for equipment in equipment_list],
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment_by_id(equipment_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific equipment by ID"""
    result = await db.execute(select(Equipment).where(Equipment.equipment_id == equipment_id))
    equipment = result.scalar_one_or_none()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return EquipmentResponse.from_orm(equipment)
