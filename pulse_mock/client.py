"""
Main MockAPIClient implementation for handling VCR cassettes.
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse, parse_qs

from .exceptions import CassetteNotFoundError, RequestNotFoundError, InvalidCassetteError


class MockResponse:
    """A mock response object that mimics requests.Response."""
    
    def __init__(self, status_code: int, headers: Dict[str, Any], content: str):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.text = content
        
    def json(self) -> Dict[str, Any]:
        """Parse response content as JSON."""
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            raise ValueError("Response content is not valid JSON")


class MockAPIClient:
    """
    A mock API client that uses VCR cassettes to simulate API responses.
    
    The client automatically discovers and loads appropriate cassettes when requests are made,
    making it transparent to use - just make HTTP requests as you would with any REST API.
    
    Example:
        client = MockAPIClient()
        # No need to manually load cassettes - they're loaded automatically!
        response = client.get('http://localhost:1339/v1/leagues/NFL/games/NFL_game_iUehba7YmVy6d5KxLnvFCgRy')
        print(response.json())
    """
    
    def __init__(self, cassette_dir: Optional[str] = None, auto_load_all: bool = False):
        """
        Initialize the MockAPIClient.
        
        Args:
            cassette_dir: Directory containing VCR cassette files. Defaults to cassettes/ subdirectory.
            auto_load_all: If True, automatically load all available cassettes on initialization.
        """
        if cassette_dir is None:
            # Default to cassettes/ subdirectory relative to the pulse_mock package
            current_dir = os.path.dirname(__file__)
            cassette_dir = os.path.join(current_dir, 'cassettes')
        self.cassette_dir = cassette_dir
        self.interactions: List[Dict[str, Any]] = []
        self.loaded_cassettes: List[str] = []
        self._available_cassettes: Optional[List[str]] = None
        
        if auto_load_all:
            self.load_all_available_cassettes()
    
    def discover_available_cassettes(self) -> List[str]:
        """
        Discover all available cassette files in the cassette directory.
        
        Returns:
            List of cassette filenames
        """
        if self._available_cassettes is None:
            cassettes = []
            if os.path.exists(self.cassette_dir):
                for filename in os.listdir(self.cassette_dir):
                    if filename.endswith(('.yaml', '.yml')):
                        cassettes.append(filename)
            self._available_cassettes = sorted(cassettes)
        return self._available_cassettes
    
    def load_all_available_cassettes(self) -> None:
        """
        Load all available cassette files from the cassette directory.
        """
        available = self.discover_available_cassettes()
        for cassette in available:
            try:
                self.load_cassette(cassette)
            except (CassetteNotFoundError, InvalidCassetteError) as e:
                print(f"Warning: Could not load cassette {cassette}: {e}")
    
    def auto_load_cassette_for_url(self, url: str) -> bool:
        """
        Attempt to automatically load a cassette that might contain the requested URL.
        
        Args:
            url: The request URL to match against
            
        Returns:
            True if a potentially matching cassette was loaded, False otherwise
        """
        # If we already have interactions that might match, don't load more
        normalized_url = self._normalize_url(url)
        for interaction in self.interactions:
            request = interaction.get('request', {})
            interaction_url = self._normalize_url(request.get('url', ''))
            if interaction_url == normalized_url:
                return True
        
        # Try to load cassettes that haven't been loaded yet
        available = self.discover_available_cassettes()
        unloaded = [c for c in available if c not in self.loaded_cassettes]
        
        for cassette in unloaded:
            try:
                self.load_cassette(cassette)
                # Check if this cassette contains our URL
                for interaction in self.interactions:
                    request = interaction.get('request', {})
                    interaction_url = self._normalize_url(request.get('url', ''))
                    if interaction_url == normalized_url:
                        return True
            except (CassetteNotFoundError, InvalidCassetteError):
                continue
        
        return False
        
    def load_cassette(self, cassette_name: str) -> None:
        """
        Load a VCR cassette file.
        
        Args:
            cassette_name: Name of the cassette file (with or without .yaml extension)
            
        Raises:
            CassetteNotFoundError: If the cassette file cannot be found
            InvalidCassetteError: If the cassette file is malformed
        """
        if not cassette_name.endswith('.yaml') and not cassette_name.endswith('.yml'):
            cassette_name += '.yaml'
            
        cassette_path = os.path.join(self.cassette_dir, cassette_name)
        
        if not os.path.exists(cassette_path):
            raise CassetteNotFoundError(f"Cassette file not found: {cassette_path}")
            
        try:
            with open(cassette_path, 'r', encoding='utf-8') as f:
                cassette_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidCassetteError(f"Invalid YAML in cassette {cassette_name}: {e}")
        except Exception as e:
            raise InvalidCassetteError(f"Error reading cassette {cassette_name}: {e}")
            
        if not isinstance(cassette_data, dict) or 'interactions' not in cassette_data:
            raise InvalidCassetteError(f"Invalid cassette format in {cassette_name}")
            
        self.interactions.extend(cassette_data['interactions'])
        self.loaded_cassettes.append(cassette_name)
        
    def load_cassettes(self, cassette_names: List[str]) -> None:
        """
        Load multiple VCR cassette files.
        
        Args:
            cassette_names: List of cassette file names
        """
        for cassette_name in cassette_names:
            self.load_cassette(cassette_name)
            
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for matching by removing query parameters and fragments."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
    def _normalize_headers(self, headers: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Normalize headers for case-insensitive matching."""
        if not headers:
            return {}
        return {k.lower(): str(v) for k, v in headers.items()}
        
    def _match_request(self, method: str, url: str, headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Find a matching interaction for the given request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            
        Returns:
            Matching interaction dictionary
            
        Raises:
            RequestNotFoundError: If no matching interaction is found
        """
        normalized_url = self._normalize_url(url)
        normalized_headers = self._normalize_headers(headers)
        method = method.upper()
        
        # First try: match against already loaded interactions
        for interaction in self.interactions:
            request = interaction.get('request', {})
            
            # Match method
            if request.get('method', '').upper() != method:
                continue
                
            # Match URL (normalized)
            interaction_url = self._normalize_url(request.get('url', ''))
            if interaction_url != normalized_url:
                continue
                
            # If we get here, we have a match
            return interaction
        
        # Second try: attempt to auto-load cassettes for this URL
        if self.auto_load_cassette_for_url(url):
            # Try matching again after loading new cassettes
            for interaction in self.interactions:
                request = interaction.get('request', {})
                
                # Match method
                if request.get('method', '').upper() != method:
                    continue
                    
                # Match URL (normalized)
                interaction_url = self._normalize_url(request.get('url', ''))
                if interaction_url != normalized_url:
                    continue
                    
                # If we get here, we have a match
                return interaction
            
        raise RequestNotFoundError(
            f"No matching interaction found for {method} {url}. "
            f"Loaded {len(self.interactions)} interactions from cassettes: {', '.join(self.loaded_cassettes)}"
        )
        
    def _create_response(self, interaction: Dict[str, Any]) -> MockResponse:
        """Create a MockResponse from an interaction."""
        response_data = interaction.get('response', {})
        
        status_code = response_data.get('code', 200)
        headers = response_data.get('headers', {})
        body = response_data.get('body', '')
        
        return MockResponse(status_code, headers, body)
        
    def request(self, method: str, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """
        Make a mock request and return the corresponding response from cassettes.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            **kwargs: Additional arguments (ignored for compatibility)
            
        Returns:
            MockResponse object
        """
        interaction = self._match_request(method, url, headers)
        return self._create_response(interaction)
        
    def get(self, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """Make a GET request."""
        return self.request('GET', url, headers, **kwargs)
        
    def post(self, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """Make a POST request."""
        return self.request('POST', url, headers, **kwargs)
        
    def put(self, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """Make a PUT request."""
        return self.request('PUT', url, headers, **kwargs)
        
    def delete(self, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """Make a DELETE request."""
        return self.request('DELETE', url, headers, **kwargs)
        
    def patch(self, url: str, headers: Optional[Dict[str, Any]] = None, **kwargs) -> MockResponse:
        """Make a PATCH request."""
        return self.request('PATCH', url, headers, **kwargs)
        
    def clear_cassettes(self) -> None:
        """Clear all loaded cassettes and interactions."""
        self.interactions.clear()
        self.loaded_cassettes.clear()
        
    def list_interactions(self) -> List[str]:
        """Return a list of all loaded interactions as human-readable strings."""
        return [
            f"{interaction['request']['method']} {interaction['request']['url']}"
            for interaction in self.interactions
        ]


class NFLMockClient(MockAPIClient):
    """
    A specialized mock client for NFL API endpoints with convenient methods.
    
    This client provides easy-to-use methods for accessing NFL data including
    leagues, teams, players, and games. It works like a real REST API - just
    call the methods and the appropriate mock data is returned automatically.
    
    Example:
        client = NFLMockClient()
        # VCR cassettes are loaded automatically - no manual setup required!
        
        # Get all leagues
        leagues = client.get_leagues()
        
        # Get NFL teams  
        teams = client.get_teams()
        
        # Get a specific team
        team = client.get_team("NFL_team_ram7VKb86QoDRToIZOIN8rH")
        
        # Get players for a team
        players = client.get_team_players("NFL_team_ram7VKb86QoDRToIZOIN8rH")
        
        # Get games for a team
        games = client.get_team_games("NFL_team_ram7VKb86QoDRToIZOIN8rH")
        
        # Get a specific player
        player = client.get_player("NFL_player_SyWsd7T30Oev84KlU0vKvQrU")
        
        # Get a specific game
        game = client.get_game("NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8")
        
        # Get all players in the league
        all_players = client.get_all_players()
    """
    
    def __init__(self, cassette_dir: Optional[str] = None, auto_load_all: bool = True):
        """
        Initialize the NFLMockClient.
        
        Args:
            cassette_dir: Directory containing VCR cassette files
            auto_load_all: Whether to automatically load all available cassettes on initialization
        """
        super().__init__(cassette_dir, auto_load_all=auto_load_all)
        self.base_url = "http://localhost:1339"
    
    def get_leagues(self) -> List[Dict[str, Any]]:
        """
        Get all available leagues.
        
        Returns:
            List of league dictionaries
        """
        url = f"{self.base_url}/v1/leagues"
        response = self.get(url)
        return response.json()
    
    def get_teams(self, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all teams in a league.
        
        Args:
            league: League identifier (default: "NFL")
            
        Returns:
            List of team dictionaries
        """
        url = f"{self.base_url}/v1/leagues/{league}/teams"
        response = self.get(url)
        return response.json()
    
    def get_team(self, team_id: str, league: str = "NFL") -> Dict[str, Any]:
        """
        Get a specific team by ID.
        
        Args:
            team_id: Team identifier
            league: League identifier (default: "NFL")
            
        Returns:
            Team dictionary
        """
        url = f"{self.base_url}/v1/leagues/{league}/teams/{team_id}"
        response = self.get(url)
        return response.json()
    
    def get_team_players(self, team_id: str, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all players for a specific team.
        
        Args:
            team_id: Team identifier
            league: League identifier (default: "NFL")
            
        Returns:
            List of player dictionaries
        """
        url = f"{self.base_url}/v1/leagues/{league}/teams/{team_id}/players"
        response = self.get(url)
        return response.json()
    
    def get_team_games(self, team_id: str, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all games for a specific team.
        
        Args:
            team_id: Team identifier
            league: League identifier (default: "NFL")
            
        Returns:
            List of game dictionaries
        """
        url = f"{self.base_url}/v1/leagues/{league}/teams/{team_id}/games"
        response = self.get(url)
        return response.json()
    
    def get_player(self, player_id: str, league: str = "NFL") -> Dict[str, Any]:
        """
        Get a specific player by ID.
        
        Args:
            player_id: Player identifier
            league: League identifier (default: "NFL")
            
        Returns:
            Player dictionary
        """
        url = f"{self.base_url}/v1/leagues/{league}/players/{player_id}"
        response = self.get(url)
        return response.json()
    
    def get_game(self, game_id: str, league: str = "NFL") -> Dict[str, Any]:
        """
        Get a specific game by ID.
        
        Args:
            game_id: Game identifier
            league: League identifier (default: "NFL")
            
        Returns:
            Game dictionary
        """
        url = f"{self.base_url}/v1/leagues/{league}/games/{game_id}"
        response = self.get(url)
        return response.json()
    
    def get_all_games(self, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all games in a league.
        
        Args:
            league: League identifier (default: "NFL")
            
        Returns:
            List of game dictionaries
        """
        url = f"{self.base_url}/v1/leagues/{league}/games"
        response = self.get(url)
        return response.json()
    
    def get_all_players(self, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all players in a league.
        
        Args:
            league: League identifier (default: "NFL")
            
        Returns:
            List of player dictionaries
        """
        url = f"{self.base_url}/v1/leagues/{league}/players"
        response = self.get(url)
        data = response.json()
        # The response contains {"players": [array_of_players]}, so extract just the players array
        return data.get("players", [])
    
    # Convenience methods for filtering and searching
    
    def find_team_by_name(self, team_name: str, league: str = "NFL") -> Optional[Dict[str, Any]]:
        """
        Find a team by name or market.
        
        Args:
            team_name: Team name or market to search for
            league: League identifier (default: "NFL")
            
        Returns:
            Team dictionary if found, None otherwise
        """
        teams = self.get_teams(league)
        team_name_lower = team_name.lower()
        
        for team in teams:
            if (team_name_lower in team.get('name', '').lower() or
                team_name_lower in team.get('market', '').lower() or
                team_name_lower == team.get('abbreviation', '').lower()):
                return team
        return None
    
    def find_player_by_name(self, player_name: str, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Find players by name (supports partial matching).
        
        Args:
            player_name: Player name to search for
            league: League identifier (default: "NFL")
            
        Returns:
            List of matching player dictionaries
        """
        players = self.get_all_players(league)
        player_name_lower = player_name.lower()
        
        matching_players = []
        for player in players:
            first_name = player.get('first_name', '').lower()
            last_name = player.get('last_name', '').lower()
            full_name = f"{first_name} {last_name}".strip()
            
            if (player_name_lower in first_name or
                player_name_lower in last_name or
                player_name_lower in full_name):
                matching_players.append(player)
        
        return matching_players
    
    def get_games_between_teams(self, team1_id: str, team2_id: str, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get all games between two specific teams.
        
        Args:
            team1_id: First team identifier
            team2_id: Second team identifier
            league: League identifier (default: "NFL")
            
        Returns:
            List of game dictionaries
        """
        # Get games for team1 and filter for games against team2
        team1_games = self.get_team_games(team1_id, league)
        
        matching_games = []
        for game in team1_games:
            home_team_id = game.get('home_team', {}).get('id')
            away_team_id = game.get('away_team', {}).get('id')
            
            if ((home_team_id == team1_id and away_team_id == team2_id) or
                (home_team_id == team2_id and away_team_id == team1_id)):
                matching_games.append(game)
        
        return matching_games
    
    def get_players_by_position(self, position: str, team_id: Optional[str] = None, league: str = "NFL") -> List[Dict[str, Any]]:
        """
        Get players by position, optionally filtered by team.
        
        Args:
            position: Player position (e.g., "QB", "RB", "WR")
            team_id: Optional team identifier to filter by
            league: League identifier (default: "NFL")
            
        Returns:
            List of player dictionaries
        """
        if team_id:
            players = self.get_team_players(team_id, league)
        else:
            players = self.get_all_players(league)
        
        position_upper = position.upper()
        return [p for p in players if p.get('position', '').upper() == position_upper]
    
    def get_team_statistics(self, team_id: str, league: str = "NFL") -> Dict[str, Any]:
        """
        Get basic statistics for a team.
        
        Args:
            team_id: Team identifier
            league: League identifier (default: "NFL")
            
        Returns:
            Dictionary with team stats including player count, games count, etc.
        """
        team = self.get_team(team_id, league)
        players = self.get_team_players(team_id, league)
        games = self.get_team_games(team_id, league)
        
        # Count players by position
        position_counts = {}
        for player in players:
            pos = player.get('position', 'Unknown')
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Count games by status
        game_status_counts = {}
        for game in games:
            status = game.get('status', 'Unknown')
            game_status_counts[status] = game_status_counts.get(status, 0) + 1
        
        return {
            'team_info': team,
            'total_players': len(players),
            'total_games': len(games),
            'players_by_position': position_counts,
            'games_by_status': game_status_counts
        }
