from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WaferBase(BaseModel):
    wafer_id: str = Field(..., description="SEMI T7 compliant wafer ID")
    diameter: str = Field(..., description="Wafer diameter (e.g., '300mm')")
    thickness: Optional[str] = Field(None, description="Wafer thickness (e.g., '725 um')")
    material: str = Field(..., description="Wafer material (e.g., Silicon)")
    orientation: Optional[str] = Field(None, description="Crystal orientation")
    resistivity: Optional[str] = Field(None, description="Resistivity (e.g., '1-10 ohm-cm')")
    dopant_type: Optional[str] = Field(None, description="Dopant type (P, N, etc.)")
    dopant_concentration: Optional[str] = Field(None, description="Dopant concentration")

class WaferResponse(WaferBase):
    wafer_id: str
    creation_date: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WaferListResponse(BaseModel):
    items: List[WaferResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
