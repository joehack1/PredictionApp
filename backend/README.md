# Backend API - Premier League Analyst Pro

## Overview

FastAPI-based backend for Premier League match prediction. Provides RESTful API endpoints for teams, matches, and predictions using a Poisson regression model.

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run migrations
python -m alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload

# API docs will be at http://localhost:8000/docs
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API route handlers
│   │   ├── teams.py            # Team endpoints
│   │   ├── matches.py          # Match endpoints
│   │   └── predictions.py      # Prediction endpoints
│   ├── config/                 # Configuration
│   │   ├── settings.py         # App settings
│   │   └── database.py         # Database setup
│   ├── ml/                     # Machine learning
│   │   └── poisson_model.py    # Poisson prediction model
│   ├── models/                 # SQLAlchemy ORM models
│   │   └── models.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   └── schemas.py
│   ├── services/               # Business logic
│   │   ├── database_service.py
│   │   ├── football_data_service.py
│   │   └── data_sync_service.py
│   └── utils/                  # Utility functions
├── tests/                      # Unit tests
│   └── test_models.py
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── versions/
│   │   └── 001_initial_schema.py
│   └── alembic.ini
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── .env.example                # Environment template
└── README.md                   # This file
```

## Dependencies

### Core
- **fastapi** (0.104.1) - Modern web framework
- **uvicorn** (0.24.0) - ASGI server
- **sqlalchemy** (2.0.23) - ORM
- **psycopg2-binary** (2.9.9) - PostgreSQL adapter
- **alembic** (1.13.0) - Migrations

### Data & ML
- **pydantic** (2.5.0) - Data validation
- **pandas** (2.1.3) - Data manipulation
- **numpy** (1.26.2) - Numerical computing
- **scikit-learn** (1.3.2) - ML algorithms
- **scipy** (1.11.4) - Scientific computing

### API & Services
- **httpx** (0.25.2) - Async HTTP client
- **redis** (5.0.1) - Cache client
- **python-dotenv** (1.0.0) - Environment management

### Testing & Security
- **pytest** (7.4.3) - Testing framework
- **pytest-asyncio** (0.21.1) - Async test support
- **passlib** (1.7.4) - Password hashing
- **python-jose** (3.3.0) - JWT tokens

See `requirements.txt` for complete list with versions.

## API Endpoints

### Teams
- `GET /api/v1/teams` - List all teams
- `GET /api/v1/teams/{id}` - Get team details
- `GET /api/v1/teams/{id}/form` - Get team form

### Matches
- `GET /api/v1/matches/upcoming` - Upcoming matches
- `GET /api/v1/matches/recent` - Recent matches
- `GET /api/v1/matches/{id}` - Match details

### Predictions
- `POST /api/v1/predict/match/{id}` - Predict single match
- `POST /api/v1/predict/batch` - Predict all upcoming
- `GET /api/v1/predict/match/{id}/detailed` - Detailed prediction

See `../docs/API.md` for full documentation.

## Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=app

# Specific test
pytest tests/test_models.py::TestPoissonModel::test_match_prediction -v
```

## Deployment

```bash
# Docker
docker build -t prediction-api .

# Docker Compose
docker-compose up -d
```

---

**Last Updated**: February 10, 2026  
**Status**: MVP Phase 1
