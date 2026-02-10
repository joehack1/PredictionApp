from typing import Optional, Dict, Any
import httpx
from datetime import datetime, timedelta
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class FootballDataService:
    """Service for integrating with football-data.org API"""
    
    def __init__(self):
        self.base_url = settings.football_data_base_url
        self.api_key = settings.football_data_api_key
        self.headers = {
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json"
        }
        self.client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(headers=self.headers)
        return self.client
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
    
    async def get_league_matches(self, league_id: int = 2790, days_ahead: Optional[int] = None) -> Dict[str, Any]:
        """
        Get upcoming Premier League matches.
        
        Args:
            league_id: Football-data.org competition ID (2790 for Premier League)
            days_ahead: Number of days ahead to fetch (None = next 10)
            
        Returns:
            Dictionary with match data
        """
        try:
            client = await self.get_client()
            params = {}
            
            if days_ahead:
                date_from = datetime.utcnow().date()
                date_to = (datetime.utcnow() + timedelta(days=days_ahead)).date()
                params["dateFrom"] = date_from.isoformat()
                params["dateTo"] = date_to.isoformat()
            
            response = await client.get(
                f"{self.base_url}/competitions/{league_id}/matches",
                params=params
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error fetching matches: {e}")
            return {"matches": []}
        except Exception as e:
            logger.error(f"Error fetching matches: {e}")
            return {"matches": []}
    
    async def get_team_data(self, team_id: int) -> Dict[str, Any]:
        """
        Get detailed team information and statistics.
        
        Args:
            team_id: Football-data.org team ID
            
        Returns:
            Team data dictionary
        """
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/teams/{team_id}")
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching team data for {team_id}: {e}")
            return {}
    
    async def get_league_standings(self, league_id: int = 2790) -> Dict[str, Any]:
        """
        Get current league standings.
        
        Args:
            league_id: Football-data.org competition ID
            
        Returns:
            Standings data
        """
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/competitions/{league_id}/standings")
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            return {}
    
    async def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific match.
        
        Args:
            match_id: Football-data.org match ID
            
        Returns:
            Match details dictionary
        """
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/matches/{match_id}")
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching match {match_id}: {e}")
            return {}
    
    async def get_team_matches(self, team_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent matches for a specific team.
        
        Args:
            team_id: Football-data.org team ID
            limit: Number of matches to fetch
            
        Returns:
            Team matches dictionary
        """
        try:
            client = await self.get_client()
            response = await client.get(
                f"{self.base_url}/teams/{team_id}/matches",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching team matches for {team_id}: {e}")
            return {}
