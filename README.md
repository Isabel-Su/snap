# Pulse Mock API Client

A Python package for creating mock API clients using VCR cassettes that works transparently like a real REST API. Perfect for testing, development, and demos when you need predictable API responses without making real HTTP requests.

## Features

- 🎯 **Transparent API**: Works exactly like a real REST API - no manual cassette loading required
- 📼 **Automatic VCR Management**: Uses standard VCR YAML format with automatic discovery and loading
- 🚀 **Zero-Config Experience**: Just make HTTP requests - cassettes are loaded behind the scenes
- 🔍 **Smart Matching**: Automatically matches requests by method and URL with on-demand cassette loading
- 🏈 **Specialized Clients**: Built-in NFLMockClient with convenient methods for sports data
- 🌐 **REST Server**: Lightweight Flask server exposes all functionality via HTTP endpoints
- 🛡️ **Error Handling**: Clear error messages for missing cassettes and unmatched requests
- 📦 **Lightweight**: Minimal dependencies (PyYAML + Flask for server)
- ⚠️ **Sample Data**: Includes comprehensive NFL lists but detailed data for specific entities only

## Installation

```bash
pip install pulse-mock
```

Or for development:

```bash
git clone https://github.com/yourusername/pulse-mock.git
cd pulse-mock
pip install -e .
```

## Quick Start

### 1. Basic Usage - Transparent API Experience

```python
from pulse_mock import MockAPIClient

# Initialize the client - that's it! No manual cassette loading required
client = MockAPIClient()

# Make requests just like you would with any REST API
# Cassettes are automatically discovered and loaded as needed
response = client.get('http://localhost:1339/v1/leagues/NFL/games/NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8')

# Access response data normally
print(response.status_code)  # 200
print(response.json())       # {'id': 'NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8', ...}

# Make another request - appropriate cassettes loaded automatically
teams_response = client.get('http://localhost:1339/v1/leagues/NFL/teams')
print(f"Found {len(teams_response.json())} teams")  # Found 32 teams
```

> **📝 Note**: The included cassettes have comprehensive list data (teams, players, games) but detailed entity data for only specific items (like Philadelphia Eagles). See the "Data Availability & Limitations" section for full details.

### 2. NFL Mock Client - High-Level Sports API

```python
from pulse_mock import NFLMockClient

# Specialized client with convenient methods for NFL data
client = NFLMockClient()

# Get all leagues
leagues = client.get_leagues()
print(f"Available leagues: {[league['name'] for league in leagues]}")

# Get NFL teams
teams = client.get_teams()
print(f"NFL has {len(teams)} teams")

# Find a specific team
eagles = client.find_team_by_name("Eagles")
print(f"Found: {eagles['market']} {eagles['name']}")

# Get team players
players = client.get_team_players(eagles['id'])
print(f"Eagles have {len(players)} players")

# Get quarterbacks only
qbs = client.get_players_by_position("QB", eagles['id'])
print(f"Eagles quarterbacks: {[f\"{p['first_name']} {p['last_name']}\" for p in qbs]}")
```

> **⚠️ Note**: In this example, `find_team_by_name("Eagles")` works because team search uses the comprehensive teams list, but `get_team_players(eagles['id'])` only works for Philadelphia Eagles specifically, as detailed roster data is limited to this team in the included cassettes.

### 3. Auto-Loading Options

```python
from pulse_mock import MockAPIClient

# Option 1: Lazy loading (default) - cassettes loaded on-demand
client = MockAPIClient()

# Option 2: Eager loading - all cassettes loaded at startup
client = MockAPIClient(auto_load_all=True)

# Option 3: Custom cassette directory
client = MockAPIClient(cassette_dir='./my_cassettes')
```

### 4. Different HTTP Methods

```python
# All HTTP methods work transparently - no cassette loading required
client = MockAPIClient()

# Supports all standard HTTP methods
get_response = client.get('http://api.example.com/resource')
post_response = client.post('http://api.example.com/resource', headers={'Content-Type': 'application/json'})
put_response = client.put('http://api.example.com/resource/123')
delete_response = client.delete('http://api.example.com/resource/123')
```

### 5. Using in Tests

