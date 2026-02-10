from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.config.database import engine, Base
from app.api import teams, matches, predictions
from app.services.football_data_service import FootballDataService
import logging

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Global service instances
football_data_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle"""
    global football_data_service
    
    # Startup
    logger.info("Starting Premier League Analyst Pro API")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize services
    football_data_service = FootballDataService()
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")
    if football_data_service:
        await football_data_service.close()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-Powered Premier League Match Prediction Platform",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(predictions.router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Premier League Analyst Pro API",
        "version": settings.api_version,
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version
    }


@app.get("/api/v1")
async def api_info():
    """API v1 information"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "teams": "/api/v1/teams",
            "matches": "/api/v1/matches",
            "predictions": "/api/v1/predict"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower()
    )
