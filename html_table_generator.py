#!/usr/bin/env python3
"""
Six Nations Fantasy Rugby HTML Table Visualization
Generates HTML table output for team rosters using Jinja2 templates
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Nation/Club colors
NATION_COLORS = {
    "England": "#f0f0f0",
    "France": "#0062be",
    "Ireland": "#00a194",
    "Italy": "#5095ff",
    "Scotland": "#2d326a",
    "Wales": "#ff0019",
}


def save_team_to_html_table(team_result: Dict[str, Any], filename: str = "data/selected_team_table.html"):
    """
    Save team to HTML file as a formatted table using Jinja2 template
    
    Args:
        team_result: Team result dictionary
        filename: Output HTML filename
    """
    
    # All 6 nations in order
    ALL_NATIONS = ["England", "France", "Ireland", "Italy", "Scotland", "Wales"]
    
    # Calculate nation breakdown
    nation_counts = {}
    for player in team_result['team']:
        nation = player.get('Club', 'Unknown')
        nation_counts[nation] = nation_counts.get(nation, 0) + 1
    
    # Ensure all nations are in the dict (with 0 if not present)
    for nation in ALL_NATIONS:
        if nation not in nation_counts:
            nation_counts[nation] = 0
    
    # Custom sort with proper rugby numbering
    position_order = {
        "Second Row": 0,
        "Back Row": 1,
        "Scrum Half": 2,
        "Fly Half": 3,
        "Back Three": 4,  # One will be 11
        "Centre": 5,      # 12, 13
        # Remaining Back Three will be 14, 15
    }
    
    props = [p for p in team_result['team'] if p.get('Position Name') == 'Prop']
    hookers = [p for p in team_result['team'] if p.get('Position Name') == 'Hooker']
    back_three = [p for p in team_result['team'] if p.get('Position Name') == 'Back Three']
    centres = [p for p in team_result['team'] if p.get('Position Name') == 'Centre']
    
    rest = sorted(
        [p for p in team_result['team'] if p.get('Position Name') not in ['Prop', 'Hooker', 'Back Three', 'Centre']],
        key=lambda p: position_order.get(p.get('Position Name', 'Unknown'), 999)
    )
    
    # Build team: 1-3 (front row), 4-5 (second row), 6-8 (back row), 
    # 9 (scrum half), 10 (fly half), 11 (back three), 12-13 (centres), 14-15 (back three)
    sorted_team = (
        props[:1] + hookers + props[1:] +  # 1, 2, 3
        rest +                              # 4-10 (second row, back row, scrum half, fly half)
        back_three[:1] +                    # 11 (one back three)
        centres +                           # 12, 13
        back_three[1:]                      # 14, 15 (remaining back three)
    )
    
    # Set up Jinja2 environment
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('team_table_template.html')
    
    # Render template with data
    html_content = template.render(
        generated_date=datetime.now().strftime("%B %d, %Y"),
        total_points=team_result['total_points'],
        avg_points=team_result['average_points'],
        max_points=team_result['max_points'],
        sorted_team=sorted_team,
        captain=team_result['captain'],
        all_nations=ALL_NATIONS,
        nation_counts=nation_counts,
        nation_colors=NATION_COLORS,
    )
    
    # Write to file
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved HTML table to {output_path}")
    except Exception as e:
        print(f"Error saving HTML table: {e}")
