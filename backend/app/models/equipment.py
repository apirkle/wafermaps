from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    
    equipment_id = Column(String(50), primary_key=True)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)  # inspection, metrology, etc.
    model = Column(String(100))
    manufacturer = Column(String(100))
    location = Column(String(100))
    status = Column(String(20), nullable=False, default="active")  # active, maintenance, offline
    calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    serial_number = Column(String(100))
    software_version = Column(String(50))
    hardware_version = Column(String(50))
    specifications = Column(JSONB)  # equipment specifications
    settings = Column(JSONB)  # current equipment settings
    maintenance_history = Column(JSONB)  # maintenance records
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', name='{self.equipment_name}', type='{self.equipment_type}')>"
    
    @property
    def is_active(self) -> bool:
        return self.status == "active"
    
    @property
    def needs_calibration(self) -> bool:
        if not self.next_calibration_date:
            return False
        return datetime.utcnow() > self.next_calibration_date
