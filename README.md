# ToxZone - Emergency Exposure Boundary Planner

Professional web-based tool for determining Emergency Planning Zones (EPZ) based on toxic exposure thresholds.

## Features

- **Chemical Database**: 300+ chemicals with complete properties and exposure thresholds
- **Facility Management**: Register industrial facilities with chemical inventory
- **Scenario Builder**: Create release scenarios with multiple source term models
- **EPZ Calculation**: Dual dispersion models (Gaussian plume + heavy gas)
- **Multi-Threshold Zones**: ERPG, IDLH, AEGL thresholds on one map
- **Interactive Maps**: Real-time zone visualization
- **Population Impact**: Estimate affected population
- **GIS Export**: KML, GeoJSON exports
- **Emergency Briefing**: One-click PDF generation

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + PostGIS
- **Cache**: Redis
- **Calculation**: NumPy + SciPy
- **PDF Generation**: WeasyPrint

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Maps**: MapLibre GL JS + Turf.js
- **State**: React Query
- **UI**: shadcn/ui

## Quick Start

### Using Docker Compose

```bash
# Clone repository
cd ~/engineering-tools-suite/toxzone

# Start services
docker-compose up -d

# Access application
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

### Manual Setup

#### Backend

```bash
cd backend

# Install dependencies (requires Poetry)
poetry install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration

# Run database migrations (Alembic - coming soon)
# poetry run alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
toxzone/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── core/           # Calculation engines
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas.py      # Pydantic schemas
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/               # React frontend (coming soon)
│   ├── src/
│   └── package.json
├── data/                   # Data files
│   └── chemicals_seed.json
├── docker-compose.yml
└── README.md
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql+asyncpg://toxzone:toxzone_pass@localhost:5432/toxzone
REDIS_URL=redis://localhost:6379/0
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Development

### Running Tests

```bash
# Backend
cd backend
poetry run pytest

# Frontend
cd frontend
npm test
```

### Code Style

```bash
# Backend - Black formatting
cd backend
poetry run black src/

# Frontend - ESLint
cd frontend
npm run lint
```

## Contributing

This is part of the Engineering Tools Suite. See the main repository for contribution guidelines.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **EPA AEGL Database** - Chemical threshold values
- **AIHA ERPG/WEEL** - Emergency response planning guidelines
- **NIOSH Pocket Guide** - Occupational exposure limits
- **Britter & McQuaid** - Heavy gas dispersion model