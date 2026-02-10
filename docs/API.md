# API Documentation - Premier League Analyst Pro

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, public endpoints do not require authentication. Auth will be implemented in Phase 2.

---

## Teams Endpoints

### List All Teams
```
GET /teams
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Manchester City",
    "short_code": "MCI",
    "external_id": 333,
    "crest_url": "https://...",
    "matches_played": 20,
    "wins": 16,
    "draws": 3,
    "losses": 1,
    "goals_for": 65,
    "goals_against": 15,
    "avg_goals_scored": 3.25,
    "avg_goals_conceded": 0.75,
    "win_rate": 0.8,
    "elo_rating": 1850
  }
]
```

### Get Team Details
```
GET /teams/{team_id}
```

**Parameters:**
- `team_id` (integer, required): Team ID

**Response:** Single team object (see above)

### Get Team Form
```
GET /teams/{team_id}/form?matches=5
```

**Parameters:**
- `team_id` (integer, required): Team ID
- `matches` (integer, optional, default: 5, max: 20): Number of recent matches

**Response:**
```json
{
  "team_id": 1,
  "team_name": "Manchester City",
  "matches": [
    {
      "match_id": 100,
      "date": "2024-02-03T15:00:00",
      "opponent": "Liverpool",
      "score": "3-1",
      "result": "WIN",
      "venue": "Home"
    }
  ],
  "statistics": {
    "matches_played": 5,
    "wins": 4,
    "draws": 1,
    "losses": 0,
    "goals_for": 14,
    "goals_against": 3
  }
}
```

---

## Matches Endpoints

### Get Upcoming Matches
```
GET /matches/upcoming?limit=10&days_ahead=10&detailed=false
```

**Parameters:**
- `limit` (integer, optional, default: 10, max: 50): Number of matches
- `days_ahead` (integer, optional, default: 10, max: 30): Days to look ahead
- `detailed` (boolean, optional, default: false): Include detailed stats

**Response:**
```json
[
  {
    "id": 100,
    "home_team": {
      "id": 1,
      "name": "Manchester City",
      "short_code": "MCI"
    },
    "away_team": {
      "id": 2,
      "name": "Liverpool",
      "short_code": "LIV"
    },
    "match_date": "2024-02-10T15:00:00",
    "status": "SCHEDULED",
    "venue": "Etihad Stadium",
    "home_goals": null,
    "away_goals": null
  }
]
```

### Get Recent Matches
```
GET /matches/recent?limit=10&days_back=30
```

**Parameters:**
- `limit` (integer, optional, default: 10, max: 50)
- `days_back` (integer, optional, default: 30, max: 365)

**Response:** Array of completed matches (same structure as upcoming)

### Get Match Details
```
GET /matches/{match_id}
```

**Parameters:**
- `match_id` (integer, required): Match ID

**Response:**
```json
{
  "id": 100,
  "home_team": { ... },
  "away_team": { ... },
  "match_date": "2024-02-10T15:00:00",
  "status": "SCHEDULED",
  "venue": "Etihad Stadium",
  "home_goals": null,
  "away_goals": null,
  "predictions": [
    {
      "id": 1,
      "match_id": 100,
      "model_type": "POISSON",
      "home_win_prob": 0.65,
      "draw_prob": 0.20,
      "away_win_prob": 0.15,
      "most_likely_score": "2-0"
    }
  ]
}
```

### Get Head-to-Head
```
GET /matches/{match_id}/head-to-head?limit=10
```

**Parameters:**
- `match_id` (integer, required): Match ID
- `limit` (integer, optional, default: 10, max: 30): Historical matches to return

**Response:**
```json
{
  "home_team": "Manchester City",
  "away_team": "Liverpool",
  "statistics": {
    "Manchester City_wins": 6,
    "Liverpool_wins": 3,
    "draws": 2,
    "total_matches": 11
  },
  "recent_matches": [ ... ]
}
```