```python
import unittest
from pulse_mock import MockAPIClient

class TestMyAPI(unittest.TestCase):
    def setUp(self):
        # Just initialize - cassettes auto-loaded from test fixtures
        self.client = MockAPIClient(cassette_dir='tests/fixtures')
    
    def test_get_game_data(self):
        # Make request - appropriate cassette loaded automatically
        response = self.client.get('http://localhost:1339/v1/leagues/NFL/games/NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['id'], 'NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8')
        self.assertIn('home_team', data)
    
    def test_nfl_client_integration(self):
        from pulse_mock import NFLMockClient
        
        nfl_client = NFLMockClient()
        teams = nfl_client.get_teams()
        self.assertGreater(len(teams), 0)
        
        # Test convenience methods
        eagles = nfl_client.find_team_by_name("Eagles")
        self.assertIsNotNone(eagles)
        self.assertEqual(eagles['name'], 'Eagles')
```

## REST Server

Pulse Mock includes a lightweight REST server that exposes all the NFLMockClient functionality through HTTP endpoints. This allows you to run a mock NFL API server that other applications can interact with using standard HTTP requests.

### Starting the Server

#### Option 1: Using the provided example
```bash
# Start the server on localhost:1339
python example_nfl_server.py

# Or run with demo requests
python example_nfl_server.py --demo
```

#### Option 2: Using the module directly
```bash
# Start with default settings (localhost:1339)
python -m pulse_mock.server

# Start with custom settings
python -m pulse_mock.server --host 0.0.0.0 --port 8000 --debug
```

#### Option 3: Programmatically
```python
from pulse_mock import create_app

app = create_app()
app.run(host='localhost', port=1339, debug=True)
```

### Available Endpoints

Once the server is running, you can access these REST endpoints:

#### Server Information
- `GET /health` - Health check and server status
- `GET /v1` - API information and endpoint documentation

#### Leagues & Teams
- `GET /v1/leagues` - Get all leagues
- `GET /v1/leagues/{league}/teams` - Get all teams in a league
- `GET /v1/leagues/{league}/teams/{team_id}` - Get specific team details
- `GET /v1/leagues/{league}/teams/search?name={name}` - Search for teams by name

#### Players
- `GET /v1/leagues/{league}/players` - Get all players in a league
- `GET /v1/leagues/{league}/players/{player_id}` - Get specific player details
- `GET /v1/leagues/{league}/players?position={position}` - Filter players by position
- `GET /v1/leagues/{league}/players?position={position}&team_id={team_id}` - Filter by position and team
- `GET /v1/leagues/{league}/players/search?name={name}` - Search for players by name
- `GET /v1/leagues/{league}/teams/{team_id}/players` - Get players for a specific team

#### Games
- `GET /v1/leagues/{league}/games` - Get all games in a league
- `GET /v1/leagues/{league}/games/{game_id}` - Get specific game details
- `GET /v1/leagues/{league}/teams/{team_id}/games` - Get games for a specific team
- `GET /v1/leagues/{league}/teams/{team1_id}/vs/{team2_id}` - Get games between two teams

#### Statistics
- `GET /v1/leagues/{league}/teams/{team_id}/stats` - Get team statistics

### Example Usage

```bash
# ✅ Health check - always works
curl http://localhost:1339/health

# ✅ Get all NFL teams - full data available
curl http://localhost:1339/v1/leagues/NFL/teams

# ✅ Get specific team details - works for Philadelphia Eagles
curl http://localhost:1339/v1/leagues/NFL/teams/NFL_team_ram7VKb86QoDRToIZOIN8rH

# ✅ Search for a team - works for available team names
curl "http://localhost:1339/v1/leagues/NFL/teams/search?name=Patriots"

# ✅ Get all quarterbacks - works for all positions
curl "http://localhost:1339/v1/leagues/NFL/players?position=QB"

# ✅ Get team statistics - works for Philadelphia Eagles
curl http://localhost:1339/v1/leagues/NFL/teams/NFL_team_ram7VKb86QoDRToIZOIN8rH/stats

# ❌ This will return 404 - no cassette data for Kansas City Chiefs
# curl http://localhost:1339/v1/leagues/NFL/teams/NFL_team_YTggHesR5qpx3BmqmYzxTPuq
```

**Note**: The server will return `404 Not Found` for requests to entities not covered in the included cassettes. See the "Data Availability & Limitations" section above for full details on what data is available.

### Using with Other Applications

The REST server makes it easy to use the mock NFL data with any application that can make HTTP requests:

```javascript
// JavaScript/Node.js
const response = await fetch('http://localhost:1339/v1/leagues/NFL/teams');
const teams = await response.json();
console.log(`Found ${teams.length} NFL teams`);
```

