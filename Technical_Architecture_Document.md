# Technical Architecture Document
## Semiconductor Fab Defect Data Exploration System

### 1. System Overview

#### 1.1 Architecture Principles
- **Microservices Architecture:** Modular, scalable service design
- **API-First Design:** RESTful APIs as the primary integration mechanism
- **Containerization:** Docker-based deployment for consistency and portability
- **Event-Driven:** Asynchronous processing for real-time data handling
- **Security by Design:** Security considerations integrated at every layer

#### 1.2 High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   (React)       │◄──►│   (Nginx)       │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐            │
                       │   Cache Layer   │            │
                       │   (Redis)       │◄───────────┤
                       └─────────────────┘            │
                                                       │
                       ┌─────────────────┐            │
                       │   Database      │            │
                       │   (PostgreSQL)  │◄───────────┘
                       └─────────────────┘
                                                       │
                       ┌─────────────────┐            │
                       │   File Storage  │            │
                       │   (S3/MinIO)    │◄───────────┘
                       └─────────────────┘
```

### 2. Database Design

#### 2.1 Core Schema Design

##### 2.1.1 Wafer Table
```sql
CREATE TABLE wafers (
    wafer_id VARCHAR(50) PRIMARY KEY,  -- SEMI T7 compliant ID
    wafer_type VARCHAR(20) NOT NULL,   -- 200mm, 300mm, etc.
    creation_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,       -- active, inactive, scrapped
    lot_id VARCHAR(50),                -- manufacturing lot
    process_node VARCHAR(20),          -- technology node
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_wafers_lot_id ON wafers(lot_id);
CREATE INDEX idx_wafers_creation_date ON wafers(creation_date);
CREATE INDEX idx_wafers_status ON wafers(status);
```

##### 2.1.2 Inspection Table
```sql
CREATE TABLE inspections (
    inspection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wafer_id VARCHAR(50) NOT NULL REFERENCES wafers(wafer_id),
    equipment_id VARCHAR(50) NOT NULL,
    run_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    defect_count INTEGER NOT NULL DEFAULT 0,
    inspection_parameters JSONB,       -- Flexible parameter storage
    equipment_settings JSONB,          -- Equipment configuration
    operator_id VARCHAR(50),           -- Operator performing inspection
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_inspections_wafer_id ON inspections(wafer_id);
CREATE INDEX idx_inspections_equipment_id ON inspections(equipment_id);
CREATE INDEX idx_inspections_run_id ON inspections(run_id);
CREATE INDEX idx_inspections_timestamp ON inspections(timestamp);
CREATE INDEX idx_inspections_wafer_timestamp ON inspections(wafer_id, timestamp);
```

##### 2.1.3 Defect Table
```sql
CREATE TABLE defects (
    defect_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id UUID NOT NULL REFERENCES inspections(inspection_id),
    x_coordinate DECIMAL(10,6) NOT NULL,  -- X coordinate on wafer
    y_coordinate DECIMAL(10,6) NOT NULL,  -- Y coordinate on wafer
    defect_type VARCHAR(50) NOT NULL,
    defect_size DECIMAL(10,6),            -- Size in micrometers
    defect_classification VARCHAR(50),    -- Classification category
    confidence_score DECIMAL(3,2),        -- Detection confidence (0-1)
    sem_image_url VARCHAR(500),           -- Optional SEM image URL
    edx_spectra_url VARCHAR(500),         -- Optional EDX spectra URL
    defect_parameters JSONB,              -- Additional defect metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_defects_inspection_id ON defects(inspection_id);
CREATE INDEX idx_defects_type ON defects(defect_type);
CREATE INDEX idx_defects_coordinates ON defects(x_coordinate, y_coordinate);
CREATE INDEX idx_defects_classification ON defects(defect_classification);
CREATE INDEX idx_defects_confidence ON defects(confidence_score);
```

##### 2.1.4 Equipment Table
```sql
CREATE TABLE equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,  -- inspection, metrology, etc.
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20) NOT NULL,          -- active, maintenance, offline
    calibration_date TIMESTAMP,
    next_calibration_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(status);
```

##### 2.1.5 Users Table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,            -- admin, engineer, operator, viewer
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### 2.2 Data Relationships
```sql
-- Foreign key constraints
ALTER TABLE inspections 
ADD CONSTRAINT fk_inspections_wafer 
FOREIGN KEY (wafer_id) REFERENCES wafers(wafer_id);

ALTER TABLE defects 
ADD CONSTRAINT fk_defects_inspection 
FOREIGN KEY (inspection_id) REFERENCES inspections(inspection_id);

-- Many-to-many relationship for defect types (if needed)
CREATE TABLE defect_types (
    defect_type_id SERIAL PRIMARY KEY,
    defect_type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    severity_level INTEGER,  -- 1-5 scale
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. API Design

#### 3.1 RESTful API Endpoints

##### 3.1.1 Wafer Management
```
GET    /api/v1/wafers                    # List wafers with filtering
GET    /api/v1/wafers/{wafer_id}         # Get specific wafer
POST   /api/v1/wafers                    # Create new wafer
PUT    /api/v1/wafers/{wafer_id}         # Update wafer
DELETE /api/v1/wafers/{wafer_id}         # Delete wafer
GET    /api/v1/wafers/{wafer_id}/history # Get wafer inspection history
```

##### 3.1.2 Inspection Management
```
GET    /api/v1/inspections               # List inspections with filtering
GET    /api/v1/inspections/{inspection_id} # Get specific inspection
POST   /api/v1/inspections               # Create new inspection
PUT    /api/v1/inspections/{inspection_id} # Update inspection
DELETE /api/v1/inspections/{inspection_id} # Delete inspection
GET    /api/v1/inspections/{inspection_id}/defects # Get inspection defects
```

##### 3.1.3 Defect Management
```
GET    /api/v1/defects                   # List defects with filtering
GET    /api/v1/defects/{defect_id}       # Get specific defect
POST   /api/v1/defects                   # Create new defect
PUT    /api/v1/defects/{defect_id}       # Update defect
DELETE /api/v1/defects/{defect_id}       # Delete defect
GET    /api/v1/defects/{defect_id}/sem   # Get SEM image
GET    /api/v1/defects/{defect_id}/edx   # Get EDX spectra
```

##### 3.1.4 Analytics Endpoints
```
GET    /api/v1/analytics/trends          # Get defect count trends
GET    /api/v1/analytics/pareto          # Get pareto analysis
GET    /api/v1/analytics/spc             # Get SPC control limits
GET    /api/v1/analytics/wafer-map/{wafer_id} # Get wafer map data
GET    /api/v1/analytics/correlation     # Get defect type correlations
```

##### 3.1.5 Equipment Management
```
GET    /api/v1/equipment                 # List equipment
GET    /api/v1/equipment/{equipment_id}  # Get specific equipment
POST   /api/v1/equipment                 # Create new equipment
PUT    /api/v1/equipment/{equipment_id}  # Update equipment
DELETE /api/v1/equipment/{equipment_id}  # Delete equipment
GET    /api/v1/equipment/{equipment_id}/performance # Get performance metrics
```

#### 3.2 API Response Formats

##### 3.2.1 Standard Response Structure
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2024-12-01T10:00:00Z",
    "version": "1.0"
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

##### 3.2.2 Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid wafer ID format",
    "details": {
      "field": "wafer_id",
      "value": "invalid_id",
      "constraint": "SEMI T7 format required"
    }
  },
  "meta": {
    "timestamp": "2024-12-01T10:00:00Z",
    "version": "1.0"
  }
}
```

### 4. Frontend Architecture

#### 4.1 Component Structure
```
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   ├── dashboard/
│   │   ├── Dashboard.tsx
│   │   ├── KPICard.tsx
│   │   └── SummaryStats.tsx
│   ├── analytics/
│   │   ├── TrendChart.tsx
│   │   ├── ParetoChart.tsx
│   │   ├── SPCChart.tsx
│   │   └── CorrelationMatrix.tsx
│   ├── wafer-map/
│   │   ├── WaferMap.tsx
│   │   ├── DefectOverlay.tsx
│   │   └── WaferMapControls.tsx
│   └── data-management/
│       ├── WaferList.tsx
│       ├── InspectionList.tsx
│       └── DefectList.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Analytics.tsx
│   ├── WaferMap.tsx
│   ├── DataManagement.tsx
│   └── Settings.tsx
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── websocket.ts
├── store/
│   ├── index.ts
│   ├── slices/
│   │   ├── authSlice.ts
│   │   ├── waferSlice.ts
│   │   └── analyticsSlice.ts
│   └── middleware.ts
└── utils/
    ├── constants.ts
    ├── helpers.ts
    └── validators.ts
```

#### 4.2 State Management
```typescript
// Redux store structure
interface RootState {
  auth: {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
  };
  wafers: {
    items: Wafer[];
    selectedWafer: Wafer | null;
    loading: boolean;
    error: string | null;
  };
  inspections: {
    items: Inspection[];
    selectedInspection: Inspection | null;
    loading: boolean;
    error: string | null;
  };
  defects: {
    items: Defect[];
    selectedDefect: Defect | null;
    loading: boolean;
    error: string | null;
  };
  analytics: {
    trends: TrendData[];
    pareto: ParetoData[];
    spc: SPCData[];
    loading: boolean;
    error: string | null;
  };
}
```

### 5. Data Processing and Analytics

#### 5.1 Statistical Process Control (SPC)
```python
class SPCProcessor:
    def __init__(self, data: List[float], subgroup_size: int = 1):
        self.data = data
        self.subgroup_size = subgroup_size
    
    def calculate_control_limits(self) -> Dict[str, float]:
        """Calculate UCL, LCL, and CL for X-bar and R charts"""
        mean = np.mean(self.data)
        std = np.std(self.data, ddof=1)
        
        # X-bar chart limits
        ucl_xbar = mean + (3 * std / np.sqrt(self.subgroup_size))
        lcl_xbar = mean - (3 * std / np.sqrt(self.subgroup_size))
        cl_xbar = mean
        
        # R chart limits (if subgroup_size > 1)
        if self.subgroup_size > 1:
            ranges = self._calculate_ranges()
            r_mean = np.mean(ranges)
            ucl_r = r_mean * self._get_d4_factor(self.subgroup_size)
            lcl_r = r_mean * self._get_d3_factor(self.subgroup_size)
            cl_r = r_mean
        else:
            ucl_r = lcl_r = cl_r = None
        
        return {
            'xbar': {'ucl': ucl_xbar, 'lcl': lcl_xbar, 'cl': cl_xbar},
            'r': {'ucl': ucl_r, 'lcl': lcl_r, 'cl': cl_r}
        }
    
    def detect_out_of_control(self) -> List[int]:
        """Detect out-of-control points using Western Electric rules"""
        # Implementation of Western Electric rules
        pass
```

#### 5.2 Pareto Analysis
```python
class ParetoAnalyzer:
    def __init__(self, defect_data: List[Dict]):
        self.defect_data = defect_data
    
    def generate_pareto_data(self) -> Dict:
        """Generate Pareto chart data"""
        defect_counts = {}
        for defect in self.defect_data:
            defect_type = defect['defect_type']
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
        
        # Sort by count (descending)
        sorted_defects = sorted(defect_counts.items(), 
                              key=lambda x: x[1], reverse=True)
        
        # Calculate cumulative percentages
        total_defects = sum(defect_counts.values())
        cumulative_percentage = 0
        pareto_data = []
        
        for defect_type, count in sorted_defects:
            percentage = (count / total_defects) * 100
            cumulative_percentage += percentage
            pareto_data.append({
                'defect_type': defect_type,
                'count': count,
                'percentage': percentage,
                'cumulative_percentage': cumulative_percentage
            })
        
        return {
            'data': pareto_data,
            'total_defects': total_defects,
            'defect_types': len(defect_counts)
        }
```

#### 5.3 Trend Analysis
```python
class TrendAnalyzer:
    def __init__(self, time_series_data: List[Dict]):
        self.data = time_series_data
    
    def calculate_moving_average(self, window: int = 7) -> List[float]:
        """Calculate moving average for trend smoothing"""
        values = [d['value'] for d in self.data]
        return list(pd.Series(values).rolling(window=window).mean())
    
    def detect_trends(self) -> Dict:
        """Detect trend direction and strength"""
        values = [d['value'] for d in self.data]
        timestamps = [d['timestamp'] for d in self.data]
        
        # Linear regression for trend analysis
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Determine trend direction
        if slope > 0:
            trend_direction = "increasing"
        elif slope < 0:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        return {
            'slope': slope,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'trend_direction': trend_direction,
            'trend_strength': abs(r_value)
        }
```

### 6. Wafer Map Visualization

#### 6.1 Coordinate System
```typescript
interface WaferCoordinate {
  x: number;  // X coordinate in mm
  y: number;  // Y coordinate in mm
  radius: number;  // Distance from center in mm
  angle: number;   // Angle from center in radians
}

class WaferMapRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private waferDiameter: number;
  private centerX: number;
  private centerY: number;
  
  constructor(canvas: HTMLCanvasElement, waferDiameter: number = 300) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.waferDiameter = waferDiameter;
    this.centerX = canvas.width / 2;
    this.centerY = canvas.height / 2;
  }
  
  drawWaferOutline(): void {
    this.ctx.beginPath();
    this.ctx.arc(this.centerX, this.centerY, this.waferDiameter / 2, 0, 2 * Math.PI);
    this.ctx.strokeStyle = '#333';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
  }
  
  drawDefects(defects: Defect[]): void {
    defects.forEach(defect => {
      const screenX = this.centerX + defect.x_coordinate;
      const screenY = this.centerY + defect.y_coordinate;
      
      // Draw defect point
      this.ctx.beginPath();
      this.ctx.arc(screenX, screenY, 3, 0, 2 * Math.PI);
      this.ctx.fillStyle = this.getDefectColor(defect.defect_type);
      this.ctx.fill();
    });
  }
  
  private getDefectColor(defectType: string): string {
    // Color coding based on defect type
    const colorMap: Record<string, string> = {
      'particle': '#ff0000',
      'scratch': '#00ff00',
      'contamination': '#0000ff',
      'crystal': '#ffff00',
      'void': '#ff00ff'
    };
    return colorMap[defectType] || '#999999';
  }
}
```

### 7. Security Implementation

#### 7.1 Authentication Middleware
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return username
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth_service = AuthService(settings.SECRET_KEY)
    username = auth_service.verify_token(credentials.credentials)
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

#### 7.2 Role-Based Access Control
```python
from functools import wraps
from fastapi import HTTPException

