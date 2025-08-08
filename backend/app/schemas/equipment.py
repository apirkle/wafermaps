from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EquipmentBase(BaseModel):
    equipment_id: str = Field(..., description="Equipment identifier")
    equipment_name: str = Field(..., description="Equipment name")
    equipment_type: str = Field(..., description="Type of equipment")
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    operator: Optional[str] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None

class EquipmentResponse(EquipmentBase):
    equipment_parameters: Optional[Dict[str, Any]] = None
    maintenance_history: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EquipmentListResponse(BaseModel):
    items: List[EquipmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
