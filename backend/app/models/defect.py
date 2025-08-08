from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Defect(Base):
    __tablename__ = "defects"
    
    defect_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(PostgresUUID(as_uuid=True), ForeignKey("inspections.inspection_id"), nullable=False, index=True)
    x_coordinate = Column(Numeric(10, 6), nullable=False)  # X coordinate on wafer in mm
    y_coordinate = Column(Numeric(10, 6), nullable=False)  # Y coordinate on wafer in mm
    defect_type = Column(String(50), nullable=False, index=True)
    defect_size = Column(Numeric(10, 6))  # Size in micrometers
    defect_classification = Column(String(50), index=True)  # Classification category
    confidence_score = Column(Numeric(3, 2))  # Detection confidence (0-1)
    sem_image_url = Column(String(500))  # Optional SEM image URL
    edx_spectra_url = Column(String(500))  # Optional EDX spectra URL
    defect_parameters = Column(JSONB)  # Additional defect metadata
    severity_level = Column(String(20))  # severity level
    defect_category = Column(String(50))  # defect category
    defect_subcategory = Column(String(50))  # defect subcategory
    detection_method = Column(String(50))  # detection method
    analysis_status = Column(String(20), default="detected")  # detected, analyzed, reviewed
    review_notes = Column(Text)  # review notes
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    inspection = relationship("Inspection", back_populates="defects")
    
    def __repr__(self):
        return f"<Defect(defect_id={self.defect_id}, type='{self.defect_type}', coordinates=({self.x_coordinate}, {self.y_coordinate}))>"
    
    @property
    def has_sem_image(self) -> bool:
        return bool(self.sem_image_url)
    
    @property
    def has_edx_spectra(self) -> bool:
        return bool(self.edx_spectra_url)
    
    @property
    def is_analyzed(self) -> bool:
        return self.analysis_status in ["analyzed", "reviewed"]
    
    @property
    def is_critical(self) -> bool:
        return self.severity_level == "critical"
    
    def get_distance_from_center(self) -> float:
        """Calculate distance from wafer center"""
        import math
        return math.sqrt(self.x_coordinate**2 + self.y_coordinate**2)
