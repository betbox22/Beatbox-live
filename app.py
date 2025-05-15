from flask import Flask, jsonify, request, send_from_directory
import requests
import os
import json
import time
from datetime import datetime
import threading
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("betbox.log"), logging.StreamHandler()]
)
logger = logging.getLogger("betbox")

app = Flask(__name__)

# קונפיגורציה
API_TOKEN = os.environ.get('API_TOKEN', '219761-iALwqep7Hy1aCl')
API_BASE_URL = "https://api.b365api.com/v3"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# מאגרי נתונים זמניים
games_data = {}          # מידע כללי על משחקים
opening_lines = {}       # ליין פתיחה ראשוני
current_lines = {}       # ליין נוכחי לפני המשחק
starting_lines = {}      # ליין בזמן תחילת המשחק (נעול)
live_lines = {}          # ליין בזמן אמת

# מנעול למניעת התנגשויות
data_lock = threading.Lock()

# פונקציות עזר לשמירה וטעינה
def save_data(data, filename):
    """שמירת נתונים לקובץ JSON"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f)

def load_data(filename):
    """טעינת נתונים מקובץ JSON"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# טעינת נתונים קיימים בעת הפעלת השרת
def load_all_data():
    global games_data, opening_lines, current_lines, starting_lines, live_lines
    games_data = load_data('games_data.json')
    opening_lines = load_data('opening_lines.json')
    current_lines = load_data('current_lines.json')
    starting_lines = load_data('starting_lines.json')
    live_lines = load_data('live_lines.json')

# שמירת כל הנתונים
def save_all_data():
    save_data(games_data, 'games_data.json')
    save_data(opening_lines, 'opening_lines.json')
    save_data(current_lines, 'current_lines.json')
    save_data(starting_lines, 'starting_lines.json')
    save_data(live_lines, 'live_lines.json')

# פונקציות לאיסוף נתונים
def fetch_upcoming_games():
    """מביא משחקים קרובים מה-API"""
    try:
        url = f"{API_BASE_URL}/events/upcoming"
        params = {"token": API_TOKEN}
        response = requests.get(url, params=params)
        return response.json().get('results', [])
    except Exception as e:
        logger.error(f"Error fetching upcoming games: {str(e)}")
        return []

def fetch_inplay_games():
    """מביא משחקים חיים מה-API"""
    try:
        url = f"{API_BASE_URL}/events/inplay"
        params = {"token": API_TOKEN}
        response = requests.get(url, params=params)
        return response.json().get('results', [])
    except Exception as e:
        logger.error(f"Error fetching inplay games: {str(e)}")
        return []

def fetch_odds(game_id):
    """מביא יחסי הימור עבור משחק"""
    try:
        # בפועל יש לקרוא ל-API אמיתי
        # זו פונקציית דמה למטרות הדגמה
        import random
        
        if game_id in opening_lines:
            base_spread = opening_lines[game_id].get('spread', 0)
            base_total = opening_lines[game_id].get('total', 180)
        else:
            base_spread = -5 + random.uniform(-3, 3)
            base_total = 180 + random.uniform(-10, 10)
        
        # הוסף שינוי רנדומלי קטן לדמות שינויים בליין
        spread = base_spread + random.uniform(-1, 1)
        total = base_total + random.uniform(-3, 3)
        
        return {
            'spread': round(spread, 1),
            'total': round(total, 1)
        }
    except Exception as e:
        logger.error(f"Error fetching odds for game {game_id}: {str(e)}")
        return {}

# פונקציות עדכון
def daily_games_scan():
    """סורק משחקים חדשים פעם ביום"""
    logger.info("Performing daily games scan...")
    games = fetch_upcoming_games()
    
    with data_lock:
        for game in games:
            game_id = game.get('id')
            
            # אם המשחק חדש, הוסף אותו
            if game_id not in games_data:
                games_data[game_id] = {
                    'id': game_id,
                    'sport_id': game.get('sport_id'),
                    'league': game.get('league', {}).get('name', ''),
                    'home': game.get('home', {}).get('name', ''),
                    'away': game.get('away', {}).get('name', ''),
                    'time': game.get('time'),
                    'status': 'upcoming'
                }
                
                # שמור את ליין הפתיחה
                odds = fetch_odds(game_id)
                opening_lines[game_id] = odds
                current_lines[game_id] = odds.copy()
                
        save_all_data()

