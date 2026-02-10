from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.football_data_service import FootballDataService
from app.services.database_service import TeamService, MatchService
from app.models.models import Match
from app.schemas.schemas import MatchCreate
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for syncing data from football-data.org"""
    
    def __init__(self, db: Session, football_data_service: FootballDataService):
        self.db = db
        self.api = football_data_service
    
    async def sync_teams(self) -> int:
        """Sync Premier League teams from API"""
        try:
            teams_data = await self.api.get_league_standings()
            
            if not teams_data or "standings" not in teams_data:
                logger.warning("No standings data from API")
                return 0
            
            synced_count = 0
            for standings in teams_data.get("standings", []):
                for table_entry in standings.get("table", []):
                    team_data = table_entry.get("team", {})
                    external_id = team_data.get("id")
                    name = team_data.get("name")
                    
                    if not external_id or not name:
                        continue
                    
                    # Check if team exists
                    existing_team = self.db.query(Match).filter(
                        Match.external_id == external_id
                    ).first()
                    
                    if not existing_team:
                        team = TeamService.create_team(
                            self.db,
                            name=name,
                            short_code=team_data.get("tla", name[:3]),
                            external_id=external_id
                        )
                        synced_count += 1
                    else:
                        # Update stats
                        TeamService.update_team_stats(
                            self.db,
                            existing_team.id,
                            wins=table_entry.get("won", 0),
                            draws=table_entry.get("draw", 0),
                            losses=table_entry.get("lost", 0),
                            goals_for=table_entry.get("goalsFor", 0),
                            goals_against=table_entry.get("goalsAgainst", 0),
                            matches_played=table_entry.get("playedGames", 0)
                        )
                        synced_count += 1
            
            logger.info(f"Synced {synced_count} teams")
            return synced_count
        
        except Exception as e:
            logger.error(f"Error syncing teams: {e}")
            return 0
    
    async def sync_upcoming_matches(self, days_ahead: int = 14) -> int:
        """Sync upcoming matches from API"""
        try:
            matches_data = await self.api.get_league_matches(days_ahead=days_ahead)
            
            if not matches_data or "matches" not in matches_data:
                logger.warning("No matches data from API")
                return 0
            
            synced_count = 0
            for match_data in matches_data.get("matches", []):
                external_id = match_data.get("id")
                
                # Check if match already exists
                existing = self.db.query(Match).filter(
                    Match.external_id == external_id
                ).first()
                
                if existing:
                    continue
                
                # Get or create teams
                home_team_data = match_data.get("homeTeam", {})
                away_team_data = match_data.get("awayTeam", {})
                
                home_team = self._get_or_create_team(home_team_data)
                away_team = self._get_or_create_team(away_team_data)
                
                if not home_team or not away_team:
                    continue
                
                # Create match
                match_date = datetime.fromisoformat(
                    match_data.get("utcDate", "").replace("Z", "+00:00")
                )
                
                match_create = MatchCreate(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    external_id=external_id,
                    venue=match_data.get("venue")
                )
                
                MatchService.create_match(self.db, match_create)
                synced_count += 1
            
            logger.info(f"Synced {synced_count} upcoming matches")
            return synced_count
        
        except Exception as e:
            logger.error(f"Error syncing matches: {e}")
            return 0
    
    async def sync_match_results(self, days_back: int = 30) -> int:
        """Sync completed match results"""
        try:
            from_date = (datetime.utcnow() - timedelta(days=days_back)).date()
            to_date = datetime.utcnow().date()
            
            matches_data = await self.api.get_league_matches()
            
            if not matches_data or "matches" not in matches_data:
                return 0
            
            synced_count = 0
            for match_data in matches_data.get("matches", []):
                if match_data.get("status") != "FINISHED":
                    continue
                
                external_id = match_data.get("id")
                
                # Find match in DB
                match = self.db.query(Match).filter(
                    Match.external_id == external_id
                ).first()
                
                if not match:
                    continue
                
                # Update result if not already set
                if match.home_goals is None:
                    result = match_data.get("score", {})
                    home_goals = result.get("fullTime", {}).get("home")
                    away_goals = result.get("fullTime", {}).get("away")
                    
                    if home_goals is not None and away_goals is not None:
                        MatchService.update_match(
                            self.db,
                            match.id,
                            from pydantic import BaseModel
                            class Update:
                                home_goals = home_goals
                                away_goals = away_goals
                                status = "FINISHED"
                        )
                        synced_count += 1
            
            logger.info(f"Synced {synced_count} match results")
            return synced_count
        
        except Exception as e:
            logger.error(f"Error syncing results: {e}")
            return 0
    
    def _get_or_create_team(self, team_data: Dict[str, Any]):
        """Get or create a team from API data"""
        external_id = team_data.get("id")
        name = team_data.get("name")
        
        if not external_id or not name:
            return None
        
        existing = self.db.query(Match).filter(
            Match.external_id == external_id
        ).first()
        
        if existing:
            return existing
        
        return TeamService.create_team(
            self.db,
            name=name,
            short_code=team_data.get("tla", name[:3]),
            external_id=external_id
        )