def require_role(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role != required_role and current_user.role != 'admin':
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{required_role}' required"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@router.get("/api/v1/admin/users")
@require_role("admin")
async def get_all_users(current_user: User):
    # Only admins can access this endpoint
    return get_users()
```

### 8. Performance Optimization

#### 8.1 Database Optimization
```sql
-- Partitioning for large tables
CREATE TABLE defects_partitioned (
    LIKE defects INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create partitions by month
CREATE TABLE defects_2024_01 PARTITION OF defects_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for complex queries
CREATE MATERIALIZED VIEW defect_summary_daily AS
SELECT 
    DATE(timestamp) as date,
    defect_type,
    COUNT(*) as defect_count,
    AVG(defect_size) as avg_size
FROM defects d
JOIN inspections i ON d.inspection_id = i.inspection_id
GROUP BY DATE(timestamp), defect_type;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW defect_summary_daily;
```

#### 8.2 Caching Strategy
```python
from redis import Redis
import json

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get_cached_data(self, key: str):
        """Get data from cache"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_cached_data(self, key: str, data: dict, ttl: int = 3600):
        """Set data in cache with TTL"""
        self.redis.setex(key, ttl, json.dumps(data))
    
    async def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

# Usage in API endpoints
@router.get("/api/v1/analytics/trends")
async def get_trends(
    start_date: str,
    end_date: str,
    cache_service: CacheService = Depends(get_cache_service)
):
    cache_key = f"trends:{start_date}:{end_date}"
    
    # Try to get from cache first
    cached_data = await cache_service.get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    # Calculate trends
    trends = calculate_trends(start_date, end_date)
    
    # Cache the result
    await cache_service.set_cached_data(cache_key, trends, ttl=1800)
    
    return trends
```

### 9. Deployment Configuration

#### 9.1 Docker Configuration
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Install nginx
RUN apk add --no-cache nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### 9.2 Docker Compose Configuration
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/wafermaps
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-secret-key

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=wafermaps
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 10. Monitoring and Logging

#### 10.1 Application Logging
```python
import logging
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in application
@router.post("/api/v1/inspections")
async def create_inspection(
    inspection: InspectionCreate,
    current_user: User = Depends(get_current_user)
):
    logger.info(
        "Creating inspection",
        user_id=current_user.user_id,
        wafer_id=inspection.wafer_id,
        equipment_id=inspection.equipment_id
    )
    
    try:
        result = await create_inspection_record(inspection)
        logger.info(
            "Inspection created successfully",
            inspection_id=result.inspection_id
        )
        return result
    except Exception as e:
        logger.error(
            "Failed to create inspection",
            error=str(e),
            wafer_id=inspection.wafer_id
        )
        raise
```

#### 10.2 Health Checks
```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psycopg2
import redis

app = FastAPI()

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return JSONResponse(
        content=health_status,
        status_code=200 if health_status["status"] == "healthy" else 503
    )
```

This technical architecture document provides the foundation for implementing the PRD requirements. It covers all aspects of the system design, from database schema to deployment configuration, ensuring a robust and scalable solution for semiconductor fab defect data exploration.
