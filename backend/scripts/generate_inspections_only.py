#!/usr/bin/env python3
"""
Script to generate synthetic inspections and defects for existing wafers
"""

import asyncio
import random
import math
from datetime import timedelta
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.wafer import Wafer
from app.models.equipment import Equipment
from app.models.defect_type import DefectType
from app.models.inspection import Inspection
from app.models.defect import Defect

async def generate_inspections_and_defects(db: AsyncSession):
    """Generate synthetic inspections and defects for existing data"""
    
    # Get existing data
    result = await db.execute(select(Wafer))
    wafers = result.scalars().all()
    
    result = await db.execute(select(Equipment))
    equipment = result.scalars().all()
    
    result = await db.execute(select(DefectType))
    defect_types = result.scalars().all()
    
    print(f"Found {len(wafers)} wafers, {len(equipment)} equipment, {len(defect_types)} defect types")
    
    if not wafers or not equipment or not defect_types:
        print("Missing required data. Please run the full synthetic data generation first.")
        return
    
    inspections = []
    defects = []
    
    # Get defect type names
    defect_type_names = [dt.defect_type_name for dt in defect_types]
    
    for wafer in wafers:
        # Generate 1-5 inspections per wafer
        num_inspections = random.randint(1, 5)
        
        for i in range(num_inspections):
            inspection_date = wafer.creation_date + timedelta(days=random.randint(1, 30))
            equipment_id = random.choice(equipment).equipment_id
            
            # Generate defect count (0-50 defects per inspection)
            defect_count = random.randint(0, 50)
            
            inspection = Inspection(
                wafer_id=wafer.wafer_id,
                equipment_id=equipment_id,
                run_id=f"RUN{random.randint(100000, 999999)}",
                timestamp=inspection_date,
                defect_count=defect_count,
                inspection_type=random.choice(["optical", "SEM", "metrology"]),
                inspection_mode=random.choice(["bright_field", "dark_field", "confocal"]),
                sensitivity=random.choice(["high", "medium", "low"]),
                scan_speed=f"{random.randint(10, 100)} mm/s",
                resolution=f"{random.randint(1, 10)} um"
            )
            db.add(inspection)
            await db.flush()  # Flush to get the inspection_id
            
            inspections.append(inspection)
            
            # Generate defects for this inspection
            for j in range(defect_count):
                # Generate coordinates within wafer radius
                radius = 100 if wafer.wafer_type == "200mm" else 150
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(0, radius)
                x_coord = distance * math.cos(angle)
                y_coord = distance * math.sin(angle)
                
                defect = Defect(
                    inspection_id=inspection.inspection_id,  # Now this will have a valid ID
                    x_coordinate=Decimal(str(round(x_coord, 6))),
                    y_coordinate=Decimal(str(round(y_coord, 6))),
                    defect_type=random.choice(defect_type_names),
                    defect_size=Decimal(str(round(random.uniform(0.1, 10.0), 6))),
                    defect_classification=random.choice(["critical", "major", "minor"]),
                    confidence_score=Decimal(str(round(random.uniform(0.7, 1.0), 2))),
                    severity_level=random.choice(["low", "medium", "high", "critical"]),
                    detection_method=random.choice(["optical", "SEM", "metrology"])
                )
                db.add(defect)
                defects.append(defect)
    
    await db.commit()
    print(f"Generated {len(inspections)} inspections and {len(defects)} defects")

async def main():
    """Main function to generate inspections and defects"""
    print("Starting inspection and defect generation...")
    
    async with AsyncSessionLocal() as db:
        await generate_inspections_and_defects(db)
    
    print("Inspection and defect generation completed!")

if __name__ == "__main__":
    asyncio.run(main())
