#!/bin/bash

# Premier League Analyst Pro - Setup Script

set -e

echo "🏆 Premier League Analyst Pro - Setup"
echo "======================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📋 Creating .env file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your FOOTBALL_DATA_API_KEY"
fi

# Build and start services
echo "🚀 Starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T api python -m alembic upgrade head

# Create initial teams (optional)
echo "📊 Setting up initial data..."
docker-compose exec -T api python -c "
from app.config.database import SessionLocal
from app.models.models import Team

db = SessionLocal()
teams_data = [
    {'name': 'Manchester City', 'short_code': 'MCI', 'external_id': 333},
    {'name': 'Liverpool', 'short_code': 'LIV', 'external_id': 64},
    {'name': 'Arsenal', 'short_code': 'ARS', 'external_id': 1},
    {'name': 'Manchester United', 'short_code': 'MUN', 'external_id': 66},
    {'name': 'Chelsea', 'short_code': 'CHE', 'external_id': 65},
]

for team_data in teams_data:
    existing = db.query(Team).filter(Team.name == team_data['name']).first()
    if not existing:
        team = Team(**team_data)
        db.add(team)

db.commit()
db.close()
print('✅ Teams initialized')
" || echo "⚠️  Teams already exist"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Services running:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Database: localhost:5432"
echo "   - Cache: localhost:6379"
echo ""
echo "📚 Next steps:"
echo "   1. Visit http://localhost:8000/docs to explore API"
echo "   2. Review README.md for development guide"
echo "   3. Check docs/API.md for endpoint documentation"
echo ""
echo "🔧 Common commands:"
echo "   docker-compose logs api             # View API logs"
echo "   docker-compose down                 # Stop all services"
echo "   docker-compose restart api          # Restart API"