```python
# Python (using requests)
import requests
response = requests.get('http://localhost:1339/v1/leagues/NFL/teams')
teams = response.json()
print(f"Found {len(teams)} NFL teams")
```

```bash
# Shell/curl
curl http://localhost:1339/v1/leagues/NFL/teams | jq '.[0].name'
```

### Server Features

- 🚀 **Auto-loading**: Automatically loads all available VCR cassettes on startup
- 📡 **RESTful API**: Clean, standard REST endpoints following API conventions
- 🔍 **Search & Filter**: Built-in support for searching teams/players and filtering by position
- 📊 **Statistics**: Advanced endpoints for team statistics and analytics
- 🛡️ **Error Handling**: Proper HTTP status codes and error messages
- 💾 **In-Memory**: Fast responses using in-memory data from VCR cassettes

## Why Pulse Mock?

### 🚀 **Zero-Configuration Experience**
- **Before**: Manually load cassettes, manage file paths, handle errors
- **After**: Just make HTTP requests - everything works transparently

### 🏗️ **Perfect for Development & Testing**
```python
# Replace this...
import requests
response = requests.get('http://api.example.com/data')

# With this - same interface, predictable responses
from pulse_mock import MockAPIClient
client = MockAPIClient()
response = client.get('http://api.example.com/data')
```

### 🏈 **Rich Domain-Specific APIs**
The NFLMockClient demonstrates how to build specialized clients:
- **High-level methods**: `get_teams()`, `find_player_by_name()`
- **Smart filtering**: `get_players_by_position("QB")`
- **Analytics**: `get_team_statistics()`
- **Search capabilities**: Partial name matching, team lookup

### 📈 **Scalable Architecture**
- **Lazy loading**: Handle large cassette collections efficiently
- **Smart discovery**: Automatically find relevant cassettes
- **Memory efficient**: Load only what you need, when you need it

### 🎯 **Use Cases**

1. **Integration Testing**: Test against predictable API responses
2. **Development**: Work offline with realistic data
3. **Demos & Presentations**: Consistent, reliable API responses
4. **CI/CD Pipelines**: Fast, deterministic test runs
5. **API Prototyping**: Mock future APIs before they exist

## Data Availability & Limitations

⚠️ **Important**: The included VCR cassettes contain **limited sample data** from recorded API interactions. While all endpoints are functional, only specific entities have detailed data available.

### Available Data in Included Cassettes

The package includes sample NFL data with the following coverage:

#### ✅ **Fully Available Data**
- **All leagues** (NFL, NCAAFB)
- **All NFL teams** (32 teams with basic info)  
- **All NFL players** (2,400+ players with basic info)
- **All NFL games** (game listings)
- **Position filtering** (works for all positions: QB, RB, WR, etc.)
- **Team/player search** (works for available names)

#### ⚠️ **Limited Detail Data**
The following endpoints work but only have data for **specific entities**:

- **Team Details** (`/teams/{team_id}`): Only **Philadelphia Eagles** (`NFL_team_ram7VKb86QoDRToIZOIN8rH`)
- **Team Players** (`/teams/{team_id}/players`): Only **Philadelphia Eagles** roster
- **Team Games** (`/teams/{team_id}/games`): Only **Philadelphia Eagles** games  
- **Team Statistics** (`/teams/{team_id}/stats`): Only **Philadelphia Eagles** stats
- **Player Details** (`/players/{player_id}`): Only **Jalen Hurts** (`NFL_player_SyWsd7T30Oev84KlU0vKvQrU`)
- **Game Details** (`/games/{game_id}`): Only specific game (`NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8`)

### Adding Your Own Data

To add more detailed data, you have several options:

1. **Record new VCR cassettes** from a live API:
```python
# Use python-vcrpy to record new interactions
import vcr

with vcr.use_cassette('my_new_data.yaml'):
    # Make real API requests - they'll be recorded
    response = requests.get('https://real-api.com/teams/some_other_team')
```

2. **Manually create cassette files** following the VCR YAML format (see below)

3. **Extend existing cassettes** by adding new interactions to the YAML files

### Example Usage with Limited Data

```python
from pulse_mock import NFLMockClient

client = NFLMockClient()

# ✅ These work for any team/player
teams = client.get_teams()  # All 32 teams
all_players = client.get_all_players()  # 2400+ players 
qbs = client.get_players_by_position("QB")  # All quarterbacks

# ⚠️ These only work for specific entities
eagles_details = client.get_team("NFL_team_ram7VKb86QoDRToIZOIN8rH")  # ✅ Works
eagles_players = client.get_team_players("NFL_team_ram7VKb86QoDRToIZOIN8rH")  # ✅ Works

# This will raise RequestNotFoundError - no cassette data available
# chiefs_details = client.get_team("NFL_team_YTggHesR5qpx3BmqmYzxTPuq")  # ❌ Fails
```

