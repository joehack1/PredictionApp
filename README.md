# Premier League Analyst Pro - Development Guide

## Project Overview

**Premier League Analyst Pro** is a full-stack web application that analyzes Premier League statistics and predicts match outcomes using machine learning. This document provides setup, development, and deployment instructions.

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + TypeScript
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML**: Scikit-learn, Poisson Regression
- **Deployment**: Docker & Docker Compose

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 15+ (if running locally without Docker)
- Redis (if running locally without Docker)
- Python 3.11+
- Node.js 18+

### Setup with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/PredictionApp.git
cd PredictionApp

# Create environment file
cp backend/.env.example backend/.env
# Edit backend/.env and add your FOOTBALL_DATA_API_KEY

# Start services
docker-compose up -d

# Run migrations
docker-compose exec api python -m alembic upgrade head

# Seed initial data (optional)
docker-compose exec api python scripts/seed_data.py
```

API will be available at `http://localhost:8000`

### Local Development Setup

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install PostgreSQL and Redis
# On macOS: brew install postgresql redis
# On Ubuntu: sudo apt-get install postgresql redis-server

# Start services
createdb prediction_db
redis-server

# Create .env file
cp .env.example .env
# Edit with your local database URL and API keys

# Run migrations
python -m alembic upgrade head

# Start API server
python -m uvicorn app.main:app --reload

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
PredictionApp/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── teams.py      # Team endpoints
│   │   │   ├── matches.py    # Match endpoints
│   │   │   └── predictions.py # Prediction endpoints
│   │   ├── config/           # Configuration
│   │   │   ├── settings.py   # App settings
│   │   │   └── database.py   # Database setup
│   │   ├── ml/               # Machine Learning models
│   │   │   └── poisson_model.py  # Poisson prediction model
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic
│   │   │   ├── database_service.py
│   │   │   ├── football_data_service.py
│   │   │   └── data_sync_service.py
│   │   └── main.py           # FastAPI app initialization
│   ├── tests/                # Unit tests
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main dashboard component
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── public/
├── docker-compose.yml
└── README.md
```

---

## API Endpoints

### Teams
```
GET /api/v1/teams              # List all teams
GET /api/v1/teams/{id}         # Get team details
GET /api/v1/teams/{id}/form    # Get team form (last N matches)
```

### Matches
```
GET /api/v1/matches/upcoming   # Get upcoming matches
GET /api/v1/matches/recent     # Get recent matches
GET /api/v1/matches/{id}       # Get match details with predictions
```

### Predictions
```
POST /api/v1/predict/match/{id}        # Predict single match
POST /api/v1/predict/batch             # Predict all upcoming matches
GET /api/v1/predict/match/{id}/detailed  # Get detailed predictions
```

### System
```
GET /health                    # Health check
GET /api/v1                    # API info
```

---

## Database Schema

### Tables

#### teams
Store Premier League team information and statistics.
- `id`: Primary key
- `external_id`: ID from football-data.org
- `name`: Team name (unique)
- `short_code`: 3-letter code (e.g., "MCI")
- `matches_played`, `wins`, `draws`, `losses`: Match statistics
- `goals_for`, `goals_against`: Scoring statistics
- `avg_goals_scored`, `avg_goals_conceded`: Average metrics
- `elo_rating`: Current Elo rating
- `created_at`, `updated_at`: Timestamps

#### matches
Store match information and results.
- `id`: Primary key
- `external_id`: ID from football-data.org
- `home_team_id`, `away_team_id`: Foreign keys to teams
- `match_date`: Match kickoff time
- `home_goals`, `away_goals`: Match result (null if not played)
- `status`: "SCHEDULED", "LIVE", or "FINISHED"
- `home_xg`, `away_xg`: Expected goals
- `home_shots`, `away_shots`: Shot counts
- Advanced metrics for team comparison

#### predictions
Store model predictions for matches.
- `id`: Primary key
- `match_id`: Foreign key to matches
- `model_type`: "POISSON", "XGBOOST", "ENSEMBLE", etc.
- `home_win_prob`, `draw_prob`, `away_win_prob`: Outcome probabilities
- `predicted_home_score`, `predicted_away_score`: Expected goals
- `most_likely_score`: e.g., "2-1"
- Market predictions: `over_2_5_goals`, `btts_yes`, `home_clean_sheet`, etc.
- `confidence_score`: Prediction confidence (0-1)
- `created_at`: When prediction was made

#### users
User account information.
- `id`: Primary key
- `email`, `username`: Unique identifiers
- `hashed_password`: Secure password
- `favorite_teams`: JSON array of team IDs
- `notifications_enabled`: Push notification preference

#### user_predictions
Track user's own predictions vs algorithm.
- `id`: Primary key
- `user_id`, `match_id`: Foreign keys
- `home_win_prob`, `draw_prob`, `away_win_prob`: User prediction
- `was_correct`: Accuracy after match result

---

## Machine Learning Models

### Poisson Regression Model

The primary prediction model uses Poisson distribution to estimate match outcomes.

**How it works:**
1. Estimates attack strength and defense weakness for each team
2. Calculates expected goals for home and away teams
3. Uses Poisson distribution to generate probabilities for all possible scorelines
4. Aggregates to produce win/draw/loss and market probabilities

**Parameters:**
- `home_attack_param`: Team's attacking strength at home
- `away_attack_param`: Team's attacking strength away
- `home_defense_param`: Team's defensive weakness at home
- `away_defense_param`: Team's defensive weakness away
- `league_home_advantage`: Home team advantage factor

**Accuracy:**
- Target: >55% for match outcome prediction
- Current confidence threshold: 0.55

### Future Models
- **XGBoost**: Classification for match outcomes
- **Random Forest**: Feature importance analysis
- **LSTM Networks**: Time-series form analysis
- **Ensemble**: Weighted combination of all models

---

## Data Synchronization

### Football-data.org Integration

The application syncs with [football-data.org](https://www.football-data.org/) to keep data current.

**Required:**
1. Get API key from https://www.football-data.org/client/register
2. Add to `.env`: `FOOTBALL_DATA_API_KEY=your_key`

**Data synced:**
- Team information and standings
- Match schedules and results
- Historical season data

**Sync endpoints:**
```python
# Sync teams from standings
await data_sync_service.sync_teams()

