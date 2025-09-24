# NFL Mock API Documentation

## Overview

The NFL Mock API provides comprehensive access to football league data including teams, players, games, and schedules. This API uses VCR cassettes to deliver predictable, offline-capable responses perfect for development, testing, and demonstrations.

## Quick Start

### View Interactive Documentation

1. **Swagger UI (Recommended)**: Open `swagger.html` in your browser for interactive API exploration
2. **Swagger/OpenAPI Spec**: View `swagger.yaml` for the complete API specification
3. **Code Examples**: See the Python client examples in `example.py` and `example_nfl_client.py`

### Base URL
```
http://localhost:1339
```

## Available Endpoints

### 🏆 Leagues
- `GET /v1/leagues` - Get all available leagues

### 🏈 Teams  
- `GET /v1/leagues/{league}/teams` - Get all teams in league
- `GET /v1/leagues/{league}/teams/{teamId}` - Get specific team
- `GET /v1/leagues/{league}/teams/{teamId}/players` - Get team players
- `GET /v1/leagues/{league}/teams/{teamId}/games` - Get team games

### 👤 Players
- `GET /v1/leagues/{league}/players` - Get all players (with pagination)
- `GET /v1/leagues/{league}/players/{playerId}` - Get specific player

### 🎮 Games
- `GET /v1/leagues/{league}/games` - Get all games (with date filters)
- `GET /v1/leagues/{league}/games/{gameId}` - Get specific game

## Key Features

### 🎯 **RESTful Design**
All endpoints follow REST conventions with predictable URL patterns and HTTP methods.

### 📊 **Rich Data Models**
- **Teams**: Complete team info with records, colors, and identifiers
- **Players**: Detailed player profiles with positions, stats, and team affiliations
- **Games**: Full game data with schedules, broadcast info, and participating teams
- **Leagues**: League information with sport categorization

### 🔍 **Query Parameters**
- **Pagination**: `cursor` and `per_page` for large datasets
- **Date Filtering**: `from_date` and `to_date` for game queries
- **League Scoping**: All endpoints support league-specific queries

### 📱 **Response Format**
All responses return JSON with consistent structure:
```json
{
  "id": "resource_identifier",
  "name": "Resource Name",
  "...": "additional properties"
}
```

## Example Usage

### Using Python Client
```python
from pulse_mock import NFLMockClient

client = NFLMockClient()

# Get all NFL teams
teams = client.get_teams()
print(f"Found {len(teams)} NFL teams")

# Find specific team
eagles = client.find_team_by_name("Eagles")
print(f"Team: {eagles['market']} {eagles['name']}")

# Get team players
players = client.get_team_players(eagles['id'])
qbs = client.get_players_by_position("QB", eagles['id'])
print(f"Eagles have {len(players)} players, {len(qbs)} QBs")
```

### Direct HTTP Requests
```bash
# Get all leagues
curl http://localhost:1339/v1/leagues

# Get NFL teams
curl http://localhost:1339/v1/leagues/NFL/teams

# Get specific team
curl http://localhost:1339/v1/leagues/NFL/teams/NFL_team_ram7VKb86QoDRToIZOIN8rH

# Get team games with date filter
curl "http://localhost:1339/v1/leagues/NFL/games?from_date=2025-09-05&to_date=2026-01-04"
```

## Data Models

### Team Object
```json
{
  "id": "NFL_team_ram7VKb86QoDRToIZOIN8rH",
  "name": "Eagles",
  "market": "Philadelphia", 
  "abbreviation": "PHI",
  "record": {
    "wins": 2,
    "losses": 0,
    "ties": 0,
    "win_percentage": 100
  },
  "colors": [
    {"hex": "#004c54", "priority": 1},
    {"hex": "#a5acaf", "priority": 2}
  ]
}
```

### Player Object
```json
{
  "id": "NFL_player_SyWsd7T30Oev84KlU0vKvQrU",
  "first_name": "Jalen",
  "last_name": "Hurts",
  "position": "QB",
  "jersey_number": "1",
  "team": {
    "id": "NFL_team_ram7VKb86QoDRToIZOIN8rH",
    "name": "Eagles",
    "market": "Philadelphia"
  }
}
```

### Game Object
```json
{
  "id": "NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8",
  "display_name": "Dallas Cowboys @ Philadelphia Eagles",
  "scheduled_at": "2025-09-05T00:20:00Z",
  "status": "closed",
  "home_team": { "name": "Eagles", "market": "Philadelphia" },
  "away_team": { "name": "Cowboys", "market": "Dallas" }
}
```

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)

Error responses include descriptive messages:
```json
{
  "error": "Resource not found",
  "message": "The requested team could not be found"
}
```

## Integration Examples

### Testing
```python
import unittest
from pulse_mock import NFLMockClient

class TestNFLAPI(unittest.TestCase):
    def setUp(self):
        self.client = NFLMockClient()
    
    def test_get_teams(self):
        teams = self.client.get_teams()
        self.assertGreater(len(teams), 0)
        self.assertIn('Eagles', [t['name'] for t in teams])
```

### Development
```python
# Replace real API calls with mock client
# Real API: response = requests.get('https://api.nfl.com/teams')
# Mock API: 
client = NFLMockClient()
teams = client.get_teams()  # Same data structure, predictable responses
```

## File Structure

- `swagger.yaml` - Complete OpenAPI 3.0 specification
- `swagger.html` - Interactive Swagger UI documentation
- `pulse_mock/cassettes/` - VCR cassette files with recorded responses
- `example_nfl_client.py` - Comprehensive usage examples

## Next Steps

1. **Explore the API**: Open `swagger.html` to interactively explore all endpoints
2. **Try the Python Client**: Run `python example_nfl_client.py` to see the API in action
3. **Integration**: Use the mock client in your applications for reliable, offline testing
4. **Customization**: Add your own VCR cassettes for additional endpoints or data

---

For more information, see the [README.md](README.md) and the complete [Swagger specification](swagger.yaml).
