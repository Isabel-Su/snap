#!/usr/bin/env python3
"""
NFL Mock Client Example

This example demonstrates how to use the NFLMockClient as a transparent REST API
for NFL data. The client automatically manages VCR cassettes behind the scenes,
providing convenient methods for accessing leagues, teams, players, and games data.
"""

from pulse_mock import NFLMockClient


def main():
    """Main example function demonstrating NFLMockClient usage."""
    
    print("🏈 NFL Mock Client Example")
    print("=" * 50)
    
    # Initialize the NFL client - works like a real REST API!
    # VCR cassettes are automatically loaded behind the scenes
    client = NFLMockClient()
    
    print("\n1. Getting all leagues...")
    leagues = client.get_leagues()
    print(f"   Found {len(leagues)} leagues:")
    for league in leagues:
        print(f"   - {league['name']} ({league['abbreviation']})")
    
    print("\n2. Getting all NFL teams...")
    teams = client.get_teams()
    print(f"   Found {len(teams)} teams:")
    for team in teams[:5]:  # Show first 5 teams
        print(f"   - {team['market']} {team['name']} ({team['abbreviation']})")
    print(f"   ... and {len(teams) - 5} more teams")
    
    print("\n3. Finding the Philadelphia Eagles...")
    eagles = client.find_team_by_name("Eagles")
    if eagles:
        print(f"   Found: {eagles['market']} {eagles['name']} (ID: {eagles['id']})")
        
        print("\n4. Getting Eagles players...")
        players = client.get_team_players(eagles['id'])
        print(f"   Found {len(players)} players:")
        for player in players[:10]:  # Show first 10 players
            print(f"   - {player['first_name']} {player['last_name']} ({player['position']})")
        print(f"   ... and {len(players) - 10} more players")
        
        print("\n5. Getting Eagles quarterbacks...")
        qbs = client.get_players_by_position("QB", eagles['id'])
        print(f"   Found {len(qbs)} quarterbacks:")
        for qb in qbs:
            print(f"   - {qb['first_name']} {qb['last_name']}")
        
        print("\n6. Getting Eagles games...")
        games = client.get_team_games(eagles['id'])
        print(f"   Found {len(games)} games:")
        for game in games[:5]:  # Show first 5 games
            home = game['home_team']['market'] + ' ' + game['home_team']['name']
            away = game['away_team']['market'] + ' ' + game['away_team']['name']
            print(f"   - {away} @ {home} ({game['status']})")
        print(f"   ... and {len(games) - 5} more games")
        
        print("\n7. Getting team statistics...")
        stats = client.get_team_statistics(eagles['id'])
        print(f"   Team: {stats['team_info']['market']} {stats['team_info']['name']}")
        print(f"   Total Players: {stats['total_players']}")
        print(f"   Total Games: {stats['total_games']}")
        print(f"   Players by Position:")
        for pos, count in sorted(stats['players_by_position'].items()):
            print(f"     {pos}: {count}")
    else:
        print("   Eagles not found!")
    
    print("\n8. Finding a specific player (Jalen Hurts)...")
    hurts_players = client.find_player_by_name("Jalen Hurts")
    if hurts_players:
        hurts = hurts_players[0]  # Take the first match
        print(f"   Found: {hurts['first_name']} {hurts['last_name']} (ID: {hurts['id']})")
        
        # Get full player details
        player_details = client.get_player(hurts['id'])
        print(f"   Position: {player_details['position']}")
        print(f"   Jersey Number: {player_details.get('jersey_number', 'N/A')}")
        print(f"   Team: {player_details['team']['market']} {player_details['team']['name']}")
    else:
        print("   Jalen Hurts not found!")
    
    print("\n9. Getting a specific game...")
    # Using game ID from the cassettes we examined
    game_id = "NFL_game_s7NlrGA1L1RaSOZNtJ8HHSj8"
    game = client.get_game(game_id)
    home = f"{game['home_team']['market']} {game['home_team']['name']}"
    away = f"{game['away_team']['market']} {game['away_team']['name']}"
    print(f"   Game: {game['display_name']}")
    print(f"   Status: {game['status']}")
    print(f"   Scheduled: {game['scheduled_at']}")
    
    print("\n10. Getting all quarterbacks in the league...")
    all_qbs = client.get_players_by_position("QB")
    print(f"    Found {len(all_qbs)} quarterbacks league-wide:")
    for qb in all_qbs[:10]:  # Show first 10
        team_name = f"{qb['team']['market']} {qb['team']['name']}"
        print(f"    - {qb['first_name']} {qb['last_name']} ({team_name})")
    print(f"    ... and {len(all_qbs) - 10} more quarterbacks")
    
    print("\n" + "=" * 50)
    print("✅ NFL Mock Client example completed successfully!")


if __name__ == "__main__":
    main()
