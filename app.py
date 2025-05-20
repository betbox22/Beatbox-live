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
                    opportunities = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                opportunities = {}
        
        # Save new opportunity data
        opportunities[game_id] = opportunity_data
        
        # Save to file
        with open(OPPORTUNITIES_FILE, 'w') as f:
            json.dump(opportunities, f)
        
        return True
    except Exception as e:
        logger.error(f"Error saving opportunity data: {str(e)}")
        return False

# Function to get opportunity
def get_opportunity(game_id):
    try:
        if not os.path.exists(OPPORTUNITIES_FILE):
            return None
        
        with open(OPPORTUNITIES_FILE, 'r') as f:
            opportunities = json.load(f)
        
        return opportunities.get(game_id, None)
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logger.error(f"Error reading opportunity data: {str(e)}")
        return None
# Function to extract line data from a game
def extract_lines_from_game(game):
    """
    Extract line data from a game - adapt to B365 data structure
    Returns an object with spread and total data
    """
    lines_data = {
        'spread': None,
        'total': None,
        'time_status': game.get('time_status'),
        'timestamp': datetime.now().isoformat(),
        'quarter': None,
        'time_remaining': None
    }
    
    # Extract quarter and game clock info
    if 'timer' in game:
        timer = game.get('timer', {})
        lines_data['quarter'] = timer.get('q')
        lines_data['time_remaining'] = timer.get('tm')
    
    # Extract line data directly from odds if available
    if 'odds' in game:
        for market_type, market_data in game['odds'].items():
            # Search for spread market in B365 format
            if market_type in ['handicap', 'handicap_line', 'ah', 'point_spread']:
                try:
                    handicap_val = float(market_data)
                    lines_data['spread'] = handicap_val
                except (ValueError, TypeError):
                    pass
            
            # Search for total market in B365 format
            elif market_type in ['total', 'total_line', 'ou']:
                try:
                    total_val = float(market_data)
                    lines_data['total'] = total_val
                except (ValueError, TypeError):
                    pass
    
    # Handle direct selection data from extra fields
    if not lines_data['spread'] and 'extra' in game:
        extra = game.get('extra', {})
        if 'handicap' in extra:
            try:
                lines_data['spread'] = float(extra['handicap'])
            except (ValueError, TypeError):
                pass
    
    # Handle other odds formats
    if not lines_data['spread'] and 'odds' in game:
        for key, value in game['odds'].items():
            if 'ah_home' in key or 'handicap_home' in key:
                try:
                    lines_data['spread'] = float(value)
                    break
                except (ValueError, TypeError):
                    pass
    
    # Extract total from alternate formats
    if not lines_data['total'] and 'odds' in game:
        for key, value in game['odds'].items():
            if 'total' in key.lower() and 'over' in key.lower():
                try:
                    lines_data['total'] = float(value)
                    break
                except (ValueError, TypeError):
                    pass
    
    # Estimate from score if needed
    if (not lines_data['spread'] or not lines_data['total']) and 'ss' in game:
        try:
            scores = game['ss'].split('-')
            home_score = int(scores[0].strip())
            away_score = int(scores[1].strip())
            
            # Calculate spread from score if needed
            if not lines_data['spread']:
                score_diff = home_score - away_score
                if score_diff > 0:
                    lines_data['spread'] = round(score_diff + 3.5, 1)
                else:
                    lines_data['spread'] = round(score_diff - 3.5, 1)
            
            # Calculate total from score and quarter if needed
            if not lines_data['total']:
                current_total = home_score + away_score
                quarter = int(lines_data['quarter'] or 0)
                
                if quarter > 0:
                    estimated_final = current_total * (4 / quarter)
                    lines_data['total'] = round(estimated_final * 1.05, 1)
        except (ValueError, IndexError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating lines from score: {str(e)}")
    
    # Use league averages if needed
    if not lines_data['total'] and 'league' in game:
        league_name = game.get('league', {}).get('name', '').lower()
        
        # Default totals by league
        league_average_points = {
            'nba': 224.5,
            'euroleague': 158.5,
            'eurocup': 162.0,
            'spain': 156.0,
            'greece': 150.0,
            'italy': 154.0,
            'israel': 160.0,
            'turkey': 158.0,
            'lithuania': 152.0,
            'germany': 158.0,
            'france': 152.0,
            'portugal': 150.0,
            'qatar': 148.0
        }
        
        default_total = 155.0
        
        # Match league
        for league_key, avg_points in league_average_points.items():
            if league_key in league_name:
                lines_data['total'] = avg_points
                break
        
        # Default if no match
        if not lines_data['total']:
            lines_data['total'] = default_total
    
    # Round to nearest half point
    if lines_data['spread']:
        lines_data['spread'] = round(lines_data['spread'] * 2) / 2
    
    if lines_data['total']:
        lines_data['total'] = round(lines_data['total'] * 2) / 2
    
    return lines_data

# Function to calculate opportunities
def calculate_opportunities(game_id, current_lines):
    try:
        history = get_game_lines_history(game_id)
        
        if not history or len(history) < 2:
            return None
        
        # Get opening line (first in history)
        opening_lines = history[0]
        
        # Current
        current_spread = current_lines.get('spread')
        current_total = current_lines.get('total')
        
        # Opening
        opening_spread = opening_lines.get('spread')
        opening_total = opening_lines.get('total')
        
        # Calculate differences
        spread_diff = 0
        total_diff = 0
        
        if current_spread is not None and opening_spread is not None:
            spread_diff = current_spread - opening_spread
        
        if current_total is not None and opening_total is not None:
            total_diff = current_total - opening_total
        
        # Identify opportunities based on rules
        opportunity_type = 'neutral'
        opportunity_reason = ''
        
        if abs(spread_diff) >= 7:
            opportunity_type = 'green'
            opportunity_reason = f'Significant spread movement: {spread_diff:.1f} points'
        elif abs(total_diff) >= 10:
            opportunity_type = 'green'
            opportunity_reason = f'Significant total movement: {total_diff:.1f} points'
        
        return {
            'type': opportunity_type,
            'reason': opportunity_reason,
            'spread_diff': spread_diff,
            'total_diff': total_diff,
            'time_status': current_lines.get('time_status'),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating opportunities for game {game_id}: {str(e)}")
        return {
            'type': 'neutral',
            'reason': '',
            'spread_diff': 0,
            'total_diff': 0,
            'time_status': current_lines.get('time_status'),
            'timestamp': datetime.now().isoformat()
        }
# Function to add opportunity and line info to a game
def add_opportunity_and_lines_to_game(game, opportunity):
    try:
        history = get_game_lines_history(game.get('id', ''))
        
        # Add line information
        if history:
            # Opening line (first in history)
            opening_lines = history[0]
            
            # Start line (if available)
            start_lines = history[1] if len(history) > 1 else opening_lines
            
            # Current line (last in history)
            current_lines = history[-1]
            
            # Add line data to game
            game['opening_spread'] = opening_lines.get('spread')
            game['opening_total'] = opening_lines.get('total')
            
            game['start_spread'] = start_lines.get('spread')
            game['start_total'] = start_lines.get('total')
            
            game['live_spread'] = current_lines.get('spread')
            game['live_total'] = current_lines.get('total')
            
            # Calculate differences
            if game['opening_spread'] is not None and game['live_spread'] is not None:
                game['live_spread_diff'] = game['live_spread'] - game['opening_spread']
            else:
                game['live_spread_diff'] = 0
                
            if game['opening_total'] is not None and game['live_total'] is not None:
                game['live_total_diff'] = game['live_total'] - game['opening_total']
            else:
                game['live_total_diff'] = 0
                
            # Set movement direction
            game['spread_direction'] = 'up' if game.get('live_spread_diff', 0) > 0 else 'down' if game.get('live_spread_diff', 0) < 0 else 'neutral'
            game['total_direction'] = 'up' if game.get('live_total_diff', 0) > 0 else 'down' if game.get('live_total_diff', 0) < 0 else 'neutral'
            
            # Mark significant changes
            game['spread_flag'] = 'green' if abs(game.get('live_spread_diff', 0)) >= 7 else 'neutral'
            game['ou_flag'] = 'green' if abs(game.get('live_total_diff', 0)) >= 10 else 'neutral'
            
            # Mark opening vs start
            if game['opening_spread'] is not None and game['start_spread'] is not None:
                opening_vs_start_spread = game['start_spread'] - game['opening_spread']
                game['opening_vs_start'] = 'green' if abs(opening_vs_start_spread) >= 1 else 'neutral'
            else:
                game['opening_vs_start'] = 'neutral'
        else:
            # If no history, set default values
            game['opening_spread'] = None
            game['opening_total'] = None
            game['start_spread'] = None
            game['start_total'] = None
            game['live_spread'] = None
            game['live_total'] = None
            game['live_spread_diff'] = 0
            game['live_total_diff'] = 0
            game['spread_direction'] = 'neutral'
            game['total_direction'] = 'neutral'
            game['spread_flag'] = 'neutral'
            game['ou_flag'] = 'neutral'
            game['opening_vs_start'] = 'neutral'
        
        # Add opportunity information
        if opportunity:
            game['opportunity_type'] = opportunity.get('type', 'neutral')
            game['opportunity_reason'] = opportunity.get('reason', '')
        else:
            game['opportunity_type'] = 'neutral'
            game['opportunity_reason'] = ''
    except Exception as e:
        logger.error(f"Error adding info to game: {str(e)}")
        # Set default values
        game['opportunity_type'] = 'neutral'
        game['opportunity_reason'] = ''
# המשך מהחלק הקודם שכבר הוספת
@app.route('/api/stats')
def get_stats():
    # Calculate statistics from opportunities
    try:
        opportunities = {}
        if os.path.exists(OPPORTUNITIES_FILE):
            try:
                with open(OPPORTUNITIES_FILE, 'r') as f:
                    opportunities = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                opportunities = {}
        
        # Count opportunities by type
        green_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'green')
        red_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'red')
        blue_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'blue')
        
        # Calculate opportunity percentage
        total_opportunities = green_opportunities + red_opportunities + blue_opportunities
        total_games = max(len(opportunities), 1)  # Prevent division by zero
        opportunity_percentage = round((total_opportunities / total_games * 100) if total_games > 0 else 0)
        
        # Count live and upcoming games from real-time API data
        total_live = 0
        total_upcoming = 0
        
        try:
            # Call the API to get current game data
            params = {
                "sport_id": SPORT_ID,
                "token": B365_TOKEN
            }
            response = requests.get(B365_API_URL, params=params, timeout=10)
            if response.status_code == 200:
                games_data = response.json()
                if 'results' in games_data:
                    # Count games by status
                    for game in games_data['results']:
                        status = game.get('time_status')
                        if status == '1':  # Live game
                            total_live += 1
                        elif status == '0':  # Upcoming game
                            total_upcoming += 1
        except Exception as e:
            logger.error(f"Error counting games: {str(e)}")
            # If error, show at least the number of games in our history
            total_live = sum(1 for game_id, opps in opportunities.items() if opps.get('time_status') == '1')
            total_upcoming = sum(1 for game_id, opps in opportunities.items() if opps.get('time_status') == '0')
        
        stats = {
            "opportunity_percentage": opportunity_percentage,
            "green_opportunities": green_opportunities,
            "red_opportunities": red_opportunities,
            "blue_opportunities": blue_opportunities,
            "total_live": total_live,
            "total_upcoming": total_upcoming
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        return jsonify({
            "opportunity_percentage": 0,
            "green_opportunities": 0,
            "red_opportunities": 0,
            "blue_opportunities": 0,
            "total_live": 0,
            "total_upcoming": 0
        })

@app.route('/api/check-b365')
def check_b365():
    """Manual check of B365 API"""
    try:
        logger.info("Starting manual check of B365 API")
        response = requests.get(B365_API_URL, params={"token": B365_TOKEN, "sport_id": SPORT_ID}, timeout=10)
        
        logger.info(f"Received response with status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and data['results']:
                live_count = sum(1 for g in data['results'] if g.get('time_status') == '1')
                upcoming_count = sum(1 for g in data['results'] if g.get('time_status') == '0')
                
                return jsonify({
                    "status": "ok",
                    "total_games": len(data['results']),
                    "live_games": live_count,
                    "upcoming_games": upcoming_count,
                    "first_game_sample": data['results'][0] if data['results'] else None,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({
                    "status": "no_games",
                    "message": "API connection successful but no games found",
                    "raw_response": data,
                    "timestamp": datetime.now().isoformat()
                })
        else:
            return jsonify({
                "status": "error",
                "message": f"Error connecting to API: {response.status_code}",
                "response_text": response.text[:500],
                "timestamp": datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error in check: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

# שים לב אם כבר יש לך נתיב דומה, החלף אותו במקום להוסיף
@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('.', path)

# אם כבר יש לך את החלק הזה, אל תוסיף שוב
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
