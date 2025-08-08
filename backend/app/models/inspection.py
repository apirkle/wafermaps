from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Inspection(Base):
    __tablename__ = "inspections"
    
    inspection_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wafer_id = Column(String(50), ForeignKey("wafers.wafer_id"), nullable=False, index=True)
    equipment_id = Column(String(50), ForeignKey("equipment.equipment_id"), nullable=False, index=True)
    run_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    defect_count = Column(Integer, nullable=False, default=0)
    inspection_parameters = Column(JSONB)  # inspection parameters
    equipment_settings = Column(JSONB)  # equipment configuration
    operator_id = Column(String(50))  # operator performing inspection
    inspection_type = Column(String(50))  # type of inspection
    inspection_mode = Column(String(50))  # inspection mode
    sensitivity = Column(String(50))  # detection sensitivity
    scan_speed = Column(String(50))  # scan speed
    resolution = Column(String(50))  # inspection resolution
    coverage = Column(String(50))  # inspection coverage
    results_summary = Column(JSONB)  # inspection results summary
    quality_metrics = Column(JSONB)  # quality metrics
    notes = Column(Text)  # operator notes
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    wafer = relationship("Wafer", backref="inspections")
    equipment = relationship("Equipment", backref="inspections")
    defects = relationship("Defect", back_populates="inspection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Inspection(inspection_id={self.inspection_id}, wafer_id='{self.wafer_id}', equipment_id='{self.equipment_id}')>"
    
    @property
    def has_defects(self) -> bool:
        return self.defect_count > 0
    
    @property
    def is_recent(self) -> bool:
        """Check if inspection was performed in the last 24 hours"""
        return (datetime.utcnow() - self.timestamp).days < 1
