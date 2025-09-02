#!/bin/bash

# Set up the environment
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Change to the correct directory
cd /Users/rchaudhary/understat_teams_data

# Log file for debugging
LOG_FILE="/Users/rchaudhary/understat_teams_data/cron_log.txt"

# Start logging
echo "=== Starting daily update at $(date) ===" >> "$LOG_FILE"

# Run the Python script
echo "Running Python script..." >> "$LOG_FILE"
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/rchaudhary/understat_teams_data/understat_teams_aggregated_latest_season.py >> "$LOG_FILE" 2>&1

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "Python script completed successfully" >> "$LOG_FILE"
    
    # Add, commit and push to GitHub
    echo "Pushing to GitHub..." >> "$LOG_FILE"
    git add . >> "$LOG_FILE" 2>&1
    git commit -m "Daily update: $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "Successfully pushed to GitHub" >> "$LOG_FILE"
    else
        echo "Failed to push to GitHub" >> "$LOG_FILE"
    fi
else
    echo "Python script failed" >> "$LOG_FILE"
fi

echo "=== Update completed at $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"