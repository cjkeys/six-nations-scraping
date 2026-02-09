#!/usr/bin/env python3
"""
Six Nations Fantasy Rugby Team Builder
Reads player stats from CSV and builds optimal team based on constraints
"""

import csv
from typing import List, Dict, Any
from pathlib import Path
import pulp

from html_generator import save_teams_to_html
from html_table_generator import save_team_to_html_table

# Position mapping
POSITION_NAMES = {
    "6": "Back Three",
    "7": "Centre",
    "8": "Fly Half",
    "9": "Scrum Half",
    "10": "Back Row",
    "11": "Second Row",
    "12": "Prop",
    "13": "Hooker",
}


def read_players_from_csv(filename: str = "data/six_nations_stats2.csv") -> List[Dict[str, Any]]:
    """
    Read player data from CSV file
    
    Args:
        filename: Path to the CSV file
    
    Returns:
        List of player records as dictionaries
    """
    players = []
    csv_path = Path(filename)
    
    if not csv_path.exists():
        print(f"Error: File {filename} not found")
        return []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                players.append(row)
        print(f"Loaded {len(players)} players from {filename}")
        return players
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []


def build_optimal_team(players: List[Dict[str, Any]], excluded_ids: set = None, limit_nations: bool = True) -> Dict[str, Any]:
    """
    Build an optimal fantasy rugby team using linear programming.
    
    Maximizes total average points while respecting constraints:
    - Max 4 players from any one club
    - Exactly: Back Three (3), Centre (2), Fly Half (1), Scrum Half (1), 
               Back Row (3), Second Row (2), Prop (2), Hooker (1)
    
    Uses PuLP linear programming solver for fast, optimal results.
    
    Args:
        players: List of player records
        excluded_ids: Set of player IDs to exclude from selection
    
    Returns:
        Dictionary with team, captain, total points, and club breakdown
    """
    if excluded_ids is None:
        excluded_ids = set()
    
    position_requirements = {
        "Back Three": 3,
        "Centre": 2,
        "Fly Half": 1,
        "Scrum Half": 1,
        "Back Row": 3,
        "Second Row": 2,
        "Prop": 2,
        "Hooker": 1,
    }
    
    # Calculate average points and position name for each player
    for player in players:
        # Use only the "Average points" column
        try:
            avg_points = float(player.get("Average points", 0)) if player.get("Average points") else 0
        except (ValueError, TypeError):
            avg_points = 0
        player["avg_points"] = avg_points
        
        # Map position number to position name
        position_num = str(player.get("Position", "")).strip()
        player["Position Name"] = POSITION_NAMES.get(position_num, "Unknown")
    
    # Create the LP problem
    prob = pulp.LpProblem("Fantasy_Rugby_Team", pulp.LpMaximize)
    
    # Create binary decision variables for each player (excluding those already selected)
    player_vars = {}
    for i, player in enumerate(players):
        if player.get("ID") not in excluded_ids:
            player_vars[i] = pulp.LpVariable(f"player_{i}", cat='Binary')
    
    # Objective: maximize total average points
    prob += pulp.lpSum([player_vars[i] * players[i].get("avg_points", 0) for i in player_vars])
    
    # Constraint: position requirements
    for position, count_needed in position_requirements.items():
        position_players = [i for i in player_vars if players[i].get("Position Name") == position]
        prob += pulp.lpSum([player_vars[i] for i in position_players]) == count_needed, f"position_{position}"
    
    # Constraint: max 4 players per club
    if limit_nations:
        clubs = set(p.get("Club", "Unknown") for p in players if p.get("ID") not in excluded_ids)
        for club in clubs:
            club_players = [i for i in player_vars if players[i].get("Club") == club]
            prob += pulp.lpSum([player_vars[i] for i in club_players]) <= 4, f"club_{club}"
    
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extract the solution
    team = []
    for i, player in enumerate(players):
        if i in player_vars and pulp.value(player_vars[i]) == 1:
            team.append(player)
    
    # Find the captain (highest scorer)
    captain = max(team, key=lambda p: p.get("avg_points", 0)) if team else None
    
    # Build result dictionary with counts
    club_counts = {}
    position_counts = {pos: 0 for pos in position_requirements}
    
    for player in team:
        club = player.get("Club", "Unknown")
        club_counts[club] = club_counts.get(club, 0) + 1
        position = player.get("Position Name", "Unknown")
        position_counts[position] += 1
    
    # Calculate total points with captain bonus
    total_points = sum(p.get("avg_points", 0) for p in team)
    if captain:
        # Captain gets double points, so add their points once more
        total_points += captain.get("avg_points", 0)
    
    avg_points = total_points / len(team) if team else 0
    max_points = captain.get("avg_points", 0)
    
    return {
        "team": team,
        "captain": captain,
        "total_players": len(team),
        "total_points": total_points,
        "average_points": avg_points,
        "max_points": max_points,
        "club_breakdown": club_counts,
        "position_breakdown": position_counts
    }

