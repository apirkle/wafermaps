from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.sql import text
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.wafer import Wafer
from app.models.inspection import Inspection
from app.models.defect import Defect
from app.models.defect_type import DefectType
from app.models.equipment import Equipment

router = APIRouter()

@router.get("/")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get general analytics summary"""
    
    # Total counts
    wafer_count = await db.execute(select(func.count(Wafer.wafer_id)))
    inspection_count = await db.execute(select(func.count(Inspection.inspection_id)))
    defect_count = await db.execute(select(func.count(Defect.defect_id)))
    equipment_count = await db.execute(select(func.count(Equipment.equipment_id)))
    
    # Calculate defect rate
    total_inspections = inspection_count.scalar() or 0
    total_defects = defect_count.scalar() or 0
    defect_rate = (total_defects / total_inspections * 100) if total_inspections > 0 else 0
    
    # Calculate inspection completion rate (simplified)
    inspection_completion_rate = 95.0  # Placeholder - would need more complex logic
    
    # Get defects by type
    defect_type_result = await db.execute(
        select(Defect.defect_type, func.count(Defect.defect_id))
        .group_by(Defect.defect_type)
    )
    defects_by_type = {row[0]: row[1] for row in defect_type_result}
    
    # Get defects by severity
    defect_severity_result = await db.execute(
        select(Defect.severity_level, func.count(Defect.defect_id))
        .group_by(Defect.severity_level)
    )
    defects_by_severity = {row[0]: row[1] for row in defect_severity_result if row[0]}
    
    return {
        "total_wafers": wafer_count.scalar() or 0,
        "total_inspections": total_inspections,
        "total_defects": total_defects,
        "defect_rate": round(defect_rate, 2),
        "inspection_completion_rate": inspection_completion_rate,
        "defects_by_type": defects_by_type,
        "defects_by_severity": defects_by_severity
    }

@router.get("/dashboard-stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Total counts
    wafer_count = await db.execute(select(func.count(Wafer.wafer_id)))
    inspection_count = await db.execute(select(func.count(Inspection.inspection_id)))
    defect_count = await db.execute(select(func.count(Defect.defect_id)))
    equipment_count = await db.execute(select(func.count(Equipment.equipment_id)))
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_inspections = await db.execute(
        select(func.count(Inspection.inspection_id)).where(Inspection.inspection_date >= week_ago)
    )
    recent_defects = await db.execute(
        select(func.count(Defect.defect_id)).where(Defect.created_at >= week_ago)
    )
    
    # Average defects per inspection
    avg_defects = await db.execute(
        select(func.avg(Inspection.defect_count))
    )
    
    return {
        "total_wafers": wafer_count.scalar(),
        "total_inspections": inspection_count.scalar(),
        "total_defects": defect_count.scalar(),
        "total_equipment": equipment_count.scalar(),
        "recent_inspections": recent_inspections.scalar(),
        "recent_defects": recent_defects.scalar(),
        "avg_defects_per_inspection": float(avg_defects.scalar() or 0)
    }

@router.get("/defect-trends")
async def get_defect_trends(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get defect count trends over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily defect counts
    result = await db.execute(text("""
        SELECT 
            DATE(inspection_date) as date,
            COUNT(*) as inspection_count,
            SUM(defect_count) as total_defects,
            AVG(defect_count) as avg_defects
        FROM inspections 
        WHERE inspection_date >= :start_date
        GROUP BY DATE(inspection_date)
        ORDER BY date
    """), {"start_date": start_date})
    
    trends = []
    for row in result:
        trends.append({
            "date": row.date.isoformat(),
            "inspection_count": row.inspection_count,
            "total_defects": row.total_defects,
            "avg_defects": float(row.avg_defects or 0)
        })
    
    return {"trends": trends}

@router.get("/defect-pareto")
async def get_defect_pareto(db: AsyncSession = Depends(get_db)):
    """Get defect type Pareto chart data"""
    
    result = await db.execute(text("""
        SELECT 
            dt.defect_type_name,
            COUNT(d.defect_id) as defect_count,
            ROUND(COUNT(d.defect_id) * 100.0 / (SELECT COUNT(*) FROM defects), 2) as percentage
        FROM defects d
        JOIN defect_types dt ON d.defect_type_id = dt.defect_type_id
        GROUP BY dt.defect_type_id, dt.defect_type_name
        ORDER BY defect_count DESC
    """))
    
    pareto_data = []
    cumulative_percentage = 0
    
    for row in result:
        cumulative_percentage += row.percentage
        pareto_data.append({
            "defect_type": row.defect_type_name,
            "count": row.defect_count,
            "percentage": row.percentage,
            "cumulative_percentage": cumulative_percentage
        })
    
    return {"pareto_data": pareto_data}

@router.get("/equipment-stats")
async def get_equipment_stats(db: AsyncSession = Depends(get_db)):
    """Get equipment performance statistics"""
    
    result = await db.execute(text("""
        SELECT 
            e.equipment_id,
            e.equipment_name,
            e.equipment_type,
            COUNT(i.inspection_id) as inspection_count,
            SUM(i.defect_count) as total_defects,
            AVG(i.defect_count) as avg_defects_per_inspection,
            MAX(i.inspection_date) as last_inspection
        FROM equipment e
        LEFT JOIN inspections i ON e.equipment_id = i.equipment_id
        GROUP BY e.equipment_id, e.equipment_name, e.equipment_type
        ORDER BY inspection_count DESC
    """))
    
    equipment_stats = []
    for row in result:
        equipment_stats.append({
            "equipment_id": row.equipment_id,
            "equipment_name": row.equipment_name,
            "equipment_type": row.equipment_type,
            "inspection_count": row.inspection_count,
            "total_defects": row.total_defects or 0,
            "avg_defects_per_inspection": float(row.avg_defects_per_inspection or 0),
            "last_inspection": row.last_inspection.isoformat() if row.last_inspection else None
        })
    
    return {"equipment_stats": equipment_stats}
