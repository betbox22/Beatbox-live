# Import required libraries
from flask import Flask, jsonify, request, send_from_directory
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')

# API configuration
API_TOKEN = "219761-iALwqep7Hy1aCl"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/health')
def health_check():
    """System health check"""
    return jsonify({
        "status": "ok",
        "environment": "production" if 'RENDER' in os.environ else "development",
        "timestamp": time.time()
    })

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('.', path)

# Start the application when run directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
# הוסף אחרי שורות הייבוא הקיימות
import json
import tempfile
from datetime import datetime

# API configuration - עדכן את זה במקום מה שכבר יש
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # Sport code for basketball

# Function to get storage directory - הוסף אחרי הגדרות ה-API
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
