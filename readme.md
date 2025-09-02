
# Understat Football Team Statistics Dataset

## Overview
Comprehensive football team statistics from Europe's top 6 leagues, sourced from Understat.com. Contains detailed team performance metrics including goals, expected goals (xG), league standings, and advanced analytics.

## Files

| File | Coverage | Description |
|------|----------|-------------|
| `understat_teams_aggregated_2014_2024.csv` | 2014/15 - 2024/25 | Historical data for 11 complete seasons |
| `understat_teams_aggregated_2025_latest.csv` | 2025/26 only | Current season in progress (updated daily) |
| `understat_teams_aggregated_2014_td.csv` | 2014/15 - current | Complete dataset including latest matches (updated daily) |

*Parquet versions also available for all files (70% smaller, faster loading)*

## Quick Start

### Load Data Directly from GitHub

```python
import pandas as pd

# For historical analysis (complete seasons only)
historical = pd.read_csv('https://raw.githubusercontent.com/vibedatascience/understat_teams_aggregated/main/understat_teams_aggregated_2014_2024.csv')

# For current season tracking
current = pd.read_csv('https://raw.githubusercontent.com/vibedatascience/understat_teams_aggregated/main/understat_teams_aggregated_2025_latest.csv')

# For complete dataset
full = pd.read_csv('https://raw.githubusercontent.com/vibedatascience/understat_teams_aggregated/main/understat_teams_aggregated_2014_td.csv')
```

### Load Local Files

```python
import pandas as pd

# For historical analysis (complete seasons only)
historical = pd.read_csv('understat_teams_aggregated_2014_2024.csv')

# For current season tracking
current = pd.read_csv('understat_teams_aggregated_2025_latest.csv')

# For complete dataset
full = pd.read_csv('understat_teams_aggregated_2014_td.csv')
```

## Coverage Details

### League Codes
- **EPL** - English Premier League
- **La_Liga** - Spanish La Liga  
- **Bundesliga** - German Bundesliga
- **Serie_A** - Italian Serie A
- **Ligue_1** - French Ligue 1
- **RFPL** - Russian Premier League

### Seasons
- **Historical**: 2014/15 through 2024/25 (11 complete seasons)
- **Current**: 2025/26 (in progress)
- **Records**: ~1,320 team-season combinations
- **Unique Teams**: ~140 clubs

## Data Dictionary

### Core Columns

| Column | Type | Description |
|--------|------|-------------|
| `team_id` | str | Unique team ID from Understat |
| `team_name` | str | Team/club name |
| `league` | str | League code (see league codes above) |
| `year` | int | Season start year (e.g., 2024 for 2024/25) |
| `season` | str | Display format (e.g., "2024/25") |
| `position` | int | Final league position (1-20) |

### Performance Metrics

| Column | Type | Description |
|--------|------|-------------|
| `matches` | int | Matches played |
| `wins` | int | Matches won |
| `draws` | int | Matches drawn |
| `losses` | int | Matches lost |
| `pts` | int | Points earned |
| `scored` | int | Goals scored |
| `conceded` | int | Goals conceded |

### Expected Goals Metrics

| Column | Type | Description |
|--------|------|-------------|
| `xG` | float | Expected goals for |
| `xGA` | float | Expected goals against |
| `npxG` | float | Non-penalty expected goals for |
| `npxGA` | float | Non-penalty expected goals against |
| `npxGD` | float | Non-penalty xG difference |
| `xpts` | float | Expected points |

### Advanced Metrics

| Column | Type | Description |
|--------|------|-------------|
| `ppda_coef` | float | Passes allowed per defensive action (lower = more intense pressing) |
| `oppda_coef` | float | Opponent's passes per defensive action against this team |
| `deep` | int | Passes completed within 20 meters of opposition goal |
| `deep_allowed` | int | Opposition passes completed within 20 meters of this team's goal |

### Performance Differences

| Column | Type | Description |
|--------|------|-------------|
| `xG_diff` | float | xG minus actual goals (positive = underperformed scoring) |
| `xGA_diff` | float | xGA minus actual goals conceded (positive = conceded fewer than expected) |
| `xpts_diff` | float | Expected points minus actual points (positive = underperformed) |

### Metadata

| Column | Type | Description |
|--------|------|-------------|
| `scrape_timestamp` | str | Data collection time |

## Critical Usage Guidelines

### Team Identification

Teams may change names over time or have similar names. Use the `team_id` column for consistent tracking across seasons.

```python
# CORRECT - Use team ID for tracking
team_data = df[df['team_id'] == '89']
team_name = team_data['team_name'].iloc[0]

# ACCEPTABLE - Team names are more unique than player names
team_data = df[df['team_name'] == 'Liverpool']
```

### Promoted/Relegated Teams

Teams appear in different leagues across seasons due to promotion/relegation. A team may have records in multiple leagues.

```python
# Example: Check which leagues a team has played in
team_leagues = df[df['team_name'] == 'Leicester'].groupby('league').size()
```

## Data Quality Notes

1. **Current Season**: 2025/26 data is partial (season in progress)
2. **League Size**: Most leagues have 20 teams, Bundesliga has 18
3. **Missing Teams**: Some teams may be missing if relegated or not in top division
4. **Position**: Calculated based on points; ties broken by goal difference in source data

## File Formats

All datasets are available in both CSV and Parquet formats:
- **CSV**: Universal compatibility, human-readable
- **Parquet**: 70% smaller file size, faster loading with pandas

## Data Source

Data sourced from [Understat.com](https://understat.com/), a leading football analytics platform providing expected goals (xG) and other advanced metrics.
