# Import required libraries
from flask import Flask, jsonify, request, send_from_directory
import requests
import os
import json
import time
import tempfile
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with static files in the root directory
app = Flask(__name__, static_folder='.', static_url_path='')

# API configuration
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # Sport code for basketball

# Function to get storage directory
def get_storage_dir():
    # Check if we're on Render server
    if 'RENDER' in os.environ:
        # Use temporary directory
        return tempfile.gettempdir()
    else:
        # Use current directory
        return '.'

# Location of history and opportunities files
LINES_HISTORY_FILE = os.path.join(get_storage_dir(), 'lines_history.json')
OPPORTUNITIES_FILE = os.path.join(get_storage_dir(), 'opportunities.json')

# Configuration validation
def validate_configuration():
    issues = []
    
    # Check API URL
    if not B365_API_URL or not B365_API_URL.startswith("http"):
        issues.append(f"Invalid API URL: {B365_API_URL}")
    
    # Check token
    if not B365_TOKEN or len(B365_TOKEN) < 10:
        issues.append(f"Invalid API token: {B365_TOKEN}")
    
    # Check write permissions to history files
    storage_dir = get_storage_dir()
    test_file = os.path.join(storage_dir, "test_write.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        issues.append(f"Write permission issue in directory {storage_dir}: {str(e)}")
    
    if issues:
        for issue in issues:
            logger.error(f"Configuration issue: {issue}")
        return False
    
    logger.info("Configuration validation successful")
    return True

# Run configuration validation
is_config_valid = validate_configuration()

# Function to save game lines history
def save_game_lines(game_id, lines_data):
    try:
        # Check if parent directory exists
        parent_dir = os.path.dirname(LINES_HISTORY_FILE)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Load existing history
        history = {}
        if os.path.exists(LINES_HISTORY_FILE):
            try:
                with open(LINES_HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                history = {}
        
        # Save new line data
        if game_id not in history:
            history[game_id] = []
        
        # Check if the data has changed since the last update
        changed = True  # Default: assume change
        
        if history[game_id]:
            last_entry = history[game_id][-1]
            # Compare important values
            changed = (
                last_entry.get('spread') != lines_data.get('spread') or
                last_entry.get('total') != lines_data.get('total') or
                last_entry.get('time_status') != lines_data.get('time_status')
            )
        
        if not changed:
            return False
        
        # Add line data with timestamp
        lines_data['timestamp'] = datetime.now().isoformat()
        history[game_id].append(lines_data)
        
        # Save to file
        with open(LINES_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        
        return True
    except Exception as e:
        logger.error(f"Error saving line data: {str(e)}")
        # If error, return True to continue processing
        return True

# Function to get game lines history
def get_game_lines_history(game_id):
    try:
        if not os.path.exists(LINES_HISTORY_FILE):
            return []
        
        with open(LINES_HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        return history.get(game_id, [])
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logger.error(f"Error reading lines history: {str(e)}")
        return []

# Function to save opportunities
def save_opportunity(game_id, opportunity_data):
    try:
        # Check if parent directory exists
        parent_dir = os.path.dirname(OPPORTUNITIES_FILE)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Load existing opportunities
        opportunities = {}
        if os.path.exists(OPPORTUNITIES_FILE):
            try:
                with open(OPPORTUNITIES_FILE, 'r') as f:
                    opportunities = json
