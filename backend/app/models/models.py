from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.config.database import Base


class Team(Base):
    """Team model for storing Premier League team information"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, nullable=True)  # From football-data.org
    name = Column(String(100), unique=True, index=True)
    short_code = Column(String(10), unique=True)
    crest_url = Column(String(500), nullable=True)
    
    # Historical statistics
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    
    # Form metrics
    avg_goals_scored = Column(Float, default=0.0)
    avg_goals_conceded = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    # Elo rating
    elo_rating = Column(Float, default=1500.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")


class Match(Base):
    """Match model for storing Premier League match information"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, nullable=True)  # From football-data.org
    
    # Team information
    home_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    
    # Match details
    match_date = Column(DateTime, index=True)
    venue = Column(String(200), nullable=True)
    
    # Results (NULL if not played yet)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    status = Column(String(50), default="SCHEDULED")  # SCHEDULED, LIVE, FINISHED
    
    # Advanced statistics
    home_xg = Column(Float, nullable=True)
    away_xg = Column(Float, nullable=True)
    home_shots = Column(Integer, nullable=True)
    away_shots = Column(Integer, nullable=True)
    home_shots_on_target = Column(Integer, nullable=True)
    away_shots_on_target = Column(Integer, nullable=True)
    
    # Context
    home_days_rest = Column(Integer, nullable=True)
    away_days_rest = Column(Integer, nullable=True)
    is_derby = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")


class Prediction(Base):
    """Prediction model for storing model predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)
    
    # Model type
    model_type = Column(String(50))  # e.g., "POISSON", "XGBOOST", "ENSEMBLE"
    
    # Outcome predictions
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    
    # Score prediction
    predicted_home_score = Column(Float)
    predicted_away_score = Column(Float)
    most_likely_score = Column(String(10))  # e.g., "1-1"
    
    # Market predictions
    over_2_5_goals = Column(Float)
    under_2_5_goals = Column(Float)
    btts_yes = Column(Float)
    btts_no = Column(Float)
    home_clean_sheet = Column(Float)
    away_clean_sheet = Column(Float)
    
    # Confidence and metadata
    confidence_score = Column(Float)
    prediction_notes = Column(Text, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="predictions")


class User(Base):
    """User model for storing user account information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # User preferences
    favorite_teams = Column(JSON, default=[])
    notifications_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_predictions = relationship("UserPrediction", back_populates="user", cascade="all, delete-orphan")


class UserPrediction(Base):
    """Track user's own predictions vs algorithm"""
    __tablename__ = "user_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)
    
    # User's prediction
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    predicted_score = Column(String(10), nullable=True)
    
    # Accuracy tracking
    was_correct = Column(Boolean, nullable=True)  # After match result
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_predictions")
    match = relationship("Match")