def update_pregame_lines():
    """מעדכן ליינים של משחקים לפני תחילתם"""
    logger.info("Updating pregame lines...")
    
    with data_lock:
        for game_id, game in list(games_data.items()):
            if game['status'] == 'upcoming':
                new_odds = fetch_odds(game_id)
                current_lines[game_id] = new_odds
        
        save_data(current_lines, 'current_lines.json')

def monitor_live_games():
    """מנטר משחקים חיים"""
    logger.info("Monitoring live games...")
    live_games = fetch_inplay_games()
    
    with data_lock:
        for game in live_games:
            game_id = game.get('id')
            
            # אם המשחק קיים
            if game_id in games_data:
                # אם המשחק הפך עכשיו לחי, נעל את ליין ההתחלה
                if games_data[game_id]['status'] != 'live':
                    games_data[game_id]['status'] = 'live'
                    starting_lines[game_id] = current_lines.get(game_id, {}).copy()
                
                # עדכון מידע בסיסי
                games_data[game_id]['score'] = game.get('ss', '0-0')
                games_data[game_id]['timer'] = game.get('timer', {})
                
                # עדכון ליין לייב
                live_odds = fetch_odds(game_id)
                live_lines[game_id] = live_odds
        
        save_data(games_data, 'games_data.json')
        save_data(starting_lines, 'starting_lines.json')
        save_data(live_lines, 'live_lines.json')

def detect_opportunities(game_id):
    """מזהה הזדמנויות בהימורים"""
    if game_id not in games_data:
        return {"type": "neutral", "reason": ""}
    
    game = games_data[game_id]
    opening = opening_lines.get(game_id, {})
    live = live_lines.get(game_id, {})
    
    if game['status'] == 'live' and opening and live:
        # חישוב שינויים בספרד
        spread_diff = live.get('spread', 0) - opening.get('spread', 0)
        total_diff = live.get('total', 0) - opening.get('total', 0)
        
        # דוגמאות להזדמנויות
        if abs(spread_diff) >= 7:
            return {
                "type": "green",
                "reason": "שינוי משמעותי בקו הספרד"
            }
        elif abs(total_diff) >= 15:
            return {
                "type": "green",
                "reason": "שינוי משמעותי בקו הטוטאל"
            }
        elif abs(spread_diff) >= 4:
            return {
                "type": "blue",
                "reason": "שינוי מתון בקו הספרד"
            }
        elif abs(total_diff) >= 8:
            return {
                "type": "blue",
                "reason": "שינוי מתון בקו הטוטאל"
            }
    
    return {"type": "neutral", "reason": ""}

# תהליכי רקע
def start_background_tasks():
    # הפעל את הסריקה היומית
    daily_thread = threading.Thread(target=run_daily_scan)
    daily_thread.daemon = True
    daily_thread.start()
    
    # הפעל עדכוני ליינים לפני משחק
    pregame_thread = threading.Thread(target=run_pregame_updates)
    pregame_thread.daemon = True
    pregame_thread.start()
    
    # הפעל ניטור משחקים חיים
    live_thread = threading.Thread(target=run_live_monitoring)
    live_thread.daemon = True
    live_thread.start()

def run_daily_scan():
    """סריקה יומית בלופ"""
    while True:
        daily_games_scan()
        time.sleep(24 * 60 * 60)  # חכה 24 שעות

def run_pregame_updates():
    """עדכון ליינים לפני משחק בלופ"""
    while True:
        update_pregame_lines()
        time.sleep(30 * 60)  # חכה 30 דקות

def run_live_monitoring():
    """ניטור משחקים חיים בלופ"""
    while True:
        monitor_live_games()
        time.sleep(30)  # חכה 30 שניות

# נתיבי API
@app.route('/')
def home():
    """דף הבית"""
    return send_from_directory('.', 'index.html')

