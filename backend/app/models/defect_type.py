from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class DefectType(Base):
    __tablename__ = "defect_types"
    
    defect_type_id = Column(Integer, primary_key=True, autoincrement=True)
    defect_type_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    severity_level = Column(Integer)  # 1-5 scale (1=low, 5=critical)
    category = Column(String(50))  # particle, scratch, contamination, etc.
    subcategory = Column(String(50))  # subcategory within main category
    is_active = Column(Boolean, default=True)
    color_code = Column(String(7))  # hex color code for visualization
    detection_methods = Column(JSONB)  # applicable detection methods
    typical_causes = Column(JSONB)  # typical causes of this defect type
    prevention_methods = Column(JSONB)  # prevention methods
    analysis_requirements = Column(JSONB)  # analysis requirements
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DefectType(defect_type_id={self.defect_type_id}, name='{self.defect_type_name}', severity={self.severity_level})>"
    
    @property
    def is_critical(self) -> bool:
        return self.severity_level >= 4
    
    @property
    def is_high_severity(self) -> bool:
        return self.severity_level >= 3
