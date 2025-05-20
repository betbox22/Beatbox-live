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