def display_team(team_result: Dict[str, Any], team_number: int = 1):
    """Display team information in a formatted way"""
    print("\n" + "=" * 80)
    print(f"TEAM {team_number}: OPTIMAL FANTASY RUGBY TEAM")
    print("=" * 80)
    print(f"Total Players Selected: {team_result['total_players']}")
    print(f"Total Points: {team_result['total_points']:.2f}")
    if team_result['captain']:
        print(f"Captain: {team_result['captain'].get('Name', 'Unknown')} ({team_result['captain'].get('avg_points', 0):.2f} x2)")
    print(f"Average Points per Player: {team_result['average_points']:.2f}")
    print(f"\nClub Breakdown: {team_result['club_breakdown']}")
    print(f"Position Breakdown: {team_result['position_breakdown']}")
    
    # Sort by custom position order
    position_order = {
        "Prop": 0,
        "Hooker": 1,
        "Second Row": 2,
        "Back Row": 3,
        "Scrum Half": 4,
        "Fly Half": 5,
        "Centre": 6,
        "Back Three": 7,
    }
    
    sorted_team = sorted(
        team_result['team'],
        key=lambda p: position_order.get(p.get('Position Name', 'Unknown'), 999)
    )
    
    print("\n" + "-" * 80)
    print("TEAM ROSTER:")
    print("-" * 80)
    print(f"{'Name':<25} {'Position':<15} {'Club':<15} {'Points':<10}")
    print("-" * 80)
    
    for player in sorted_team:
        name = player.get('Name', 'Unknown')[:24]
        position = player.get('Position Name', 'Unknown')[:14]
        club = player.get('Club', 'Unknown')[:14]
        points = f"{player.get('avg_points', 0):.2f}"
        if team_result['captain'] and team_result['captain'].get('ID') == player.get('ID'):
            name = name + " (C)"
        print(f"{name:<25} {position:<15} {club:<15} {points:<10}")
    
    print("=" * 80)


def save_teams_to_csv(team1_result: Dict[str, Any], team2_result: Dict[str, Any], filename: str = "data/selected_teams.csv"):
    """
    Save both teams to CSV file
    
    Args:
        team1_result: First team result dictionary
        team2_result: Second team result dictionary
        filename: Output CSV filename
    """
    position_order = {
        "Prop": 0,
        "Hooker": 1,
        "Second Row": 2,
        "Back Row": 3,
        "Scrum Half": 4,
        "Fly Half": 5,
        "Centre": 6,
        "Back Three": 7,
    }
    
    # Prepare data for both teams
    all_team_data = []
    
    # Team 1
    for player in team1_result['team']:
        all_team_data.append({
            "Position": player.get('Position Name', 'Unknown'),
            "Name": player.get('Name', 'Unknown'),
            "Nation": player.get('Club', 'Unknown'),
            "Points": f"{player.get('avg_points', 0):.2f}",
            "Team": "1st",
            "Captain": "Yes" if team1_result['captain'] and team1_result['captain'].get('ID') == player.get('ID') else "No"
        })
    
    # Team 2
    for player in team2_result['team']:
        all_team_data.append({
            "Position": player.get('Position Name', 'Unknown'),
            "Name": player.get('Name', 'Unknown'),
            "Nation": player.get('Club', 'Unknown'),
            "Points": f"{player.get('avg_points', 0):.2f}",
            "Team": "2nd",
            "Captain": "Yes" if team2_result['captain'] and team2_result['captain'].get('ID') == player.get('ID') else "No"
        })
    
    # Sort by team and position
    all_team_data.sort(key=lambda x: (x["Team"], position_order.get(x["Position"], 999)))
    
    # Write to CSV
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["Position", "Name", "Nation", "Points", "Team", "Captain"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_team_data)
        print(f"\nSaved teams to {output_path}")
    except Exception as e:
        print(f"Error saving teams to CSV: {e}")


def main():
    """Main execution"""
    print("=" * 80)
    print("Six Nations Fantasy Rugby Team Builder")
    print("=" * 80)
    
    # Read players from CSV
    players = read_players_from_csv("data/six_nations_stats2.csv")
    
    if not players:
        print("Failed to load player data")
        return
    
    # Build first optimal team
    team1_result = build_optimal_team(players)
    display_team(team1_result, team_number=1)
    
    # Build second team excluding players from first team
    excluded_ids = set(p.get("ID") for p in team1_result['team'])
    team2_result = build_optimal_team(players, excluded_ids=excluded_ids)
    display_team(team2_result, team_number=2)

    #build team without nation limit
    team3_result = build_optimal_team(players, limit_nations=False)
    display_team(team3_result, team_number=3)
    
    # Summary comparison
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Team 1 Total Points: {team1_result['total_points']:.2f}")
    print(f"Team 2 Total Points: {team2_result['total_points']:.2f}")
    print(f"Combined Total Points: {team1_result['total_points'] + team2_result['total_points']:.2f}")
    print("=" * 80)
    
    # Save teams to CSV and HTML
    save_teams_to_csv(team1_result, team3_result, "data/selected_teams.csv")
    save_teams_to_html(team1_result, team2_result, "data/selected_teams.html")
    save_team_to_html_table(team1_result, "data/selected_team_table.html")


if __name__ == "__main__":
    main()
