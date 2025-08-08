from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class InspectionBase(BaseModel):
    run_id: str
    timestamp: datetime
    defect_count: int
    inspection_type: Optional[str] = None
    inspection_mode: Optional[str] = None
    operator_id: Optional[str] = None
    notes: Optional[str] = None

class InspectionResponse(InspectionBase):
    inspection_id: UUID
    wafer_id: str
    equipment_id: str
    inspection_parameters: Optional[Dict[str, Any]] = None
    equipment_settings: Optional[Dict[str, Any]] = None
    sensitivity: Optional[str] = None
    scan_speed: Optional[str] = None
    resolution: Optional[str] = None
    coverage: Optional[str] = None
    results_summary: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InspectionListResponse(BaseModel):
    items: List[InspectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
