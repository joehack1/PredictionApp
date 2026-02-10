from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Configuration
    api_title: str = "Premier League Analyst Pro API"
    api_version: str = "0.1.0"
    debug: bool = True
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/prediction_db"
    database_echo: bool = True
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600
    
    # External APIs
    football_data_api_key: str = ""
    football_data_base_url: str = "https://api.football-data.org/v4"
    understat_base_url: str = "https://understat.com/api/v1"
    
    # Model Configuration
    model_retrain_interval_days: int = 7
    prediction_confidence_threshold: float = 0.55
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
