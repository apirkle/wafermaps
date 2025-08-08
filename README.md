# Introduction

This is a vibe coding experiment testing the capabilities of Cursor and GPT-5. Dev chat logs are in `cursor_dev_chat1.md` and `cursor_dev_chat2.md`.

# WaferMaps - Semiconductor Fab Defect Data System

A comprehensive web application for managing and visualizing semiconductor wafer inspection data, defects, and analytics in a semiconductor fabrication facility.

## 🚀 Features

### Core Functionality
- **Wafer Management**: Track and manage semiconductor wafers with detailed specifications
- **Inspection Tracking**: Monitor inspection processes and results
- **Defect Analysis**: Visualize and analyze defects with severity classification
- **Equipment Management**: Track inspection equipment and maintenance schedules
- **Analytics Dashboard**: Comprehensive analytics and reporting
- **Interactive Wafer Maps**: Visual defect plotting on wafer representations

### Key Features
- **Real-time Data Visualization**: Interactive wafer maps showing defect locations
- **Multi-dimensional Analytics**: Defect trends, equipment performance, and quality metrics
- **Responsive Design**: Modern UI that works on desktop and mobile devices
- **RESTful API**: Comprehensive backend API for data management
- **Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture

### Frontend
- **React 18** with TypeScript
- **Redux Toolkit** for state management
- **React Router** for navigation
- **SVG-based Wafer Maps** for defect visualization
- **Responsive CSS** with modern design

### Backend
- **FastAPI** (Python) for high-performance API
- **PostgreSQL** for primary data storage
- **Redis** for caching and session management
- **MinIO** for object storage
- **SQLAlchemy** for ORM and database management

### Infrastructure
- **Docker** for containerization
- **Nginx** as reverse proxy
- **PostgreSQL** for relational data
- **Redis** for caching
- **MinIO** for file storage

## 🛠️ Technology Stack

### Frontend
- React 18
- TypeScript
- Redux Toolkit
- React Router
- CSS3 with Flexbox/Grid

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Redis

### DevOps
- Docker
- Docker Compose
- Nginx
- GitHub Actions (ready for CI/CD)

## 📦 Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/apirkle/wafermaps.git
   cd wafermaps
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:13001
   - Backend API: http://localhost:18080
   - Nginx Gateway: http://localhost:80
   - MinIO Console: http://localhost:9003 (admin/admin)

### Development Setup

1. **Backend Development**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🗄️ Database Schema

### Core Entities
- **Wafers**: Semiconductor wafers with specifications
- **Inspections**: Inspection processes and results
- **Defects**: Defect details with coordinates and severity
- **Equipment**: Inspection equipment and maintenance
- **Users**: System users and authentication

### Key Relationships
- Wafers have multiple Inspections
- Inspections have multiple Defects
- Equipment performs Inspections
- Users manage all entities

## 🔌 API Endpoints

### Core Endpoints
- `GET /api/v1/wafers/` - List wafers with pagination
- `GET /api/v1/inspections/` - List inspections with filtering
- `GET /api/v1/defects/` - List defects with filtering
- `GET /api/v1/equipment/` - List equipment
- `GET /api/v1/analytics/` - Analytics summary

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration

## 🎯 Key Features in Detail

### Interactive Wafer Maps
- Visual representation of wafer with defect plotting
- Color-coded defects by severity level
- Hover interactions for defect details
- Responsive design for different wafer sizes
- Real-time data from inspection results

### Analytics Dashboard
- Defect trends over time
- Equipment performance metrics
- Quality score calculations
- Pareto analysis of defect types
- Interactive charts and visualizations

### Equipment Management
- Equipment status tracking
- Maintenance scheduling
- Performance analytics
- Operator assignment
- Location tracking

## 🚀 Deployment

### Production Deployment
1. Set up environment variables
2. Configure database connections
3. Set up SSL certificates
4. Deploy with Docker Compose
5. Configure monitoring and logging

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/db

# Redis
REDIS_URL=redis://host:port

# MinIO
MINIO_URL=http://host:port
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# Security
SECRET_KEY=your_secret_key
ENVIRONMENT=production
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `/docs` when running

## 🔮 Roadmap

- [ ] Real-time notifications
- [ ] Advanced analytics with ML
- [ ] Mobile app
- [ ] Integration with fab equipment
- [ ] Advanced reporting
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Advanced security features

---

**Built with ❤️ for semiconductor manufacturing excellence**
