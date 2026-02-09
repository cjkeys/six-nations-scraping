#!/usr/bin/env python3
"""
Six Nations Fantasy Game Stats Scraper
Fetches all player stats from the Six Nations Fantasy API and saves to CSV/JSON
"""

import requests
import json
import csv
from typing import List, Dict, Any
from pathlib import Path

# Configuration
API_URL = "https://fantasy.sixnationsrugby.com/v1/private/stats"
# Note: Paste your fresh JWT token here (without "Token " prefix if using Bearer format)
AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NzA1ODkwNTYsImV4cCI6MTc3MzAwODI1NiwianRpIjoiOTFhSVZjaEc5Y3ZUQSt6XC9wQmJoUFE9PSIsImlzcyI6Imh0dHBzOlwvXC9mYW50YXN5LnNpeG5hdGlvbnNydWdieS5jb21cL202biIsInN1YiI6eyJpZCI6IjM2NTYzOSIsIm1haWwiOiJjYW1lcm9uLmtleXM1QGdtYWlsLmNvbSIsIm1hbmFnZXIiOiJDYW1lcm9uICIsImlkbCI6IjEiLCJpZGciOiIxIiwiZnVzZWF1IjoiRXVyb3BlXC9Mb25kb24iLCJtZXJjYXRvIjowLCJpZGpnIjoiMzkwNTgyIiwiaXNhZG1pbmNsaWVudCI6ZmFsc2UsImlzYWRtaW4iOmZhbHNlLCJpc3N1cGVyYWRtaW4iOmZhbHNlLCJpbnZpdGUiOmZhbHNlLCJ2aXAiOmZhbHNlLCJpZGVudGl0eSI6NjAwLCJpZ25vcmVjb2RlIjpmYWxzZSwiY29kZSI6IjYwMC4yIiwiY29kZUY1IjoiNjAwLjIzIiwiZGVjbyI6MH19.zrjNkvT9Bbu0RtxtvEbqjZdMpOrLIn7L8ktFYSLWUd0"
PAGE_SIZE = 50  # Get 50 players per request

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

# Headers for API request
HEADERS = {
    "authority": "fantasy.sixnationsrugby.com",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "authorization": f"Token {AUTH_TOKEN}",  # Token format as per API
    "origin": "https://fantasy.sixnationsrugby.com",
    "referer": "https://fantasy.sixnationsrugby.com/m6n/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "x-access-key": "600@18.23@"
}


def get_player_stats(page_index: int = 0, page_size: int = PAGE_SIZE, club = None, journee: int = None) -> Dict[str, Any]:
    """
    Fetch player stats from the API
    
    Args:
        page_index: Page number (0-indexed)
        page_size: Number of players per page
        club: Club filter (None = all clubs, or specific club ID)
        journee: Game week filter (None = all weeks, or specific week number)
    
    Returns:
        API response as dictionary
    """
    payload = {
        "credentials": {
            "critereRecherche": {
                "nom": "",
                "club": club,
                "position": "",
                "journee": journee if journee is not None else ""
            },
            "critereTri": "critere_16",  # Sort by attacking scrum wins
            "loadSelect": 0,
            "pageIndex": page_index,
            "pageSize": page_size
        }
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            params={"lg": "en"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"  Response keys: {result.keys()}")
        print(f"  Full response: {str(result)[:300]}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_index}: {e}")
        print(f"  Status code: {response.status_code if 'response' in locals() else 'N/A'}")
        if 'response' in locals():
            print(f"  Response text: {response.text[:200]}")
        return None


def fetch_all_stats(club = None) -> List[Dict[str, Any]]:
    """
    Fetch all player stats by paginating through all results
    
    Args:
        club: Club filter (None = all clubs)
    
    Returns:
        List of all player records
    """
    all_players = []
    page_index = 0
    
    while True:
        print(f"Fetching page {page_index}...")
        data = get_player_stats(page_index=page_index, page_size=PAGE_SIZE, club=club)
        
        if not data or not data.get("joueurs"):  # Changed from "data" to "joueurs"
            print("No more data to fetch")
            break
        
        players = data.get("joueurs", [])  # Changed from "data" to "joueurs"
        all_players.extend(players)
        
        total = data.get("total", 0)
        print(f"  Retrieved {len(players)} players (total: {total})")
        
        # Check if we've fetched all players
        if len(all_players) >= total:
            break
        
        page_index += 1
    
    print(f"\nTotal players fetched: {len(all_players)}")
    return all_players


def flatten_player_data(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten nested player data for CSV export
    
    Args:
        players: List of player records from API
    
    Returns:
        List of flattened player records
    """
    flattened = []
    
    for player in players:
        flat_record = {
            "Name": player.get("nomaffiche"),
            "ID": player.get("idws"),
            "Club": player.get("club"),
            "Position": player.get("position"),
            "Position Name": POSITION_NAMES.get(str(player.get("position")), "Unknown"),
        }
        
        # Add all stats/criteres
        if "criteres" in player:
            for critere in player["criteres"]:
                nom = critere.get("nom")
                value = critere.get("value")
                message = critere.get("message")
                flat_record[message] = value
        
        flattened.append(flat_record)
    
    return flattened


def save_to_json(players: List[Dict[str, Any]], filename: str = "six_nations_stats.json"):
    """Save player data to JSON file"""
    output_path = Path(filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    print(f"Saved raw data to {output_path}")


def save_to_csv(players: List[Dict[str, Any]], filename: str = "six_nations_stats.csv"):
    """Save flattened player data to CSV file"""
    if not players:
        print("No players to save")
        return
    
    flattened = flatten_player_data(players)
    output_path = Path(filename)
    
    # Get all unique fieldnames
    fieldnames = set()
    for record in flattened:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)
    
    print(f"Saved CSV to {output_path}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Six Nations Fantasy Game Stats Scraper")
    print("=" * 60)
    
    # Fetch all stats
    players = fetch_all_stats(club=None)  # None = all clubs
    
    if players:
        # Save to both JSON and CSV
        save_to_json(players, "data/six_nations_stats.json")
        save_to_csv(players, "data/six_nations_stats2.csv")
        
        print("\n" + "=" * 60)
        print("✓ Data download complete!")
        print("=" * 60)
    else:
        print("Failed to fetch player data")


if __name__ == "__main__":
    main()
