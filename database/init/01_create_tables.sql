-- Create database schema for WaferMaps
-- This script creates all tables and indexes for the semiconductor fab defect data system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create wafers table
CREATE TABLE IF NOT EXISTS wafers (
    wafer_id VARCHAR(50) PRIMARY KEY,
    wafer_type VARCHAR(20) NOT NULL,
    creation_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    lot_id VARCHAR(50),
    process_node VARCHAR(20),
    manufacturer VARCHAR(100),
    material VARCHAR(50),
    orientation VARCHAR(20),
    resistivity VARCHAR(50),
    thickness VARCHAR(20),
    diameter VARCHAR(20),
    flat_length VARCHAR(20),
    additional_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create equipment table
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    calibration_date TIMESTAMP,
    next_calibration_date TIMESTAMP,
    serial_number VARCHAR(100),
    software_version VARCHAR(50),
    hardware_version VARCHAR(50),
    specifications JSONB,
    settings JSONB,
    maintenance_history JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create defect_types table
CREATE TABLE IF NOT EXISTS defect_types (
    defect_type_id SERIAL PRIMARY KEY,
    defect_type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    severity_level INTEGER,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    color_code VARCHAR(7),
    detection_methods JSONB,
    typical_causes JSONB,
    prevention_methods JSONB,
    analysis_requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create inspections table
CREATE TABLE IF NOT EXISTS inspections (
    inspection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wafer_id VARCHAR(50) NOT NULL REFERENCES wafers(wafer_id),
    equipment_id VARCHAR(50) NOT NULL REFERENCES equipment(equipment_id),
    run_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    defect_count INTEGER NOT NULL DEFAULT 0,
    inspection_parameters JSONB,
    equipment_settings JSONB,
    operator_id VARCHAR(50),
    inspection_type VARCHAR(50),
    inspection_mode VARCHAR(50),
    sensitivity VARCHAR(50),
    scan_speed VARCHAR(50),
    resolution VARCHAR(50),
    coverage VARCHAR(50),
    results_summary JSONB,
    quality_metrics JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create defects table
CREATE TABLE IF NOT EXISTS defects (
    defect_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_id UUID NOT NULL REFERENCES inspections(inspection_id) ON DELETE CASCADE,
    x_coordinate DECIMAL(10,6) NOT NULL,
    y_coordinate DECIMAL(10,6) NOT NULL,
    defect_type VARCHAR(50) NOT NULL,
    defect_size DECIMAL(10,6),
    defect_classification VARCHAR(50),
    confidence_score DECIMAL(3,2),
    sem_image_url VARCHAR(500),
    edx_spectra_url VARCHAR(500),
    defect_parameters JSONB,
    severity_level VARCHAR(20),
    defect_category VARCHAR(50),
    defect_subcategory VARCHAR(50),
    detection_method VARCHAR(50),
    analysis_status VARCHAR(20) DEFAULT 'detected',
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_wafers_lot_id ON wafers(lot_id);
CREATE INDEX IF NOT EXISTS idx_wafers_creation_date ON wafers(creation_date);
CREATE INDEX IF NOT EXISTS idx_wafers_status ON wafers(status);
CREATE INDEX IF NOT EXISTS idx_wafers_type ON wafers(wafer_type);

CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

CREATE INDEX IF NOT EXISTS idx_defect_types_name ON defect_types(defect_type_name);
CREATE INDEX IF NOT EXISTS idx_defect_types_category ON defect_types(category);
CREATE INDEX IF NOT EXISTS idx_defect_types_severity ON defect_types(severity_level);

CREATE INDEX IF NOT EXISTS idx_inspections_wafer_id ON inspections(wafer_id);
CREATE INDEX IF NOT EXISTS idx_inspections_equipment_id ON inspections(equipment_id);
CREATE INDEX IF NOT EXISTS idx_inspections_run_id ON inspections(run_id);
CREATE INDEX IF NOT EXISTS idx_inspections_timestamp ON inspections(timestamp);
CREATE INDEX IF NOT EXISTS idx_inspections_wafer_timestamp ON inspections(wafer_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_defects_inspection_id ON defects(inspection_id);
CREATE INDEX IF NOT EXISTS idx_defects_type ON defects(defect_type);
CREATE INDEX IF NOT EXISTS idx_defects_coordinates ON defects(x_coordinate, y_coordinate);
CREATE INDEX IF NOT EXISTS idx_defects_classification ON defects(defect_classification);
CREATE INDEX IF NOT EXISTS idx_defects_confidence ON defects(confidence_score);
CREATE INDEX IF NOT EXISTS idx_defects_severity ON defects(severity_level);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_defects_type_timestamp ON defects(defect_type, created_at);
CREATE INDEX IF NOT EXISTS idx_inspections_equipment_timestamp ON inspections(equipment_id, timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_wafers_updated_at BEFORE UPDATE ON wafers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_defect_types_updated_at BEFORE UPDATE ON defect_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inspections_updated_at BEFORE UPDATE ON inspections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_defects_updated_at BEFORE UPDATE ON defects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
