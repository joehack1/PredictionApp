# 🚀 Quick Start Guide

## 60-Second Setup

### Option 1: Docker (Recommended)

```bash
# 1. Start everything
docker-compose up -d

# 2. Wait 10 seconds for services to start

# 3. Open in browser
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Frontend: http://localhost:5173 (if running npm run dev)

# Done! 🎉
```

### Option 2: Run Setup Script

```bash
# Make script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Follow the prompts
```

### Option 3: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit: Add FOOTBALL_DATA_API_KEY

# Database (requires PostgreSQL running)
python -m alembic upgrade head

# Start API
python -m uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

---

## Test the API

### 1. **Swagger UI** (Easiest)
Open: http://localhost:8000/docs
- Try endpoint buttons directly
- See response formats
- Modify parameters

### 2. **cURL**

```bash
# Get teams
curl http://localhost:8000/api/v1/teams

# Get upcoming matches
curl http://localhost:8000/api/v1/matches/upcoming?limit=3

# Predict a match
curl -X POST http://localhost:8000/api/v1/predict/match/1
```

### 3. **Python**

```python
import requests

api = "http://localhost:8000/api/v1"

# Get teams
teams = requests.get(f"{api}/teams").json()
print(f"Teams: {len(teams)}")

# Get upcoming matches
matches = requests.get(f"{api}/matches/upcoming").json()
print(f"Upcoming: {len(matches)}")

# For each match, get prediction
for match in matches[:3]:
    pred = requests.post(f"{api}/predict/match/{match['id']}").json()
    print(f"{match['home_team']['name']} vs {match['away_team']['name']}: {pred['prediction']['most_likely_score']}")
```

---

## Common Commands

### Docker

```bash
# View logs
docker-compose logs api

# Restart API
docker-compose restart api

# Stop everything
docker-compose down

# Stop and remove data
docker-compose down -v

# Run migrations
docker-compose exec api python -m alembic upgrade head

# Open database shell
docker-compose exec postgres psql -U prediction_user -d prediction_db

# Redis CLI
docker-compose exec redis redis-cli
```

### Testing

```bash
# Run all tests
pytest backend/tests/

# Specific test
pytest backend/tests/test_models.py::TestPoissonModel::test_match_prediction

# With coverage
pytest backend/tests/ --cov=app

# Verbose output
pytest backend/tests/ -v -s
```

### Database

```bash
# Backup database
docker-compose exec postgres pg_dump -U prediction_user prediction_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U prediction_user prediction_db < backup.sql

# Delete and recreate
docker-compose down -v
docker-compose up -d
```

---

## Configuration

### Add Football-data.org API Key

1. Visit https://www.football-data.org/client/register
2. Copy your API key
3. Edit `backend/.env`:
   ```
   FOOTBALL_DATA_API_KEY=your_key_here
   ```
4. Restart API: `docker-compose restart api`

### Sync Data from API

```python
# In Python shell or script
from app.config.database import SessionLocal
from app.services.football_data_service import FootballDataService
from app.services.data_sync_service import DataSyncService
import asyncio

async def sync():
    db = SessionLocal()
    api = FootballDataService()
    sync_service = DataSyncService(db, api)
    
    # Sync teams
    await sync_service.sync_teams()
    
    # Sync upcoming matches
    await sync_service.sync_upcoming_matches(days_ahead=14)
    
    # Sync results
    await sync_service.sync_match_results(days_back=30)
    
    db.close()
    await api.close()

asyncio.run(sync())
```

---

## Project Structure Overview

```
PredictionApp/
├── backend/          # FastAPI server
├── frontend/         # React dashboard
├── docker-compose.yml # Multi-service orchestration
└── docs/            # Documentation
```

### Backend Key Files
- `backend/app/main.py` - FastAPI app
- `backend/app/api/` - Endpoints
- `backend/app/ml/poisson_model.py` - ML model
- `backend/app/models/models.py` - Database models
- `backend/requirements.txt` - Dependencies

### Frontend Key Files
- `frontend/src/App.tsx` - Main dashboard
- `frontend/src/hooks/useApi.ts` - API integration
- `frontend/package.json` - Dependencies

---

## File Structure Reference

```
PredictionApp/
├── README.md                    # Full development guide
├── IMPLEMENTATION_SUMMARY.md    # What was built
├── QUICKSTART.md               # This file
├── setup.sh                     # Automated setup
├── docker-compose.yml           # Docker orchestration
└── backend/
    ├── app/
    │   ├── main.py             # FastAPI app
    │   ├── api/                # Endpoints
    │   ├── models/             # Database models
    │   ├── services/           # Business logic
    │   ├── ml/                 # ML models
    │   └── config/             # Configuration
    ├── alembic/                # Migrations
    ├── tests/                  # Unit tests
    ├── requirements.txt        # Python deps
    └── Dockerfile              # Container
└── frontend/
    ├── src/                    # React code
    ├── package.json            # Node deps
    └── vite.config.ts          # Bundler config
```

---

## Useful Links

- 📚 **Full Docs**: See README.md
- 📖 **API Reference**: See docs/API.md
- 🐍 **FastAPI**: https://fastapi.tiangolo.com
- ⚛️ **React**: https://react.dev
- 🎲 **Football Data**: https://www.football-data.org

---

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml or:
docker-compose up -p 8001:8000
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### No Data Available
```bash
# You need to add FOOTBALL_DATA_API_KEY and sync data
# See "Configuration" section above
```

### Frontend Not Loading
```bash
# Install dependencies
cd frontend
npm install
npm run dev
```

---

## Next Steps

1. ✅ Get API running (docker-compose up -d)
2. ✅ Explore endpoints (/docs)
3. ✅ Add API key (Football-data.org)
4. ✅ Sync real data
5. ✅ Run tests (pytest)
6. ✅ Customize frontend
7. 📖 Read full README.md for advanced setup

---

## Getting Help

Need more info? Check these:
- `README.md` - Comprehensive guide
- `docs/API.md` - All API endpoints
- `backend/tests/test_models.py` - Usage examples
- API docs at http://localhost:8000/docs

**Happy predicting! ⚽🎲**
