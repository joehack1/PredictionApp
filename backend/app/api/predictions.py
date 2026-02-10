from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.config.database import get_db
from app.schemas.schemas import PredictionResponse
from app.services.database_service import MatchService, PredictionService, TeamService
from app.ml.poisson_model import PoissonModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])

# Global model instance (in production, use model registry)
poisson_model = None


async def get_poisson_model(db: Session = Depends(get_db)):
    """Get or initialize Poisson model"""
    global poisson_model
    
    if poisson_model is None or not poisson_model.is_trained:
        poisson_model = PoissonModel()
        
        # Get teams and recent matches for training
        teams = TeamService.get_all_teams(db)
        recent_matches = MatchService.get_recent_matches(db, days_back=365, limit=1000)
        
        # Train model
        poisson_model.estimate_parameters(recent_matches, teams)
        logger.info("Poisson model trained")
    
    return poisson_model


@router.post("/match/{match_id}")
async def predict_match(
    match_id: int,
    db: Session = Depends(get_db),
    model: PoissonModel = Depends(get_poisson_model)
) -> Dict[str, Any]:
    """Predict outcome for a specific match"""
    
    match = MatchService.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get existing prediction or create new one
    existing_prediction = PredictionService.get_latest_prediction(db, match_id, "POISSON")
    if existing_prediction:
        return {
            "match_id": match_id,
            "home_team": match.home_team.name,
            "away_team": match.away_team.name,
            "prediction": {
                "home_win_prob": existing_prediction.home_win_prob,
                "draw_prob": existing_prediction.draw_prob,
                "away_win_prob": existing_prediction.away_win_prob,
                "predicted_home_score": existing_prediction.predicted_home_score,
                "predicted_away_score": existing_prediction.predicted_away_score,
                "most_likely_score": existing_prediction.most_likely_score,
            }
        }
    
    # Generate new prediction
    prediction_data = model.predict_match(match.home_team_id, match.away_team_id)
    market_data = model.predict_markets(match.home_team_id, match.away_team_id)
    
    # Calculate confidence
    confidence = max(
        prediction_data["home_win_prob"],
        prediction_data["draw_prob"],
        prediction_data["away_win_prob"]
    )
    
    # Save to database
    from app.schemas.schemas import PredictionCreate
    pred_create = PredictionCreate(
        match_id=match_id,
        model_type="POISSON",
        home_win_prob=prediction_data["home_win_prob"],
        draw_prob=prediction_data["draw_prob"],
        away_win_prob=prediction_data["away_win_prob"],
        predicted_home_score=prediction_data["predicted_home_score"],
        predicted_away_score=prediction_data["predicted_away_score"],
        most_likely_score=prediction_data["most_likely_score"],
        confidence_score=confidence,
        **market_data
    )
    
    db_pred = PredictionService.create_prediction(db, pred_create)
    
    return {
        "match_id": match_id,
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "prediction": {
            "home_win_prob": db_pred.home_win_prob,
            "draw_prob": db_pred.draw_prob,
            "away_win_prob": db_pred.away_win_prob,
            "predicted_home_score": db_pred.predicted_home_score,
            "predicted_away_score": db_pred.predicted_away_score,
            "most_likely_score": db_pred.most_likely_score,
            "confidence": db_pred.confidence_score,
            "over_2_5_goals": db_pred.over_2_5_goals,
            "btts": db_pred.btts_yes,
            "clean_sheet_home": db_pred.home_clean_sheet,
        }
    }


@router.post("/batch")
async def predict_batch(
    days_ahead: int = 10,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    model: PoissonModel = Depends(get_poisson_model)
) -> Dict[str, Any]:
    """Predict all upcoming matches for next N days"""
    
    matches = MatchService.get_upcoming_matches(db, days_ahead=days_ahead, limit=100)
    
    predictions = []
    for match in matches:
        try:
            prediction_data = model.predict_match(match.home_team_id, match.away_team_id)
            market_data = model.predict_markets(match.home_team_id, match.away_team_id)
            
            confidence = max(
                prediction_data["home_win_prob"],
                prediction_data["draw_prob"],
                prediction_data["away_win_prob"]
            )
            
            from app.schemas.schemas import PredictionCreate
            pred_create = PredictionCreate(
                match_id=match.id,
                model_type="POISSON",
                home_win_prob=prediction_data["home_win_prob"],
                draw_prob=prediction_data["draw_prob"],
                away_win_prob=prediction_data["away_win_prob"],
                predicted_home_score=prediction_data["predicted_home_score"],
                predicted_away_score=prediction_data["predicted_away_score"],
                most_likely_score=prediction_data["most_likely_score"],
                confidence_score=confidence,
                **market_data
            )
            
            db_pred = PredictionService.create_prediction(db, pred_create)
            
            predictions.append({
                "match_id": match.id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "predicted_score": db_pred.most_likely_score,
                "confidence": db_pred.confidence_score
            })
        except Exception as e:
            logger.error(f"Error predicting match {match.id}: {e}")
            continue
    
    return {
        "predictions_count": len(predictions),
        "predictions": predictions
    }


@router.get("/match/{match_id}/detailed")
async def get_detailed_prediction(
    match_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed prediction for a match with all markets"""
    
    match = MatchService.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    prediction = PredictionService.get_latest_prediction(db, match_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction found for this match")
    
    return {
        "match_id": match.id,
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "match_date": match.match_date,
        "prediction": {
            "model_type": prediction.model_type,
            "outcomes": {
                "home_win": round(prediction.home_win_prob, 4),
                "draw": round(prediction.draw_prob, 4),
                "away_win": round(prediction.away_win_prob, 4),
            },
            "score_prediction": {
                "predicted_home": round(prediction.predicted_home_score, 2),
                "predicted_away": round(prediction.predicted_away_score, 2),
                "most_likely": prediction.most_likely_score,
            },
            "markets": {
                "over_2_5_goals": round(prediction.over_2_5_goals, 4) if prediction.over_2_5_goals else None,
                "under_2_5_goals": round(prediction.under_2_5_goals, 4) if prediction.under_2_5_goals else None,
                "both_teams_to_score": round(prediction.btts_yes, 4) if prediction.btts_yes else None,
                "home_clean_sheet": round(prediction.home_clean_sheet, 4) if prediction.home_clean_sheet else None,
                "away_clean_sheet": round(prediction.away_clean_sheet, 4) if prediction.away_clean_sheet else None,
            },
            "confidence": round(prediction.confidence_score, 4),
            "created_at": prediction.created_at,
        }
    }
