from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class DefectBase(BaseModel):
    x_coordinate: Decimal = Field(..., description="X coordinate on wafer")
    y_coordinate: Decimal = Field(..., description="Y coordinate on wafer")
    defect_type: str = Field(..., description="Type of defect")
    defect_size: Optional[Decimal] = Field(None, description="Defect size in microns")
    defect_classification: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    severity_level: Optional[str] = None
    defect_category: Optional[str] = None
    defect_subcategory: Optional[str] = None
    detection_method: Optional[str] = None
    analysis_status: Optional[str] = None
    sem_image_url: Optional[str] = None
    edx_spectra_url: Optional[str] = None
    review_notes: Optional[str] = None

class DefectResponse(DefectBase):
    defect_id: UUID
    inspection_id: UUID
    defect_parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DefectListResponse(BaseModel):
    items: List[DefectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