The **REST server** handles these limitations gracefully by returning proper HTTP status codes (404 for missing data).

## VCR Cassette Format

Pulse Mock uses the standard VCR cassette format. Here's an example:

```yaml
---
version: 1
interactions:
- request:
    body: ""
    form: {}
    headers: {}
    url: http://localhost:1339/v1/leagues/NFL/games/NFL_game_iUehba7YmVy6d5KxLnvFCgRy
    method: GET
  response:
    body: |
      {"id":"NFL_game_iUehba7YmVy6d5KxLnvFCgRy","name":"Los Angeles Chargers v Detroit Lions"}
    headers:
      Content-Length:
      - "907"
      Content-Type:
      - application/json
    status: 200 OK
    code: 200
```

## API Reference

### MockAPIClient

The main class for transparent mock API interactions using VCR cassettes.

#### Constructor

```python
MockAPIClient(cassette_dir: Optional[str] = None, auto_load_all: bool = False)
```

- `cassette_dir`: Directory containing cassette files (defaults to `cassettes/` subdirectory)
- `auto_load_all`: If `True`, automatically load all available cassettes on initialization

#### Automatic Cassette Management

The client automatically discovers and loads cassettes as needed:

- **Lazy Loading (default)**: Cassettes loaded on-demand when requests are made
- **Eager Loading**: All cassettes loaded at initialization with `auto_load_all=True`
- **Smart Discovery**: Automatically finds all `.yaml`/`.yml` files in cassette directory

#### HTTP Methods

All HTTP methods work transparently and return a `MockResponse` object:

- `get(url, headers=None, **kwargs)`
- `post(url, headers=None, **kwargs)`
- `put(url, headers=None, **kwargs)`
- `delete(url, headers=None, **kwargs)`
- `patch(url, headers=None, **kwargs)`
- `request(method, url, headers=None, **kwargs)`

#### Cassette Management Methods

While not typically needed due to automatic loading, these methods are available:

- `load_cassette(cassette_name: str)`: Load a single cassette file
- `load_cassettes(cassette_names: List[str])`: Load multiple cassette files
- `load_all_available_cassettes()`: Load all cassettes from directory
- `discover_available_cassettes()`: List available cassette files
- `clear_cassettes()`: Clear all loaded cassettes

#### Utility Methods

- `list_interactions()`: List all loaded interactions
- `auto_load_cassette_for_url(url: str)`: Attempt to auto-load cassette for specific URL

### NFLMockClient

Specialized client for NFL API data with convenient high-level methods.

#### Constructor

```python
NFLMockClient(cassette_dir: Optional[str] = None, auto_load_all: bool = True)
```

Inherits from `MockAPIClient` with eager loading enabled by default for optimal performance.

#### Data Retrieval Methods

##### League & Team Data

- `get_leagues() -> List[Dict[str, Any]]`: Get all available leagues
- `get_teams(league: str = "NFL") -> List[Dict[str, Any]]`: Get all teams in league
- `get_team(team_id: str, league: str = "NFL") -> Dict[str, Any]`: Get specific team by ID

##### Player Data

- `get_all_players(league: str = "NFL") -> List[Dict[str, Any]]`: Get all players in league
- `get_player(player_id: str, league: str = "NFL") -> Dict[str, Any]`: Get specific player by ID
- `get_team_players(team_id: str, league: str = "NFL") -> List[Dict[str, Any]]`: Get all players for team

##### Game Data

- `get_all_games(league: str = "NFL") -> List[Dict[str, Any]]`: Get all games in league
- `get_game(game_id: str, league: str = "NFL") -> Dict[str, Any]`: Get specific game by ID
- `get_team_games(team_id: str, league: str = "NFL") -> List[Dict[str, Any]]`: Get all games for team

#### Search & Filter Methods

##### Team Search

- `find_team_by_name(team_name: str, league: str = "NFL") -> Optional[Dict[str, Any]]`: Find team by name/market/abbreviation

##### Player Search & Filtering

- `find_player_by_name(player_name: str, league: str = "NFL") -> List[Dict[str, Any]]`: Find players by name (partial matching)
- `get_players_by_position(position: str, team_id: Optional[str] = None, league: str = "NFL") -> List[Dict[str, Any]]`: Filter players by position