# Sync upcoming matches (next 14 days)
await data_sync_service.sync_upcoming_matches(days_ahead=14)

# Sync completed match results
await data_sync_service.sync_match_results(days_back=30)
```

---

## Configuration

### Environment Variables

Create `backend/.env` with:

```
# API Configuration
FOOTBALL_DATA_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/prediction_db
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# Security
SECRET_KEY=your-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

### Settings (Python)

Edit `backend/app/config/settings.py` for application defaults:
- API configuration
- Database pool sizing
- Model parameters
- Cache settings

---

## Development Workflow

### Running Tests

```bash
# Unit tests
pytest backend/tests/

# With coverage
pytest backend/tests/ --cov=app

# Specific test
pytest backend/tests/test_models.py::TestPoissonModel::test_match_prediction
```

### Code Quality

```bash
# Format code
black backend/

# Type checking
mypy backend/app/

# Lint
flake8 backend/
```

### Database Migrations

```bash
# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t prediction-api backend/

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e FOOTBALL_DATA_API_KEY=... \
  prediction-api

# With compose
docker-compose up -d
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure CORS for frontend domain
- [ ] Set up HTTPS/SSL
- [ ] Configure database backups
- [ ] Set up logging and monitoring
- [ ] Enable Redis persistence
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline

### AWS/GCP Deployment

The application can be deployed to:
- **AWS**: ECS, Elastic Beanstalk, or AppRunner
- **GCP**: Cloud Run, App Engine, or GKE
- **Heroku**: Simple git push deployment
- **DigitalOcean**: App Platform or Kubernetes

Requires environment variable configuration in cloud provider settings.

---

## API Documentation

### Interactive Docs

When running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Request

```bash
# Get upcoming matches
curl http://localhost:8000/api/v1/matches/upcoming?limit=5

# Predict single match
curl -X POST http://localhost:8000/api/v1/predict/match/123

# Get detailed prediction
curl http://localhost:8000/api/v1/predict/match/123/detailed
```

---

## Troubleshooting

### Common Issues

**Connection refused (PostgreSQL)**
```bash
# Check if PostgreSQL is running
psql --version
# Start PostgreSQL (Docker)
docker-compose up postgres
```

**Empty predictions**
- Ensure sufficient historical data in database
- Run `docker-compose exec api python scripts/seed_data.py`
- Check API logs: `docker-compose logs api`

**Model not training**
```bash
# Check database connection
docker-compose exec api python -c "from app.config.database import SessionLocal; SessionLocal()"
```

**Port already in use**
```bash
# Change port in docker-compose.yml or:
docker-compose up -p 8001:8000
```

---

## Performance Optimization

### Database
- Added indexes on frequently queried columns
- Connection pooling with `pool_size=10`
- Pre-ping connections for stability

### Caching
- Redis for match predictions (TTL: 1 hour)
- Model parameters cached after training
- API responses cached by client library

### API
- Asynchronous endpoints where possible
- Pagination for large result sets
- Selective field loading

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Run tests: `pytest`
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

---

## License

This project is provided as-is for development and educational purposes.

---

## Support

For issues, questions, or feedback:
- Create GitHub issue
- Check documentation at `/docs` endpoint
- Review test cases for usage examples

**Last Updated**: February 10, 2026
**API Version**: v1.0
**Status**: MVP Phase
