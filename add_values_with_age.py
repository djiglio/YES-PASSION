import os
import json
import random

data_dir = os.path.join(os.path.dirname(__file__), 'data', 'seasons')

# Seed so results are reproducible
random.seed(101)

# Global dict to store birth years for consistency across seasons
birth_years = {}

def calculate_value_and_age(name, ovr, season_year):
    try:
        ovr = int(ovr)
    except:
        return "€0", 0, 25
        
    # Generate consistent age
    if name not in birth_years:
        # Base age when we first see them
        base_age = random.randint(18, 34)
        if ovr >= 88:
            base_age = random.randint(24, 32) # Superstars are rarely 18
        birth_years[name] = season_year - base_age
        
    age = season_year - birth_years[name]
    
    # Cap age to realistic bounds if they somehow persist too long
    if age < 16: age = 16
    if age > 42: age = 42
        
    val = 0
    if ovr >= 90:
        val = 60 + (ovr - 90) * 15
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
        
    # Age multiplier
    if age <= 21:
        val *= 1.6
    elif age <= 24:
        val *= 1.2
    elif age <= 28:
        val *= 1.0
    elif age <= 31:
        val *= 0.7
    else:
        val *= 0.4
        
    variance = (random.random() * 0.1) - 0.05
    val = val * (1 + variance)
    
    numeric_val = val * 1000000
    
    if val >= 1:
        formatted = f"€{round(val, 1)}M"
    else:
        formatted = f"€{int(round(val * 1000))}K"
        
    return formatted, numeric_val, age

all_players = []

# Sort files to process them chronologically to set birth years correctly
files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])

for filename in files:
    season_id = filename.split('_')[1].split('.')[0]
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    season_name = data.get('season_name', f"20{season_id}")
    season_year = int("20" + season_id)
        
    if 'teams' in data:
        for team in data['teams']:
            if 'players' in team:
                for player in team['players']:
                    ovr = player.get('Overall', 0)
                    formatted_val, num_val, age = calculate_value_and_age(player['Nome'], ovr, season_year)
                    player['Value'] = formatted_val
                    player['ValueNum'] = num_val
                    player['Age'] = age
                    
                    all_players.append({
                        'name': player['Nome'],
                        'club': team['name'],
                        'season': season_name,
                        'ovr': ovr,
                        'age': age,
                        'val_num': num_val,
                        'val_str': formatted_val
                    })
                    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Find top 5
all_players.sort(key=lambda x: x['val_num'], reverse=True)
print("TOP 5 PLAYERS:")
for i in range(5):
    p = all_players[i]
    print(f"{i+1}. {p['name']} ({p['club']}) - Season: {p['season']} | OVR: {p['ovr']} | Age: {p['age']} | Value: {p['val_str']}")
