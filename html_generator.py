#!/usr/bin/env python3
"""
Six Nations Fantasy Rugby HTML Visualization
Generates HTML output for team formations and statistics
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime

# Position to color mapping for CSS
POSITION_COLORS = {
    "Back Three": "#e74c3c",
    "Centre": "#f39c12",
    "Fly Half": "#3498db",
    "Scrum Half": "#9b59b6",
    "Back Row": "#27ae60",
    "Second Row": "#2980b9",
    "Prop": "#c0392b",
    "Hooker": "#16a085",
}

# Nation/Club colors
NATION_COLORS = {
    "England": "#15549F",
    "France": "#001f3f",
    "Ireland": "#003366",
    "Italy": "#0066cc",
    "Scotland": "#00005c",
    "Wales": "#000000",
}


def save_teams_to_html(team1_result: Dict[str, Any], team2_result: Dict[str, Any], filename: str = "data/selected_teams.html"):
    """
    Save both teams to HTML file as rugby field formations with SVG
    
    Args:
        team1_result: First team result dictionary
        team2_result: Second team result dictionary
        filename: Output HTML filename
    """
    # Field positioning for each position (x, y) in SVG coordinates
    POSITION_COORDS = {
        "Back Three": [(100, 80), (400, 50), (700, 80)],
        "Centre": [(200, 180), (600, 180)],
        "Fly Half": [(450, 280)],
        "Scrum Half": [(450, 380)],
        "Back Row": [(250, 500), (450, 550), (650, 500)],
        "Second Row": [(350, 620), (550, 620)],
        "Prop": [(300, 720), (600, 720)],
        "Hooker": [(450, 800)],
    }
    
    def generate_field_svg(team_result: Dict[str, Any], team_name: str) -> str:
        """Generate SVG rugby field with players positioned"""
        svg = """
        <svg width="800" height="900" viewBox="0 0 800 900" xmlns="http://www.w3.org/2000/svg">
            <!-- Field background -->
            <rect width="800" height="900" fill="#1a5c1a"/>
            
            <!-- Field lines -->
            <line x1="50" y1="0" x2="50" y2="900" stroke="white" stroke-width="3"/>
            <line x1="750" y1="0" x2="750" y2="900" stroke="white" stroke-width="3"/>
            <line x1="0" y1="50" x2="800" y2="50" stroke="white" stroke-width="2"/>
            <line x1="0" y1="450" x2="800" y2="450" stroke="white" stroke-width="3"/>
            <line x1="0" y1="850" x2="800" y2="850" stroke="white" stroke-width="2"/>
            
            <!-- 22m lines -->
            <line x1="0" y1="200" x2="800" y2="200" stroke="white" stroke-width="1" stroke-dasharray="5,5"/>
            <line x1="0" y1="700" x2="800" y2="700" stroke="white" stroke-width="1" stroke-dasharray="5,5"/>
            
            <!-- Halfway line circle -->
            <circle cx="400" cy="450" r="30" fill="none" stroke="white" stroke-width="2"/>
            <circle cx="400" cy="450" r="3" fill="white"/>
        """
        
        # Organize players by position
        players_by_position = {}
        for pos in POSITION_COORDS:
            players_by_position[pos] = [p for p in team_result['team'] if p.get('Position Name') == pos]
            players_by_position[pos].sort(key=lambda x: x.get('avg_points', 0), reverse=True)
        
        # Draw players
        player_id_counter = 0
        for position, coords in POSITION_COORDS.items():
            players = players_by_position.get(position, [])
            for i, coord in enumerate(coords):
                if i < len(players):
                    player = players[i]
                    x, y = coord
                    
                    nation = player.get('Club', 'Unknown')
                    nation_color = NATION_COLORS.get(nation, '#666')
                    is_captain = team_result['captain'] and team_result['captain'].get('ID') == player.get('ID')
                    
                    # Jersey circle
                    svg += f"""
            <!-- Player {player_id_counter} -->
            <circle cx="{x}" cy="{y}" r="35" fill="{nation_color}" stroke="white" stroke-width="2"/>
            <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" 
                  fill="white" font-size="11" font-weight="bold">{player.get('Name', 'N/A').split()[-1].upper()}</text>
"""
                    
                    # Captain badge
                    if is_captain:
                        svg += f"""
            <circle cx="{x+25}" cy="{y-25}" r="12" fill="#f39c12" stroke="white" stroke-width="1.5"/>
            <text x="{x+25}" y="{y-20}" text-anchor="middle" dominant-baseline="middle" 
                  fill="white" font-size="10" font-weight="bold">C</text>
"""
                    
                    # Player info below
                    svg += f"""
            <rect x="{x-45}" y="{y+40}" width="90" height="45" fill="white" stroke="white" stroke-width="1" rx="3"/>
            <text x="{x}" y="{y+52}" text-anchor="middle" font-size="10" font-weight="bold" fill="#333" dominant-baseline="middle">
                {player.get('Name', 'Unknown')[:15]}
            </text>
            <text x="{x}" y="{y+68}" text-anchor="middle" font-size="11" font-weight="bold" fill="#f39c12" dominant-baseline="middle">
                {player.get('avg_points', 0):.0f} pts
            </text>
"""
                    player_id_counter += 1
        
        svg += """
        </svg>
        """
        return svg
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Six Nations Fantasy Teams - Field View</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .teams-wrapper {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }
        
        @media (max-width: 1200px) {
            .teams-wrapper {
                grid-template-columns: 1fr;
            }
        }
        
        .team-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .team-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }
        
        .team-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .field-container {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .field-container svg {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Six Nations Fantasy Teams - Field Formation</h1>
            <p>Generated on """ + datetime.now().strftime("%B %d, %Y") + """</p>
        </div>
        
        <div class="teams-wrapper">
            <div class="team-section">
                <h2 class="team-title">TEAM 1 - PRIMARY</h2>
                <div class="team-stats">
                    <div class="stat">
                        <div class="stat-label">Total Points</div>
                        <div class="stat-value">""" + f"{team1_result['total_points']:.0f}" + """</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Avg per Player</div>
                        <div class="stat-value">""" + f"{team1_result['average_points']:.1f}" + """</div>
                    </div>
                </div>
                <div class="field-container">
""" + generate_field_svg(team1_result, "Team 1") + """
                </div>
            </div>
            
            <div class="team-section">
                <h2 class="team-title">TEAM 2 - BACKUP</h2>
                <div class="team-stats">
                    <div class="stat">
                        <div class="stat-label">Total Points</div>
                        <div class="stat-value">""" + f"{team2_result['total_points']:.0f}" + """</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Avg per Player</div>
                        <div class="stat-value">""" + f"{team2_result['average_points']:.1f}" + """</div>
                    </div>
                </div>
                <div class="field-container">
""" + generate_field_svg(team2_result, "Team 2") + """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Combined Total Points: """ + f"{team1_result['total_points'] + team2_result['total_points']:.0f}" + """</p>
        </div>
    </div>
</body>
</html>
"""
    
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved HTML teams to {output_path}")
    except Exception as e:
        print(f"Error saving HTML: {e}")
