#!/usr/bin/env python3
"""
Synthetic Data Generation Script for WaferMaps
Generates realistic semiconductor fab defect data for demonstration
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import User, Wafer, Equipment, DefectType, Inspection, Defect
from app.core.auth import AuthService

# SEMI T7 compliant wafer ID patterns
WAFER_ID_PATTERNS = [
    "W{year}{month:02d}{day:02d}{lot:03d}{wafer:02d}",
    "WF{year}{month:02d}{lot:04d}{wafer:03d}",
    "WAFER{year}{month:02d}{day:02d}{lot:05d}{wafer:02d}"
]

# Equipment types and models
EQUIPMENT_DATA = [
    {"type": "inspection", "name": "KLA-Tencor 2800", "model": "2800", "manufacturer": "KLA Corporation"},
    {"type": "inspection", "name": "KLA-Tencor 3900", "model": "3900", "manufacturer": "KLA Corporation"},
    {"type": "inspection", "name": "Applied Materials SEMVision", "model": "SEMVision", "manufacturer": "Applied Materials"},
    {"type": "metrology", "name": "Nova Measuring Instruments", "model": "Nova", "manufacturer": "Nova Measuring Instruments"},
    {"type": "inspection", "name": "Hitachi High-Tech", "model": "CG4000", "manufacturer": "Hitachi High-Tech"}
]

# Defect types with realistic categories
DEFECT_TYPES = [
    {"name": "particle", "category": "contamination", "severity": 3, "color": "#ff0000"},
    {"name": "scratch", "category": "mechanical", "severity": 4, "color": "#00ff00"},
    {"name": "contamination", "category": "contamination", "severity": 5, "color": "#0000ff"},
    {"name": "crystal_defect", "category": "material", "severity": 4, "color": "#ffff00"},
    {"name": "void", "category": "material", "severity": 3, "color": "#ff00ff"},
    {"name": "residue", "category": "contamination", "severity": 2, "color": "#00ffff"},
    {"name": "crack", "category": "mechanical", "severity": 5, "color": "#ff8800"},
    {"name": "dislocation", "category": "material", "severity": 4, "color": "#8800ff"},
    {"name": "stacking_fault", "category": "material", "severity": 3, "color": "#ff0088"},
    {"name": "oxide_defect", "category": "process", "severity": 3, "color": "#88ff00"}
]

async def generate_users(db: AsyncSession) -> List[User]:
    """Generate synthetic users"""
    users_data = [
        {"username": "admin", "email": "admin@wafermaps.com", "role": "admin", "department": "IT"},
        {"username": "engineer1", "email": "engineer1@wafermaps.com", "role": "engineer", "department": "Process Engineering"},
        {"username": "engineer2", "email": "engineer2@wafermaps.com", "role": "engineer", "department": "Quality Assurance"},
        {"username": "operator1", "email": "operator1@wafermaps.com", "role": "operator", "department": "Manufacturing"},
        {"username": "operator2", "email": "operator2@wafermaps.com", "role": "operator", "department": "Manufacturing"},
        {"username": "viewer1", "email": "viewer1@wafermaps.com", "role": "viewer", "department": "Management"}
    ]
    
    auth_service = AuthService()
    users = []
    
    for user_data in users_data:
        # Check if user already exists
        existing = await db.execute(select(User).where(User.username == user_data["username"]))
        if existing.scalar_one_or_none():
            continue
            
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password_hash=auth_service.get_password_hash("password123"),
            role=user_data["role"],
            department=user_data["department"]
        )
        db.add(user)
        users.append(user)
    
    await db.commit()
    print(f"Generated {len(users)} users")
    return users

async def generate_equipment(db: AsyncSession) -> List[Equipment]:
    """Generate synthetic equipment"""
    equipment = []
    
    for i, eq_data in enumerate(EQUIPMENT_DATA):
        equipment_id = f"EQ{i+1:03d}"
        
        # Check if equipment already exists
        existing = await db.execute(select(Equipment).where(Equipment.equipment_id == equipment_id))
        if existing.scalar_one_or_none():
            continue
            
        eq = Equipment(
            equipment_id=equipment_id,
            equipment_name=eq_data["name"],
            equipment_type=eq_data["type"],
            model=eq_data["model"],
            manufacturer=eq_data["manufacturer"],
            location=f"Fab-{random.randint(1,3)}-Area-{random.randint(1,5)}",
            status="active",
            serial_number=f"SN{random.randint(100000, 999999)}",
            software_version=f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
            hardware_version=f"{random.randint(1,3)}.{random.randint(0,9)}"
        )
        db.add(eq)
        equipment.append(eq)
    
    await db.commit()
    print(f"Generated {len(equipment)} equipment")
    return equipment

async def generate_defect_types(db: AsyncSession) -> List[DefectType]:
    """Generate synthetic defect types"""
    defect_types = []
    
    for dt_data in DEFECT_TYPES:
        # Check if defect type already exists
        existing = await db.execute(select(DefectType).where(DefectType.defect_type_name == dt_data["name"]))
        if existing.scalar_one_or_none():
            continue
            
        dt = DefectType(
            defect_type_name=dt_data["name"],
            description=f"{dt_data['name'].replace('_', ' ').title()} defect",
            severity_level=dt_data["severity"],
            category=dt_data["category"],
            color_code=dt_data["color"],
            detection_methods=["optical", "SEM"],
            typical_causes=["process variation", "equipment malfunction"],
            prevention_methods=["process optimization", "equipment maintenance"]
        )
        db.add(dt)
        defect_types.append(dt)
    
    await db.commit()
    print(f"Generated {len(defect_types)} defect types")
    return defect_types

async def generate_wafers(db: AsyncSession, count: int = 1000) -> List[Wafer]:
    """Generate synthetic wafers with SEMI T7 compliant IDs"""
    wafers = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(count):
        # Generate SEMI T7 compliant wafer ID
        creation_date = start_date + timedelta(days=random.randint(0, 365))
        year = creation_date.year % 100
        month = creation_date.month
        day = creation_date.day
        lot = random.randint(1, 999)
        wafer_num = random.randint(1, 99)
        
        pattern = random.choice(WAFER_ID_PATTERNS)
        wafer_id = pattern.format(
            year=year, month=month, day=day, lot=lot, wafer=wafer_num
        )
        
        # Check if wafer already exists
        existing = await db.execute(select(Wafer).where(Wafer.wafer_id == wafer_id))
        if existing.scalar_one_or_none():
            continue
            
        wafer = Wafer(
            wafer_id=wafer_id,
            wafer_type=random.choice(["200mm", "300mm"]),
            creation_date=creation_date,
            status=random.choice(["active", "active", "active", "inactive", "scrapped"]),
            lot_id=f"LOT{lot:06d}",
            process_node=random.choice(["90nm", "65nm", "45nm", "32nm", "28nm", "22nm", "14nm", "10nm", "7nm"]),
            manufacturer=random.choice(["TSMC", "Intel", "Samsung", "GlobalFoundries", "UMC"]),
            material="silicon",
            orientation="100",
            resistivity="1-10 ohm-cm",
            thickness="725 um" if random.choice(["200mm", "300mm"]) == "200mm" else "775 um",
            diameter="200mm" if random.choice(["200mm", "300mm"]) == "200mm" else "300mm"
        )
        db.add(wafer)
        wafers.append(wafer)
    
    await db.commit()
    print(f"Generated {len(wafers)} wafers")
    return wafers

async def generate_inspections_and_defects(db: AsyncSession, wafers: List[Wafer], equipment: List[Equipment], defect_types: List[DefectType]):
    """Generate synthetic inspections and defects"""
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
    """Main function to generate all synthetic data"""
    print("Starting synthetic data generation...")
    
    async with AsyncSessionLocal() as db:
        # Generate users
        users = await generate_users(db)
        
        # Generate equipment
        equipment = await generate_equipment(db)
        
        # Generate defect types
        defect_types = await generate_defect_types(db)
        
        # Generate wafers
        wafers = await generate_wafers(db, count=1000)
        
        # Generate inspections and defects
        await generate_inspections_and_defects(db, wafers, equipment, defect_types)
    
    print("Synthetic data generation completed!")

if __name__ == "__main__":
    import math
    asyncio.run(main())
