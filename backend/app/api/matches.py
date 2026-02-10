from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.schemas import MatchResponse, MatchDetailedResponse, MatchWithPredictionResponse
from app.services.database_service import MatchService, PredictionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


@router.get("/upcoming", response_model=List[MatchDetailedResponse])
async def get_upcoming_matches(
    limit: int = Query(10, ge=1, le=50),
    days_ahead: int = Query(10, ge=1, le=30),
    detailed: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get upcoming Premier League matches"""
    matches = MatchService.get_upcoming_matches(db, days_ahead=days_ahead, limit=limit)
    return matches


@router.get("/recent", response_model=List[MatchDetailedResponse])
async def get_recent_matches(
    limit: int = Query(10, ge=1, le=50),
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get recent completed matches"""
    matches = MatchService.get_recent_matches(db, days_back=days_back, limit=limit)
    return matches


@router.get("/{match_id}", response_model=MatchWithPredictionResponse)
async def get_match_detail(match_id: int, db: Session = Depends(get_db)):
    """Get detailed match information with predictions"""
    match = MatchService.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    predictions = PredictionService.get_match_predictions(db, match_id)
    
    match_dict = {
        **match.__dict__,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "predictions": predictions
    }
    
    return match_dict


@router.get("/{match_id}/predictions")
async def get_match_predictions(match_id: int, db: Session = Depends(get_db)):
    """Get all predictions for a match"""
    from app.schemas.schemas import PredictionResponse
    
    match = MatchService.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    predictions = PredictionService.get_match_predictions(db, match_id)
    
    return {
        "match_id": match_id,
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "match_date": match.match_date,
        "predictions": predictions
    }


@router.get("/{match_id}/head-to-head")
async def get_head_to_head(match_id: int, limit: int = Query(10, ge=1, le=30), db: Session = Depends(get_db)):
    """Get head-to-head history for teams in a match"""
    match = MatchService.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    h2h = MatchService.head_to_head(db, match.home_team_id, match.away_team_id, limit=limit)
    
    home_wins = sum(1 for m in h2h if m.home_team_id == match.home_team_id and m.home_goals > m.away_goals)
    away_wins = sum(1 for m in h2h if m.home_team_id == match.home_team_id and m.home_goals < m.away_goals)
    draws = sum(1 for m in h2h if m.home_goals == m.away_goals)
    
    return {
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "statistics": {
            f"{match.home_team.name}_wins": home_wins,
            f"{match.away_team.name}_wins": away_wins,
            "draws": draws,
            "total_matches": len(h2h)
        },
        "recent_matches": h2h
    }
