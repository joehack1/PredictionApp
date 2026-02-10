from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Match, Team, Prediction
from app.schemas.schemas import MatchCreate, MatchUpdate, PredictionCreate
import logging

logger = logging.getLogger(__name__)


class TeamService:
    """Service for team operations"""
    
    @staticmethod
    def get_team(db: Session, team_id: int) -> Optional[Team]:
        """Get team by ID"""
        return db.query(Team).filter(Team.id == team_id).first()
    
    @staticmethod
    def get_team_by_name(db: Session, name: str) -> Optional[Team]:
        """Get team by name"""
        return db.query(Team).filter(Team.name == name).first()
    
    @staticmethod
    def get_all_teams(db: Session) -> List[Team]:
        """Get all teams"""
        return db.query(Team).all()
    
    @staticmethod
    def create_team(db: Session, name: str, short_code: str, external_id: Optional[int] = None) -> Team:
        """Create new team"""
        team = Team(name=name, short_code=short_code, external_id=external_id)
        db.add(team)
        db.commit()
        db.refresh(team)
        return team
    
    @staticmethod
    def update_team_stats(db: Session, team_id: int, **kwargs) -> Optional[Team]:
        """Update team statistics"""
        team = db.query(Team).filter(Team.id == team_id).first()
        if team:
            for key, value in kwargs.items():
                if hasattr(team, key):
                    setattr(team, key, value)
            team.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(team)
        return team


class MatchService:
    """Service for match operations"""
    
    @staticmethod
    def get_match(db: Session, match_id: int) -> Optional[Match]:
        """Get match by ID"""
        return db.query(Match).filter(Match.id == match_id).first()
    
    @staticmethod
    def get_upcoming_matches(db: Session, days_ahead: int = 10, limit: int = 50) -> List[Match]:
        """Get upcoming matches within specified days"""
        from_date = datetime.utcnow()
        to_date = from_date + timedelta(days=days_ahead)
        
        return db.query(Match).filter(
            and_(
                Match.match_date >= from_date,
                Match.match_date <= to_date,
                Match.status == "SCHEDULED"
            )
        ).order_by(Match.match_date).limit(limit).all()
    
    @staticmethod
    def get_recent_matches(db: Session, days_back: int = 30, limit: int = 50) -> List[Match]:
        """Get recent completed matches"""
        from_date = datetime.utcnow() - timedelta(days=days_back)
        
        return db.query(Match).filter(
            and_(
                Match.match_date >= from_date,
                Match.status == "FINISHED"
            )
        ).order_by(desc(Match.match_date)).limit(limit).all()
    
    @staticmethod
    def get_team_recent_matches(db: Session, team_id: int, limit: int = 10) -> List[Match]:
        """Get recent matches for a specific team"""
        from_date = datetime.utcnow() - timedelta(days=90)
        
        return db.query(Match).filter(
            and_(
                Match.match_date >= from_date,
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                Match.status == "FINISHED"
            )
        ).order_by(desc(Match.match_date)).limit(limit).all()
    
    @staticmethod
    def create_match(db: Session, match_data: MatchCreate) -> Match:
        """Create new match"""
        match = Match(**match_data.model_dump())
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
    
    @staticmethod
    def update_match(db: Session, match_id: int, match_data: MatchUpdate) -> Optional[Match]:
        """Update match information"""
        match = db.query(Match).filter(Match.id == match_id).first()
        if match:
            update_data = match_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(match, key):
                    setattr(match, key, value)
            match.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(match)
        return match
    
    @staticmethod
    def head_to_head(db: Session, team1_id: int, team2_id: int, limit: int = 10) -> List[Match]:
        """Get head-to-head records between two teams"""
        from sqlalchemy import or_
        
        return db.query(Match).filter(
            and_(
                or_(
                    and_(Match.home_team_id == team1_id, Match.away_team_id == team2_id),
                    and_(Match.home_team_id == team2_id, Match.away_team_id == team1_id)
                ),
                Match.status == "FINISHED"
            )
        ).order_by(desc(Match.match_date)).limit(limit).all()


class PredictionService:
    """Service for prediction operations"""
    
    @staticmethod
    def create_prediction(db: Session, prediction_data: PredictionCreate) -> Prediction:
        """Create new prediction"""
        prediction = Prediction(**prediction_data.model_dump())
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    
    @staticmethod
    def get_match_predictions(db: Session, match_id: int) -> List[Prediction]:
        """Get all predictions for a match"""
        return db.query(Prediction).filter(Prediction.match_id == match_id).all()
    
    @staticmethod
    def get_latest_prediction(db: Session, match_id: int, model_type: str = "ENSEMBLE") -> Optional[Prediction]:
        """Get latest prediction for a match by model type"""
        return db.query(Prediction).filter(
            and_(
                Prediction.match_id == match_id,
                Prediction.model_type == model_type
            )
        ).order_by(desc(Prediction.created_at)).first()
    
    @staticmethod
    def update_prediction_accuracy(db: Session, match_id: int) -> None:
        """Update prediction accuracy after match is finished"""
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match or match.home_goals is None or match.away_goals is None:
            return
        
        predictions = db.query(Prediction).filter(Prediction.match_id == match_id).all()
        
        for pred in predictions:
            # Check if prediction was correct
            if match.home_goals > match.away_goals:
                actual_result = "home_win"
            elif match.home_goals < match.away_goals:
                actual_result = "away_win"
            else:
                actual_result = "draw"
            
            # Determine if prediction was correct
            if actual_result == "home_win" and pred.home_win_prob > pred.draw_prob and pred.home_win_prob > pred.away_win_prob:
                pred.was_correct = True
            elif actual_result == "away_win" and pred.away_win_prob > pred.draw_prob and pred.away_win_prob > pred.home_win_prob:
                pred.was_correct = True
            elif actual_result == "draw" and pred.draw_prob > pred.home_win_prob and pred.draw_prob > pred.away_win_prob:
                pred.was_correct = True
            else:
                pred.was_correct = False
            
            db.commit()
