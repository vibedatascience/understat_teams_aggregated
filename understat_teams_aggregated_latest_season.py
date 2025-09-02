import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
from datetime import datetime
import os

def get_current_season():
    """Determine current season based on date
    Football seasons run August to May
    Sept 2025 = 2025/26 season = "2025" in Understat
    """
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month >= 8:
        return str(year)
    else:
        return str(year - 1)

leagues = {
    'EPL': 'EPL',
    'La_Liga': 'La_liga',
    'Bundesliga': 'Bundesliga', 
    'Serie_A': 'Serie_A',
    'Ligue_1': 'Ligue_1',
    'RFPL': 'RFPL'
}

def scrape_team_season(league, season):
    """Scrape team statistics for a specific league and season"""
    url = f'https://understat.com/league/{league}/{season}'
    
    try:
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'lxml')
        
        # Find the script containing teamsData
        scripts = soup.find_all('script')
        json_string = ''
        
        for script in scripts:
            if 'teamsData' in str(script):
                json_string = str(script).strip()
                break
        
        if not json_string:
            return None
            
        # Extract JSON data
        start = json_string.index("('") + 2
        end = json_string.index("')")
        json_data = json_string[start:end]
        json_data = json_data.encode('utf8').decode('unicode_escape')
        data = json.loads(json_data)
        
        # Process each team
        all_teams = []
        for team_id, team_data in data.items():
            team_stats = {
                'team_id': team_id,
                'team_name': team_data['title'],
                'league': league,
                'year': int(season),
                'season': f"{season}/{str(int(season)+1)[2:]}"
            }
            
            # Get season totals from history
            if 'history' in team_data and team_data['history']:
                history = team_data['history']
                
                # Initialize counters
                totals = {
                    'matches': len(history),
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'scored': 0,
                    'conceded': 0,
                    'xG': 0,
                    'xGA': 0,
                    'npxG': 0,
                    'npxGA': 0,
                    'deep': 0,
                    'deep_allowed': 0,
                    'pts': 0,
                    'xpts': 0
                }
                
                ppda_att = []
                ppda_def = []
                oppda_att = []
                oppda_def = []
                
                # Aggregate match data
                for match in history:
                    # Count results
                    if match['result'] == 'w':
                        totals['wins'] += 1
                    elif match['result'] == 'd':
                        totals['draws'] += 1
                    else:
                        totals['losses'] += 1
                    
                    # Sum statistics
                    totals['scored'] += int(match.get('scored', 0))
                    totals['conceded'] += int(match.get('missed', 0))
                    totals['xG'] += float(match.get('xG', 0))
                    totals['xGA'] += float(match.get('xGA', 0))
                    totals['npxG'] += float(match.get('npxG', 0))
                    totals['npxGA'] += float(match.get('npxGA', 0))
                    totals['deep'] += int(match.get('deep', 0))
                    totals['deep_allowed'] += int(match.get('deep_allowed', 0))
                    totals['pts'] += int(match.get('pts', 0))
                    totals['xpts'] += float(match.get('xpts', 0))
                    
                    # PPDA calculations
                    if 'ppda' in match and match['ppda']:
                        ppda_att.append(match['ppda'].get('att', 0))
                        ppda_def.append(match['ppda'].get('def', 1))
                    
                    if 'ppda_allowed' in match and match['ppda_allowed']:
                        oppda_att.append(match['ppda_allowed'].get('att', 0))
                        oppda_def.append(match['ppda_allowed'].get('def', 1))
                
                # Calculate PPDA coefficients
                if ppda_att and ppda_def:
                    totals['ppda_coef'] = sum(ppda_att) / sum(ppda_def) if sum(ppda_def) > 0 else 0
                else:
                    totals['ppda_coef'] = 0
                    
                if oppda_att and oppda_def:
                    totals['oppda_coef'] = sum(oppda_att) / sum(oppda_def) if sum(oppda_def) > 0 else 0
                else:
                    totals['oppda_coef'] = 0
                
                # Add calculated fields
                totals['npxGD'] = totals['npxG'] - totals['npxGA']
                totals['xG_diff'] = totals['xG'] - totals['scored']
                totals['xGA_diff'] = totals['xGA'] - totals['conceded']
                totals['xpts_diff'] = totals['xpts'] - totals['pts']
                
                # Merge with team info
                team_stats.update(totals)
                all_teams.append(team_stats)
        
        return pd.DataFrame(all_teams)
        
    except Exception as e:
        print(f"Error scraping {league} {season}: {str(e)}")
        return None

current_season = get_current_season()
all_data = []

print(f"Scraping team data for {current_season} season...")

for league_name, league_code in leagues.items():
    print(f"  {league_name}...", end=" ")
    
    df = scrape_team_season(league_code, current_season)
    
    if df is not None and not df.empty:
        all_data.append(df)
        print(f"✅ {len(df)} teams")
    else:
        print("⚠️ No data")
    
    time.sleep(1.5)

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Calculate league positions
    final_df = final_df.sort_values(['league', 'pts'], ascending=[True, False])
    final_df['position'] = final_df.groupby('league').cumcount() + 1
    
    # Convert numeric columns
    numeric_cols = ['matches', 'wins', 'draws', 'losses', 'scored', 'conceded', 
                   'pts', 'deep', 'deep_allowed']
    for col in numeric_cols:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce').astype('Int64')
    
    float_cols = ['xG', 'xGA', 'npxG', 'npxGA', 'xpts', 'ppda_coef', 'oppda_coef',
                  'npxGD', 'xG_diff', 'xGA_diff', 'xpts_diff']
    for col in float_cols:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
    
    final_df['scrape_timestamp'] = datetime.now().isoformat()
    
    # Save current season files
    filename = f'understat_teams_aggregated_{current_season}_latest.parquet'
    final_df.to_parquet(filename, compression='snappy', index=False)
    
    csv_filename = f'understat_teams_aggregated_{current_season}_latest.csv'
    final_df.to_csv(csv_filename, index=False)
    
    print(f"\nSaved current season: {csv_filename}")
    
    # Append to historical data if it exists
    historical_file = 'understat_teams_aggregated_2014_2024.csv'
    if os.path.exists(historical_file):
        historical_df = pd.read_csv(historical_file, low_memory=False)
        
        # Ensure team_id is string in both datasets
        historical_df['team_id'] = historical_df['team_id'].astype(str)
        final_df['team_id'] = final_df['team_id'].astype(str)
        
        # Combine historical with current season
        combined_df = pd.concat([historical_df, final_df], ignore_index=True)
        
        # Save combined data
        combined_csv = 'understat_teams_aggregated_2014_td.csv'
        combined_parquet = 'understat_teams_aggregated_2014_td.parquet'
        
        combined_df.to_csv(combined_csv, index=False)
        combined_df.to_parquet(combined_parquet, compression='snappy', index=False)
        
        print(f"Saved combined data: {combined_csv}")
        print(f"Total records: {len(combined_df)}")
    else:
        print(f"Historical file not found: {historical_file}")