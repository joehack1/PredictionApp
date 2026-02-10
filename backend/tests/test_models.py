import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.database import Base
from app.models.models import Team, Match
from app.ml.poisson_model import PoissonModel
from datetime import datetime, timedelta


@pytest.fixture
def test_db():
    """Create in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_teams(test_db: Session):
    """Create sample teams for testing"""
    teams = [
        Team(name="Manchester City", short_code="MCI", external_id=1, elo_rating=1850),
        Team(name="Liverpool", short_code="LIV", external_id=2, elo_rating=1800),
        Team(name="Arsenal", short_code="ARS", external_id=3, elo_rating=1780),
    ]
    for team in teams:
        test_db.add(team)
    test_db.commit()
    return teams


@pytest.fixture
def sample_matches(test_db: Session, sample_teams):
    """Create sample matches for testing"""
    matches = []
    base_date = datetime.utcnow()
    
    for i in range(10):
        match = Match(
            home_team_id=sample_teams[0].id,
            away_team_id=sample_teams[1].id,
            match_date=base_date + timedelta(days=i),
            home_goals=2,
            away_goals=1,
            status="FINISHED"
        )
        matches.append(match)
        test_db.add(match)
    
    test_db.commit()
    return matches


class TestPoissonModel:
    """Test cases for Poisson prediction model"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = PoissonModel()
        assert model.model_name == "POISSON"
        assert not model.is_trained
    
    def test_model_training(self, sample_teams, sample_matches, test_db):
        """Test model parameter estimation"""
        model = PoissonModel()
        model.estimate_parameters(sample_matches, sample_teams)
        
        assert model.is_trained
        assert len(model.home_attack_param) > 0
        assert model.league_home_advantage > 0
    
    def test_match_prediction(self, sample_teams, sample_matches, test_db):
        """Test match outcome prediction"""
        model = PoissonModel()
        model.estimate_parameters(sample_matches, sample_teams)
        
        prediction = model.predict_match(sample_teams[0].id, sample_teams[1].id)
        
        assert "home_win_prob" in prediction
        assert "draw_prob" in prediction
        assert "away_win_prob" in prediction
        assert "predicted_home_score" in prediction
        assert "predicted_away_score" in prediction
        
        # Probabilities should sum to ~1.0
        total_prob = (
            prediction["home_win_prob"] +
            prediction["draw_prob"] +
            prediction["away_win_prob"]
        )
        assert 0.99 <= total_prob <= 1.01
    
    def test_market_predictions(self, sample_teams, sample_matches, test_db):
        """Test additional market predictions"""
        model = PoissonModel()
        model.estimate_parameters(sample_matches, sample_teams)
        
        markets = model.predict_markets(sample_teams[0].id, sample_teams[1].id)
        
        assert "over_2_5_goals" in markets
        assert "btts_yes" in markets
        assert "home_clean_sheet" in markets
        
        # Probabilities should be between 0 and 1
        for prob in markets.values():
            assert 0 <= prob <= 1
    
    def test_prediction_confidence(self, sample_teams, sample_matches, test_db):
        """Test prediction confidence scoring"""
        model = PoissonModel()
        model.estimate_parameters(sample_matches, sample_teams)
        
        prediction = model.predict_match(sample_teams[0].id, sample_teams[1].id)
        
        confidence = max(
            prediction["home_win_prob"],
            prediction["draw_prob"],
            prediction["away_win_prob"]
        )
        
        # Confidence should be between 0 and 1
        assert 0 <= confidence <= 1
        # Overall favorite should have some confidence
        assert confidence > 0.25


class TestDatabaseModels:
    """Test cases for database models"""
    
    def test_create_team(self, test_db):
        """Test team creation"""
        team = Team(
            name="Test Team",
            short_code="TST",
            external_id=999
        )
        test_db.add(team)
        test_db.commit()
        
        retrieved = test_db.query(Team).filter(Team.name == "Test Team").first()
        assert retrieved is not None
        assert retrieved.short_code == "TST"
    
    def test_create_match(self, test_db, sample_teams):
        """Test match creation"""
        match = Match(
            home_team_id=sample_teams[0].id,
            away_team_id=sample_teams[1].id,
            match_date=datetime.utcnow(),
            home_goals=2,
            away_goals=1,
            status="FINISHED"
        )
        test_db.add(match)
        test_db.commit()
        
        retrieved = test_db.query(Match).filter(Match.id == match.id).first()
        assert retrieved is not None
        assert retrieved.home_goals == 2
        assert retrieved.away_goals == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
