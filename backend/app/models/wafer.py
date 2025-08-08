from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class Wafer(Base):
    __tablename__ = "wafers"
    
    wafer_id = Column(String(50), primary_key=True)  # SEMI T7 compliant ID
    wafer_type = Column(String(20), nullable=False)  # 200mm, 300mm, etc.
    creation_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, inactive, scrapped
    lot_id = Column(String(50), index=True)  # manufacturing lot
    process_node = Column(String(20))  # technology node
    manufacturer = Column(String(100))
    material = Column(String(50))  # silicon, gallium arsenide, etc.
    orientation = Column(String(20))  # crystal orientation
    resistivity = Column(String(50))  # resistivity range
    thickness = Column(String(20))  # wafer thickness
    diameter = Column(String(20))  # wafer diameter
    flat_length = Column(String(20))  # flat length
    additional_info = Column(JSONB)  # flexible additional data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Wafer(wafer_id='{self.wafer_id}', wafer_type='{self.wafer_type}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        return self.status == "active"
    
    @property
    def is_scrapped(self) -> bool:
        return self.status == "scrapped"
