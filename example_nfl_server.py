#!/usr/bin/env python3
"""
NFL Mock Server Example

This example demonstrates how to start the NFL Mock API server and make HTTP requests
to it. The server exposes all NFLMockClient functionality through REST endpoints.

IMPORTANT: The included VCR cassettes have comprehensive list data (all teams, players, games)
but detailed entity data is limited to specific items (e.g., only Philadelphia Eagles for
team details). See README "Data Availability & Limitations" section for full details.

Usage:
    # Run the server
    python example_nfl_server.py

    # Or run the server directly
    python -m pulse_mock.server --host localhost --port 1339 --debug

    # Then make HTTP requests (in another terminal/browser)
    curl http://localhost:1339/v1/leagues
    curl http://localhost:1339/v1/leagues/NFL/teams
    curl http://localhost:1339/health
"""

import requests
import time
import threading
from pulse_mock import create_app


def start_server_in_thread():
    """Start the server in a background thread."""
    app = create_app()
    # Run server in a separate thread for demo purposes
    # In production, you'd run this as a separate process
    app.run(host='localhost', port=1339, debug=False, use_reloader=False)


def demo_api_requests():
    """Demonstrate making HTTP requests to the running server."""
    base_url = "http://localhost:1339"
    
    print("🏈 NFL Mock Server API Example")
    print("=" * 50)
    
    # Wait a moment for server to start
    time.sleep(2)
    
    try:
        print("\n1. Health check...")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        health_data = response.json()
        print(f"   Server status: {health_data['status']}")
        print(f"   Loaded cassettes: {len(health_data['loaded_cassettes'])}")
        print(f"   Total interactions: {health_data['total_interactions']}")
        
        print("\n2. API information...")
        response = requests.get(f"{base_url}/v1")
        api_info = response.json()
        print(f"   API: {api_info['name']} v{api_info['version']}")
        print(f"   Available endpoints: {len(api_info['endpoints'])}")
        
        print("\n3. Getting all leagues...")
        response = requests.get(f"{base_url}/v1/leagues")
        leagues = response.json()
        print(f"   Found {len(leagues)} leagues:")
        for league in leagues[:3]:  # Show first 3
            print(f"   - {league['name']} ({league['abbreviation']})")
        
        print("\n4. Getting NFL teams...")
        response = requests.get(f"{base_url}/v1/leagues/NFL/teams")
        teams = response.json()
        print(f"   Found {len(teams)} NFL teams:")
        for team in teams[:5]:  # Show first 5
            print(f"   - {team['name']} ({team['abbreviation']})")
        
        print("\n5. Getting a specific team...")
        # Use a known team ID that exists in our cassettes
        # NOTE: Detailed team data is only available for Philadelphia Eagles in the included cassettes
        known_team_id = "NFL_team_ram7VKb86QoDRToIZOIN8rH"  # Philadelphia Eagles
        response = requests.get(f"{base_url}/v1/leagues/NFL/teams/{known_team_id}")
        if response.status_code == 200:
            team = response.json()
            print(f"   Team: {team['name']} - {team['market']}")
            print(f"   Conference: {team.get('conference', 'Unknown')}")
            print(f"   Division: {team.get('division', 'Unknown')}")
        else:
            print(f"   Error fetching team details (status: {response.status_code})")
        
        print("\n6. Getting team players...")
        # Use the same known team ID (Philadelphia Eagles)
        response = requests.get(f"{base_url}/v1/leagues/NFL/teams/{known_team_id}/players")
        if response.status_code == 200:
            players = response.json()
            print(f"   Found {len(players)} players for Philadelphia Eagles:")
            for player in players[:3]:  # Show first 3
                pos = player.get('position', 'Unknown')
                print(f"   - {player['first_name']} {player['last_name']} ({pos})")
        else:
            print(f"   Error fetching team players (status: {response.status_code})")
        
        print("\n7. Getting all NFL players...")
        response = requests.get(f"{base_url}/v1/leagues/NFL/players")
        all_players = response.json()
        print(f"   Found {len(all_players)} total NFL players")
        
        print("\n8. Filtering players by position...")
        response = requests.get(f"{base_url}/v1/leagues/NFL/players?position=QB")
        qbs = response.json()
        print(f"   Found {len(qbs)} quarterbacks:")
        for qb in qbs[:3]:  # Show first 3
            print(f"   - {qb['first_name']} {qb['last_name']}")
        
        print("\n9. Searching for a team...")
        response = requests.get(f"{base_url}/v1/leagues/NFL/teams/search?name=Patriots")
        if response.status_code == 200:
            team = response.json()
            print(f"   Found: {team['name']} - {team['market']}")
        else:
            print(f"   Team not found (status: {response.status_code})")
        
        print("\n10. Getting team statistics...")
        # Use the same known team ID (Philadelphia Eagles)  
        response = requests.get(f"{base_url}/v1/leagues/NFL/teams/{known_team_id}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   {stats['team_info']['name']} statistics:")
            print(f"   - Total players: {stats['total_players']}")
            print(f"   - Total games: {stats['total_games']}")
            print(f"   - Players by position: {stats['players_by_position']}")
        else:
            print(f"   Error fetching team statistics (status: {response.status_code})")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:1339")
    except Exception as e:
        print(f"❌ Error making requests: {e}")


def main():
    """Main function - choose to run server or demo requests."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Run demo requests (assumes server is already running)
        demo_api_requests()
    else:
        print("🏈 Starting NFL Mock API Server...")
        print("=" * 50)
        print("Server will start on http://localhost:1339")
        print("\nAvailable endpoints:")
        print("  - Health check: http://localhost:1339/health")
        print("  - API info: http://localhost:1339/v1")
        print("  - All leagues: http://localhost:1339/v1/leagues")
        print("  - NFL teams: http://localhost:1339/v1/leagues/NFL/teams")
        print("  - And many more...")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start server (this will block)
        app = create_app()
        try:
            app.run(host='localhost', port=1339, debug=True)
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")


if __name__ == '__main__':
    main()
