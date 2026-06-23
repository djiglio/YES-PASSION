import os
import json
import random

data_dir = os.path.join(os.path.dirname(__file__), 'data', 'seasons')

def calculate_value(ovr):
    try:
        ovr = int(ovr)
    except:
        return "€0"
        
    val = 0
    if ovr >= 90:
        val = 60 + (ovr - 90) * 10
    elif ovr >= 85:
        val = 25 + (ovr - 85) * 7
    elif ovr >= 80:
        val = 12 + (ovr - 80) * 2.5
    elif ovr >= 75:
        val = 4 + (ovr - 75) * 1.5
    elif ovr >= 70:
        val = 1.5 + (ovr - 70) * 0.5
    elif ovr >= 65:
        val = 0.5 + (ovr - 65) * 0.2
    else:
        val = 0.2
        
    variance = (random.random() * 0.2) - 0.1
    val = val * (1 + variance)
    
    if val >= 1:
        return f"€{round(val, 1)}M"
    else:
        return f"€{int(round(val * 1000))}K"

for filename in os.listdir(data_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'teams' in data:
            for team in data['teams']:
                if 'players' in team:
                    for player in team['players']:
                        player['Value'] = calculate_value(player.get('Overall', 0))
                        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Updated {filename}")