---

## Predictions Endpoints

### Predict Single Match
```
POST /predict/match/{match_id}
```

**Parameters:**
- `match_id` (integer, required): Match ID

**Response:**
```json
{
  "match_id": 100,
  "home_team": "Manchester City",
  "away_team": "Liverpool",
  "prediction": {
    "home_win_prob": 0.65,
    "draw_prob": 0.20,
    "away_win_prob": 0.15,
    "predicted_home_score": 2.1,
    "predicted_away_score": 0.8,
    "most_likely_score": "2-0",
    "confidence": 0.65,
    "over_2_5_goals": 0.58,
    "btts": 0.35,
    "clean_sheet_home": 0.42
  }
}
```

### Predict All Upcoming Matches
```
POST /predict/batch?days_ahead=10
```

**Parameters:**
- `days_ahead` (integer, optional, default: 10): Days to predict ahead

**Response:**
```json
{
  "predictions_count": 10,
  "predictions": [
    {
      "match_id": 100,
      "home_team": "Manchester City",
      "away_team": "Liverpool",
      "predicted_score": "2-0",
      "confidence": 0.65
    }
  ]
}
```

### Get Detailed Prediction
```
GET /predict/match/{match_id}/detailed
```

**Parameters:**
- `match_id` (integer, required): Match ID

**Response:**
```json
{
  "match_id": 100,
  "home_team": "Manchester City",
  "away_team": "Liverpool",
  "match_date": "2024-02-10T15:00:00",
  "prediction": {
    "model_type": "POISSON",
    "outcomes": {
      "home_win": 0.6500,
      "draw": 0.2000,
      "away_win": 0.1500
    },
    "score_prediction": {
      "predicted_home": 2.10,
      "predicted_away": 0.80,
      "most_likely": "2-0"
    },
    "markets": {
      "over_2_5_goals": 0.5800,
      "under_2_5_goals": 0.4200,
      "both_teams_to_score": 0.3500,
      "home_clean_sheet": 0.4200,
      "away_clean_sheet": 0.7800
    },
    "confidence": 0.6500,
    "created_at": "2024-02-04T10:30:00"
  }
}
```

---

## System Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### API Root
```
GET /
```

**Response:**
```json
{
  "message": "Premier League Analyst Pro API",
  "version": "0.1.0",
  "docs": "/docs",
  "status": "online"
}
```

### API Info
```
GET /api/v1
```

**Response:**
```json
{
  "version": "1.0.0",
  "endpoints": {
    "teams": "/api/v1/teams",
    "matches": "/api/v1/matches",
    "predictions": "/api/v1/predict"
  }
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Match not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting. Will be implemented in production:
- 1000 requests / hour per IP
- 10000 requests / hour per API key

---

## Best Practices

1. **Cache Results**: Predictions are cached for 1 hour
2. **Batch Requests**: Use `/predict/batch` for multiple matches
3. **Pagination**: Use `limit` parameter to reduce response size
4. **Error Handling**: Check HTTP status codes and error details
5. **Headers**: All responses include standard HTTP headers

---

## Example Workflow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Get upcoming matches
matches = requests.get(f"{BASE_URL}/matches/upcoming?limit=5").json()

# 2. For each match, get prediction
for match in matches:
    prediction = requests.post(
        f"{BASE_URL}/predict/match/{match['id']}"
    ).json()
    
    print(f"{match['home_team']['name']} vs {match['away_team']['name']}")
    print(f"Prediction: {prediction['prediction']['most_likely_score']}")
    print(f"Confidence: {prediction['prediction']['confidence']}")

# 3. Get head-to-head history
h2h = requests.get(
    f"{BASE_URL}/matches/{matches[0]['id']}/head-to-head?limit=5"
).json()

print(f"Head-to-head record: {h2h['statistics']}")
```

---

**Last Updated**: February 10, 2026
**API Version**: 1.0
**Status**: MVP