@app.route('/api/games')
def get_games():
    """מחזיר את כל המשחקים"""
    # פילטרים אופציונליים
    sport_id = request.args.get('sport_id', 'all')
    status = request.args.get('status', 'all')
    
    result = []
    
    with data_lock:
        for game_id, game in games_data.items():
            # סינון לפי ספורט
            if sport_id != 'all' and game['sport_id'] != sport_id:
                continue
                
            # סינון לפי סטטוס
            if status != 'all' and game['status'] != status:
                continue
            
            # זיהוי הזדמנויות
            opportunity = detect_opportunities(game_id)
            
            # בניית אובייקט המשחק לתצוגה
            game_info = {
                'id': game_id,
                'sportType': 'כדורסל' if game['sport_id'] == '18' else 'כדורגל',
                'league': game['league'],
                'date': format_date(game.get('time')),
                'time': format_time(game.get('time')),
                'matchup': f"{game['home']} vs {game['away']}",
                'status': game['status'],
                
                # ליינים שונים - פורמט והתאמה לעיצוב
                'spread': format_spread(opening_lines.get(game_id, {}).get('spread')),
                'total': format_total(opening_lines.get(game_id, {}).get('total')),
                'currentSpread': format_spread(current_lines.get(game_id, {}).get('spread')),
                'currentTotal': format_total(current_lines.get(game_id, {}).get('total')),
                'startingSpread': format_spread(starting_lines.get(game_id, {}).get('spread')) if game['status'] == 'live' else '',
                'startingTotal': format_total(starting_lines.get(game_id, {}).get('total')) if game['status'] == 'live' else '',
                'liveSpread': format_spread(live_lines.get(game_id, {}).get('spread')) if game['status'] == 'live' else '',
                'liveTotal': format_total(live_lines.get(game_id, {}).get('total')) if game['status'] == 'live' else '',
                
                # מידע נוסף
                'score': game.get('score', ''),
                'timer': format_timer(game.get('timer', {})),
                'opportunity': opportunity['reason'],
                'opportunityType': opportunity['type']
            }
            
            result.append(game_info)
    
    return jsonify(result)

@app.route('/api/game/<game_id>')
def get_game(game_id):
    """מחזיר מידע מפורט על משחק ספציפי"""
    with data_lock:
        if game_id not in games_data:
            return jsonify({"error": "Game not found"}), 404
        
        game = games_data[game_id]
        opportunity = detect_opportunities(game_id)
        
        # בניית אובייקט תשובה מפורט יותר
        return jsonify({
            'id': game_id,
            'sportType': 'כדורסל' if game['sport_id'] == '18' else 'כדורגל',
            'league': game['league'],
            'date': format_date(game.get('time')),
            'time': format_time(game.get('time')),
            'home': game['home'],
            'away': game['away'],
            'status': game['status'],
            'score': game.get('score', ''),
            'timer': game.get('timer', {}),
            
            # ליינים
            'opening': opening_lines.get(game_id, {}),
            'current': current_lines.get(game_id, {}),
            'starting': starting_lines.get(game_id, {}),
            'live': live_lines.get(game_id, {}),
            
            # הזדמנויות
            'opportunity': opportunity
        })

# פונקציות עזר לפורמוט
def format_date(timestamp):
    """פורמט תאריך"""
    if not timestamp:
        return ""
    
    date = datetime.fromtimestamp(int(timestamp))
    return date.strftime("%b %d")  # Apr 30

def format_time(timestamp):
    """פורמט שעה"""
    if not timestamp:
        return ""
    
    time = datetime.fromtimestamp(int(timestamp))
    return time.strftime("%H:%M")  # 18:30

def format_spread(spread):
    """פורמט ליין ספרד"""
    if spread is None:
        return ""
    
    return f"{spread:+.1f}".replace('+', '')  # -4.5 או 3.5

def format_total(total):
    """פורמט ליין טוטאל"""
    if total is None:
        return ""
    
    return f"{total:.1f}"  # 206.5

def format_timer(timer):
    """פורמט זמן משחק"""
    if not timer:
        return ""
    
    quarter = timer.get('q', '')
    minutes = timer.get('tm', '')
    seconds = timer.get('ts', '')
    
    if minutes and seconds:
        return f"Q{quarter} {minutes}:{seconds.zfill(2)}"
    
    return ""

# תחילת התוכנית
@app.before_first_request
def startup():
    """פעולות שרצות בעת עליית השרת"""
    load_all_data()
    start_background_tasks()

if __name__ == '__main__':
    # הפעל רק כשמריצים ישירות
    load_all_data()
    daily_games_scan()  # הרץ סריקה ראשונית
    app.run(debug=True)
