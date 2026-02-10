from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.schemas import TeamResponse
from app.services.database_service import TeamService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("/", response_model=List[TeamResponse])
async def get_all_teams(db: Session = Depends(get_db)):
    """Get all Premier League teams"""
    teams = TeamService.get_all_teams(db)
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get specific team details"""
    team = TeamService.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_id}/form")
async def get_team_form(
    team_id: int,
    matches: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get team's recent form (last N matches)"""
    from app.services.database_service import MatchService
    
    team = TeamService.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    recent_matches = MatchService.get_team_recent_matches(db, team_id, limit=matches)
    
    form_data = {
        "team_id": team_id,
        "team_name": team.name,
        "matches": [],
        "statistics": {
            "matches_played": len(recent_matches),
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
    }
    
    for match in recent_matches:
        is_home = match.home_team_id == team_id
        goals_for = match.home_goals if is_home else match.away_goals
        goals_against = match.away_goals if is_home else match.home_goals
        
        if goals_for > goals_against:
            result = "WIN"
            form_data["statistics"]["wins"] += 1
        elif goals_for < goals_against:
            result = "LOSS"
            form_data["statistics"]["losses"] += 1
        else:
            result = "DRAW"
            form_data["statistics"]["draws"] += 1
        
        form_data["statistics"]["goals_for"] += goals_for
        form_data["statistics"]["goals_against"] += goals_against
        
        opponent = match.away_team if is_home else match.home_team
        form_data["matches"].append({
            "match_id": match.id,
            "date": match.match_date,
            "opponent": opponent.name,
            "score": f"{goals_for}-{goals_against}",
            "result": result,
            "venue": "Home" if is_home else "Away"
        })
    
    return form_data