##### Game Filtering

- `get_games_between_teams(team1_id: str, team2_id: str, league: str = "NFL") -> List[Dict[str, Any]]`: Get games between two teams

#### Analytics Methods

- `get_team_statistics(team_id: str, league: str = "NFL") -> Dict[str, Any]`: Get comprehensive team stats including player counts by position

### MockResponse

Response object that mimics `requests.Response`.

#### Properties

- `status_code`: HTTP status code
- `headers`: Response headers dictionary
- `content`: Raw response content
- `text`: Response content as string

#### Methods

- `json()`: Parse response content as JSON

### Exceptions

- `CassetteNotFoundError`: Cassette file not found
- `RequestNotFoundError`: No matching interaction found
- `InvalidCassetteError`: Malformed cassette file
- `MockAPIError`: Base exception class

## Advanced Usage

### Custom Cassette Organization

```python
# Organize cassettes by environment or feature
integration_client = MockAPIClient(cassette_dir='tests/cassettes/integration')
staging_client = MockAPIClient(cassette_dir='tests/cassettes/staging')

# Clients automatically discover and load cassettes from their respective directories
integration_response = integration_client.get('http://api.example.com/integration-endpoint')
staging_response = staging_client.get('http://api.example.com/staging-endpoint')
```

### Loading Strategies

```python
# Strategy 1: Lazy loading for large cassette collections (default)
client = MockAPIClient()  # Cassettes loaded only when needed

# Strategy 2: Eager loading for performance-critical applications
client = MockAPIClient(auto_load_all=True)  # All cassettes loaded upfront

# Strategy 3: Manual control when needed
client = MockAPIClient()
client.load_all_available_cassettes()  # Load all now
```

### Error Handling

```python
from pulse_mock import MockAPIClient, RequestNotFoundError

client = MockAPIClient()

try:
    # Request that doesn't match any cassette
    response = client.get('http://api.example.com/not-recorded')
except RequestNotFoundError as e:
    print(f"Request not found in any cassettes: {e}")
    # The error message will list all loaded cassettes and interactions
```

### Debugging & Inspection

```python
client = MockAPIClient()

# Make a request to trigger auto-loading
response = client.get('http://localhost:1339/v1/leagues/NFL/teams')

# Inspect what was automatically loaded
print(f"Loaded cassettes: {client.loaded_cassettes}")

# List all available interactions
interactions = client.list_interactions()
print("Available interactions:")
for interaction in interactions:
    print(f"  {interaction}")

# Discover available cassettes without loading
available = client.discover_available_cassettes()
print(f"Available cassette files: {available}")
```

### NFL Client Advanced Usage

```python
from pulse_mock import NFLMockClient

client = NFLMockClient()

# Advanced team analysis
def analyze_team(team_name):
    team = client.find_team_by_name(team_name)
    if not team:
        print(f"Team '{team_name}' not found")
        return
    
    stats = client.get_team_statistics(team['id'])
    qbs = client.get_players_by_position("QB", team['id'])
    games = client.get_team_games(team['id'])
    
    print(f"\n📊 {team['market']} {team['name']} Analysis:")
    print(f"  Total Players: {stats['total_players']}")
    print(f"  Quarterbacks: {len(qbs)}")
    print(f"  Total Games: {len(games)}")
    print(f"  QBs: {[f\"{qb['first_name']} {qb['last_name']}\" for qb in qbs[:3]]}")

# Analyze multiple teams
for team_name in ["Eagles", "Cowboys", "Giants"]:
    analyze_team(team_name)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### 2.0.0
- **🎯 Transparent API Experience**: No manual cassette loading required - works like a real REST API
- **📼 Automatic Cassette Management**: Smart discovery and on-demand loading of VCR cassettes
- **🏈 NFL Mock Client**: Specialized high-level client with 20+ convenient methods for NFL data
- **🔍 Smart Loading Strategies**: Lazy loading (default) and eager loading options
- **⚡ Enhanced Performance**: Efficient cassette discovery and loading
- **🛠️ Advanced Methods**: Team search, player filtering, game analytics, and more
- **📚 Comprehensive Documentation**: Updated examples and API reference

### 1.0.0
- Initial release
- Basic VCR cassette loading and request matching
- Support for all HTTP methods
- Comprehensive error handling
- Full test suite

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/pulse-mock/issues) on GitHub.
