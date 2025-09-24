"""
Lightweight REST server that exposes NFLMockClient methods as HTTP endpoints.

This server provides a REST API interface to all the functionality available
in the NFLMockClient, making it easy to access NFL data through HTTP requests.

Usage:
    from pulse_mock.server import create_app
    
    app = create_app()
    app.run(host='localhost', port=1339, debug=True)

Or run directly:
    python -m pulse_mock.server
"""

from flask import Flask, jsonify, request
from typing import Dict, Any, Optional
import traceback

from .client import NFLMockClient
from .exceptions import CassetteNotFoundError, RequestNotFoundError, InvalidCassetteError


def create_app(cassette_dir: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        cassette_dir: Directory containing VCR cassette files
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Initialize the NFLMockClient
    client = NFLMockClient(cassette_dir=cassette_dir, auto_load_all=True)
    
    @app.errorhandler(RequestNotFoundError)
    def handle_request_not_found(e):
        return jsonify({'error': 'Not found', 'message': str(e)}), 404
    
    @app.errorhandler(CassetteNotFoundError)
    def handle_cassette_not_found(e):
        return jsonify({'error': 'Cassette not found', 'message': str(e)}), 500
    
    @app.errorhandler(InvalidCassetteError)
    def handle_invalid_cassette(e):
        return jsonify({'error': 'Invalid cassette', 'message': str(e)}), 500
    
    @app.errorhandler(Exception)
    def handle_general_error(e):
        return jsonify({
            'error': 'Internal server error', 
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'loaded_cassettes': client.loaded_cassettes,
            'total_interactions': len(client.interactions)
        })
    
    # API Info endpoint
    @app.route('/v1')
    def api_info():
        """API information and available endpoints."""
        return jsonify({
            'name': 'NFL Mock API',
            'version': '1.0',
            'description': 'Mock NFL API server using VCR cassettes',
            'endpoints': {
                'leagues': '/v1/leagues',
                'teams': '/v1/leagues/{league}/teams',
                'team_details': '/v1/leagues/{league}/teams/{team_id}',
                'team_players': '/v1/leagues/{league}/teams/{team_id}/players',
                'team_games': '/v1/leagues/{league}/teams/{team_id}/games',
                'team_stats': '/v1/leagues/{league}/teams/{team_id}/stats',
                'players': '/v1/leagues/{league}/players',
                'player_details': '/v1/leagues/{league}/players/{player_id}',
                'games': '/v1/leagues/{league}/games',
                'game_details': '/v1/leagues/{league}/games/{game_id}',
                'search_teams': '/v1/leagues/{league}/teams/search?name={name}',
                'search_players': '/v1/leagues/{league}/players/search?name={name}',
                'filter_players': '/v1/leagues/{league}/players?position={position}&team_id={team_id}'
            },
            'loaded_cassettes': client.loaded_cassettes,
            'total_interactions': len(client.interactions)
        })
    
    # League endpoints
    @app.route('/v1/leagues')
    def get_leagues():
        """Get all available leagues."""
        return jsonify(client.get_leagues())
    
    # Team endpoints
    @app.route('/v1/leagues/<league>/teams')
    def get_teams(league: str):
        """Get all teams in a league."""
        return jsonify(client.get_teams(league))
    
    @app.route('/v1/leagues/<league>/teams/search')
    def search_teams(league: str):
        """Search for teams by name."""
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'Missing required parameter: name'}), 400
        
        team = client.find_team_by_name(name, league)
        if team:
            return jsonify(team)
        else:
            return jsonify({'error': 'Team not found', 'searched_name': name}), 404
    
    @app.route('/v1/leagues/<league>/teams/<team_id>')
    def get_team(league: str, team_id: str):
        """Get a specific team by ID."""
        return jsonify(client.get_team(team_id, league))
    
    @app.route('/v1/leagues/<league>/teams/<team_id>/players')
    def get_team_players(league: str, team_id: str):
        """Get all players for a specific team."""
        return jsonify(client.get_team_players(team_id, league))
    
    @app.route('/v1/leagues/<league>/teams/<team_id>/games')
    def get_team_games(league: str, team_id: str):
        """Get all games for a specific team."""
        return jsonify(client.get_team_games(team_id, league))
    
    @app.route('/v1/leagues/<league>/teams/<team_id>/stats')
    def get_team_stats(league: str, team_id: str):
        """Get statistics for a specific team."""
        return jsonify(client.get_team_statistics(team_id, league))
    
    # Player endpoints
    @app.route('/v1/leagues/<league>/players')
    def get_players(league: str):
        """Get all players in a league, with optional filtering."""
        position = request.args.get('position')
        team_id = request.args.get('team_id')
        
        if position:
            return jsonify(client.get_players_by_position(position, team_id, league))
        else:
            return jsonify(client.get_all_players(league))
    
    @app.route('/v1/leagues/<league>/players/search')
    def search_players(league: str):
        """Search for players by name."""
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'Missing required parameter: name'}), 400
        
        players = client.find_player_by_name(name, league)
        return jsonify(players)
    
    @app.route('/v1/leagues/<league>/players/<player_id>')
    def get_player(league: str, player_id: str):
        """Get a specific player by ID."""
        return jsonify(client.get_player(player_id, league))
    
    # Game endpoints
    @app.route('/v1/leagues/<league>/games')
    def get_games(league: str):
        """Get all games in a league."""
        return jsonify(client.get_all_games(league))
    
    @app.route('/v1/leagues/<league>/games/<game_id>')
    def get_game(league: str, game_id: str):
        """Get a specific game by ID."""
        return jsonify(client.get_game(game_id, league))
    
    # Special endpoints for game relationships
    @app.route('/v1/leagues/<league>/teams/<team1_id>/vs/<team2_id>')
    def get_games_between_teams(league: str, team1_id: str, team2_id: str):
        """Get all games between two specific teams."""
        return jsonify(client.get_games_between_teams(team1_id, team2_id, league))
    
    return app


def main():
    """Run the server directly."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Run the NFL Mock API server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=1339, help='Port to bind to (default: 1339)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--cassette-dir', help='Directory containing VCR cassette files')
    
    args = parser.parse_args()
    
    # Create the Flask app
    app = create_app(cassette_dir=args.cassette_dir)
    
    print(f"Starting NFL Mock API server on http://{args.host}:{args.port}")
    print(f"API documentation available at: http://{args.host}:{args.port}/v1")
    print(f"Health check available at: http://{args.host}:{args.port}/health")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")


if __name__ == '__main__':
    main()
