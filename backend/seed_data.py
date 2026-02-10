#!/usr/bin/env python3
"""
Seed the database with sample Premier League data for development
"""
from datetime import datetime, timedelta
from app.config.database import SessionLocal, Base, engine
from app.models.models import Team, Match, Prediction
import sys

def seed_database():
    """Create sample teams and matches"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_teams = db.query(Team).count()
        if existing_teams > 0:
            print("Database already seeded. Skipping...")
            return
        
        # Create Premier League teams (actual teams)
        teams_data = [
            {"external_id": 64, "name": "Manchester City", "short_code": "MCI"},
            {"external_id": 65, "name": "Manchester United", "short_code": "MUN"},
            {"external_id": 66, "name": "Liverpool", "short_code": "LIV"},
            {"external_id": 67, "name": "Chelsea", "short_code": "CHE"},
            {"external_id": 68, "name": "Arsenal", "short_code": "ARS"},
            {"external_id": 70, "name": "Tottenham Hotspur", "short_code": "TOT"},
            {"external_id": 71, "name": "Newcastle United", "short_code": "NEW"},
            {"external_id": 73, "name": "Brighton and Hove Albion", "short_code": "BHA"},
            {"external_id": 74, "name": "Aston Villa", "short_code": "AVL"},
            {"external_id": 75, "name": "Fulham", "short_code": "FUL"},
            {"external_id": 76, "name": "Brentford", "short_code": "BRE"},
            {"external_id": 77, "name": "West Ham United", "short_code": "WHU"},
            {"external_id": 78, "name": "Everton", "short_code": "EVE"},
            {"external_id": 79, "name": "Leicester City", "short_code": "LEI"},
            {"external_id": 80, "name": "Crystal Palace", "short_code": "CRY"},
        ]
        
        teams = []
        for team_data in teams_data:
            team = Team(**team_data)
            teams.append(team)
            db.add(team)
        
        db.commit()
        print(f"Created {len(teams)} teams")
        
        # Create sample matches
        match_data = [
            {
                "external_id": 401547001,
                "home_team_id": teams[0].id,  # Man City
                "away_team_id": teams[2].id,  # Liverpool
                "match_date": datetime.now() + timedelta(days=1),
                "venue": "Etihad Stadium",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547002,
                "home_team_id": teams[1].id,  # Man United
                "away_team_id": teams[4].id,  # Arsenal
                "match_date": datetime.now() + timedelta(days=2),
                "venue": "Old Trafford",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547003,
                "home_team_id": teams[3].id,  # Chelsea
                "away_team_id": teams[5].id,  # Tottenham
                "match_date": datetime.now() + timedelta(days=3),
                "venue": "Stamford Bridge",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547004,
                "home_team_id": teams[6].id,  # Newcastle
                "away_team_id": teams[7].id,  # Brighton
                "match_date": datetime.now() + timedelta(days=4),
                "venue": "St. James' Park",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547005,
                "home_team_id": teams[8].id,  # Aston Villa
                "away_team_id": teams[9].id,  # Fulham
                "match_date": datetime.now() + timedelta(days=5),
                "venue": "Villa Park",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547006,
                "home_team_id": teams[10].id,  # Brentford
                "away_team_id": teams[11].id,  # West Ham
                "match_date": datetime.now() + timedelta(days=6),
                "venue": "Gtech Community Stadium",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547007,
                "home_team_id": teams[0].id,  # Man City
                "away_team_id": teams[4].id,  # Arsenal
                "match_date": datetime.now() + timedelta(days=7),
                "venue": "Etihad Stadium",
                "status": "SCHEDULED"
            },
            {
                "external_id": 401547008,
                "home_team_id": teams[2].id,  # Liverpool
                "away_team_id": teams[1].id,  # Man United
                "match_date": datetime.now() + timedelta(days=8),
                "venue": "Anfield",
                "status": "SCHEDULED"
            },
        ]
        
        matches = []
        for md in match_data:
            match = Match(**md)
            matches.append(match)
            db.add(match)
        
        db.commit()
        print(f"Created {len(matches)} matches")
        
        # Create sample predictions
        prediction_data = [
            {
                "match_id": matches[0].id,
                "model_type": "ENSEMBLE",
                "home_win_prob": 0.55,
                "draw_prob": 0.25,
                "away_win_prob": 0.20,
                "predicted_home_score": 2.1,
                "predicted_away_score": 0.9,
                "most_likely_score": "2-1",
                "over_2_5_goals": 0.60,
                "under_2_5_goals": 0.40,
                "btts_yes": 0.35,
                "btts_no": 0.65,
                "home_clean_sheet": 0.45,
                "away_clean_sheet": 0.25,
                "confidence_score": 0.82
            },
            {
                "match_id": matches[1].id,
                "model_type": "ENSEMBLE",
                "home_win_prob": 0.45,
                "draw_prob": 0.30,
                "away_win_prob": 0.25,
                "predicted_home_score": 1.0,
                "predicted_away_score": 1.0,
                "most_likely_score": "1-1",
                "over_2_5_goals": 0.40,
                "under_2_5_goals": 0.60,
                "btts_yes": 0.55,
                "btts_no": 0.45,
                "home_clean_sheet": 0.30,
                "away_clean_sheet": 0.30,
                "confidence_score": 0.75
            },
            {
                "match_id": matches[2].id,
                "model_type": "ENSEMBLE",
                "home_win_prob": 0.50,
                "draw_prob": 0.25,
                "away_win_prob": 0.25,
                "predicted_home_score": 1.8,
                "predicted_away_score": 1.7,
                "most_likely_score": "2-2",
                "over_2_5_goals": 0.75,
                "under_2_5_goals": 0.25,
                "btts_yes": 0.80,
                "btts_no": 0.20,
                "home_clean_sheet": 0.20,
                "away_clean_sheet": 0.20,
                "confidence_score": 0.78
            },
        ]
        
        predictions = []
        for pd in prediction_data:
            prediction = Prediction(**pd)
            predictions.append(prediction)
            db.add(prediction)
        
        db.commit()
        print(f"Created {len(predictions)} predictions")
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
