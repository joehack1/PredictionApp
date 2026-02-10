from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# Team Schemas
class TeamBase(BaseModel):
    name: str
    short_code: str


class TeamCreate(TeamBase):
    external_id: Optional[int] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    avg_goals_scored: Optional[float] = None
    avg_goals_conceded: Optional[float] = None
    win_rate: Optional[float] = None
    elo_rating: Optional[float] = None


class TeamResponse(TeamBase):
    id: int
    external_id: Optional[int]
    crest_url: Optional[str]
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    avg_goals_scored: float
    avg_goals_conceded: float
    win_rate: float
    elo_rating: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Match Schemas
class MatchBase(BaseModel):
    home_team_id: int
    away_team_id: int
    match_date: datetime


class MatchCreate(MatchBase):
    external_id: Optional[int] = None
    venue: Optional[str] = None


class MatchUpdate(BaseModel):
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    status: Optional[str] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None


class MatchResponse(MatchBase):
    id: int
    external_id: Optional[int]
    home_goals: Optional[int]
    away_goals: Optional[int]
    status: str
    venue: Optional[str]
    home_team: TeamResponse
    away_team: TeamResponse
    home_xg: Optional[float]
    away_xg: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchDetailedResponse(MatchResponse):
    """Extended match response with predictions"""
    home_days_rest: Optional[int]
    away_days_rest: Optional[int]
    is_derby: bool
    home_shots: Optional[int]
    away_shots: Optional[int]
    home_shots_on_target: Optional[int]
    away_shots_on_target: Optional[int]


# Prediction Schemas
class PredictionBase(BaseModel):
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_score: float
    predicted_away_score: float


class PredictionCreate(PredictionBase):
    match_id: int
    model_type: str
    confidence_score: float
    most_likely_score: Optional[str] = None
    over_2_5_goals: Optional[float] = None
    under_2_5_goals: Optional[float] = None
    btts_yes: Optional[float] = None
    btts_no: Optional[float] = None
    home_clean_sheet: Optional[float] = None
    away_clean_sheet: Optional[float] = None


class PredictionResponse(PredictionBase):
    id: int
    match_id: int
    model_type: str
    most_likely_score: Optional[str]
    over_2_5_goals: Optional[float]
    under_2_5_goals: Optional[float]
    btts_yes: Optional[float]
    btts_no: Optional[float]
    home_clean_sheet: Optional[float]
    away_clean_sheet: Optional[float]
    confidence_score: float
    prediction_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchWithPredictionResponse(MatchDetailedResponse):
    """Match with associated predictions"""
    predictions: List[PredictionResponse] = []


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    favorite_teams: List[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    favorite_teams: Optional[List[int]] = None
    notifications_enabled: Optional[bool] = None


# User Prediction Schemas
class UserPredictionCreate(BaseModel):
    match_id: int
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_score: Optional[str] = None
    confidence: float = Field(ge=0, le=1)


class UserPredictionResponse(BaseModel):
    id: int
    user_id: int
    match_id: int
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_score: Optional[str]
    was_correct: Optional[bool]
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Response Wrappers
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
