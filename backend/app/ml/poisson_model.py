import numpy as np
from scipy.stats import poisson
from typing import Tuple, Dict
import pickle
import os


class PoissonModel:
    """
    Poisson Regression Model for Premier League match predictions.
    Uses observed scoring patterns to predict match outcomes.
    """
    
    def __init__(self):
        self.model_name = "POISSON"
        self.is_trained = False
        self.home_attack_param = {}  # team_id -> attack strength
        self.home_defense_param = {}  # team_id -> defense strength
        self.away_attack_param = {}
        self.away_defense_param = {}
        self.league_home_advantage = 1.0
        self.league_avg_goals = 2.8
        
    def estimate_parameters(self, matches: list, teams: list) -> None:
        """
        Estimate Poisson parameters from historical match data.
        
        Args:
            matches: List of match results with home_goals, away_goals, home_team_id, away_team_id
            teams: List of team objects with statistics
        """
        self.home_attack_param = {team.id: team.avg_goals_scored * 0.5 + 0.75 for team in teams}
        self.home_defense_param = {team.id: team.avg_goals_conceded * 0.5 + 0.75 for team in teams}
        self.away_attack_param = {team.id: team.avg_goals_scored * 0.4 + 0.6 for team in teams}
        self.away_defense_param = {team.id: team.avg_goals_conceded * 0.4 + 0.6 for team in teams}
        
        # Calculate home advantage based on goal difference
        if matches:
            home_goals = sum(m.home_goals for m in matches if m.home_goals is not None)
            away_goals = sum(m.away_goals for m in matches if m.away_goals is not None)
            match_count = sum(1 for m in matches if m.home_goals is not None)
            if match_count > 0:
                self.league_home_advantage = home_goals / match_count
                self.league_avg_goals = (home_goals + away_goals) / (2 * match_count)
        
        self.is_trained = True
    
    def predict_match(self, home_team_id: int, away_team_id: int) -> Dict:
        """
        Predict match outcome using Poisson distribution.
        
        Args:
            home_team_id: ID of home team
            away_team_id: ID of away team
            
        Returns:
            Dictionary with prediction probabilities for all outcomes
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Calculate expected goals
        home_attack = self.home_attack_param.get(home_team_id, 1.0)
        home_defense = self.home_defense_param.get(home_team_id, 1.0)
        away_attack = self.away_attack_param.get(away_team_id, 1.0)
        away_defense = self.away_defense_param.get(away_team_id, 1.0)
        
        # Expected goals based on Poisson model
        lambda_home = home_attack * away_defense * self.league_home_advantage
        lambda_away = away_attack * home_defense
        
        # Normalize to league average
        lambda_home = max(0.1, min(lambda_home, 4.5))
        lambda_away = max(0.1, min(lambda_away, 4.5))
        
        predictions = {
            "predicted_home_score": lambda_home,
            "predicted_away_score": lambda_away,
            "home_win_prob": 0.0,
            "draw_prob": 0.0,
            "away_win_prob": 0.0,
            "most_likely_score": "0-0",
            "all_scores": {},
        }
        
        # Calculate probabilities for all possible scorelines (0-4 goals each team)
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        max_score_prob = 0.0
        most_likely_score = (0, 0)
        
        for home_goals in range(5):
            for away_goals in range(5):
                # Poisson probability
                prob = (
                    poisson.pmf(home_goals, lambda_home) *
                    poisson.pmf(away_goals, lambda_away)
                )
                predictions["all_scores"][f"{home_goals}-{away_goals}"] = float(prob)
                
                # Track most likely score
                if prob > max_score_prob:
                    max_score_prob = prob
                    most_likely_score = (home_goals, away_goals)
                
                # Accumulate outcome probabilities
                if home_goals > away_goals:
                    home_win_prob += prob
                elif home_goals == away_goals:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # Normalize to ensure probabilities sum to 1
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        
        predictions["home_win_prob"] = float(home_win_prob)
        predictions["draw_prob"] = float(draw_prob)
        predictions["away_win_prob"] = float(away_win_prob)
        predictions["most_likely_score"] = f"{most_likely_score[0]}-{most_likely_score[1]}"
        
        return predictions
    
    def predict_markets(self, home_team_id: int, away_team_id: int) -> Dict:
        """
        Predict additional betting markets using Poisson distribution.
        
        Args:
            home_team_id: ID of home team
            away_team_id: ID of away team
            
        Returns:
            Dictionary with market predictions
        """
        predictions = self.predict_match(home_team_id, away_team_id)
        lambda_home = predictions["predicted_home_score"]
        lambda_away = predictions["predicted_away_score"]
        
        # Over/Under 2.5 goals
        over_2_5 = 0.0
        under_2_5 = 0.0
        btts_yes = 0.0
        btts_no = 0.0
        home_clean_sheet = 0.0
        away_clean_sheet = 0.0
        
        for home_goals in range(5):
            for away_goals in range(5):
                prob = (
                    poisson.pmf(home_goals, lambda_home) *
                    poisson.pmf(away_goals, lambda_away)
                )
                
                total_goals = home_goals + away_goals
                if total_goals > 2.5:
                    over_2_5 += prob
                else:
                    under_2_5 += prob
                
                if home_goals > 0 and away_goals > 0:
                    btts_yes += prob
                
                if home_goals == 0 or away_goals == 0:
                    btts_no += prob
                
                if away_goals == 0:
                    home_clean_sheet += prob
                
                if home_goals == 0:
                    away_clean_sheet += prob
        
        return {
            "over_2_5_goals": float(over_2_5),
            "under_2_5_goals": float(under_2_5),
            "btts_yes": float(btts_yes),
            "btts_no": float(btts_no),
            "home_clean_sheet": float(home_clean_sheet),
            "away_clean_sheet": float(away_clean_sheet),
        }
    
    def save_model(self, filepath: str) -> None:
        """Save model to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load_model(filepath: str):
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
