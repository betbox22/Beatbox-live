from flask import Flask, jsonify, request, send_from_directory
import requests
import os
import json
import time
from datetime import datetime, timedelta
import threading
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("betbox.log"), logging.StreamHandler()]
)
logger = logging.getLogger("betbox")

app = Flask(__name__, static_folder='static')

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
score_history = {}       # היסטוריית תוצאות לחישוב קצב משחק

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
    global games_data, opening_lines, current_lines, starting_lines, live_lines, score_history
    games_data = load_data('games_data.json')
    opening_lines = load_data('opening_lines.json')
    current_lines = load_data('current_lines.json')
    starting_lines = load_data('starting_lines.json')
    live_lines = load_data('live_lines.json')
    score_history = load_data('score_history.json')

# שמירת כל הנתונים
def save_all_data():
    save_data(games_data, 'games_data.json')
    save_data(opening_lines, 'opening_lines.json')
    save_data(current_lines, 'current_lines.json')
    save_data(starting_lines, 'starting_lines.json')
    save_data(live_lines, 'live_lines.json')
    save_data(score_history, 'score_history.json')

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
        params = {"token": API_TOKEN, "sport_id": "3"}  # 3 = כדורסל
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
    current_time = datetime.now()
    
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
                current_score = game.get('ss', '0-0')
                games_data[game_id]['score'] = current_score
                games_data[game_id]['timer'] = game.get('timer', {})
                
                # עדכון ליין לייב
                live_odds = fetch_odds(game_id)
                live_lines[game_id] = live_odds
                
                # שמירת היסטוריית תוצאות לחישוב קצב
                if game_id not in score_history:
                    score_history[game_id] = []
                
                score_history[game_id].append({
                    'score': current_score,
                    'timestamp': current_time.isoformat()
                })
                
                # שמירה רק של 10 דקות אחרונות
                cutoff_time = (current_time - timedelta(minutes=10)).isoformat()
                score_history[game_id] = [
                    record for record in score_history[game_id]
                    if record['timestamp'] >= cutoff_time
                ]
        
        save_data(games_data, 'games_data.json')
        save_data(starting_lines, 'starting_lines.json')
        save_data(live_lines, 'live_lines.json')
        save_data(score_history, 'score_history.json')

def calculate_shot_rate(game_id):
    """מחשב את קצב הזריקות לסל (זריקות לדקה)"""
    if game_id not in score_history or len(score_history[game_id]) < 2:
        return None
    
    # מיון לפי זמן
    history = sorted(score_history[game_id], key=lambda x: x['timestamp'])
    
    # חישוב זמן בדקות
    start_time = datetime.fromisoformat(history[0]['timestamp'])
    end_time = datetime.fromisoformat(history[-1]['timestamp'])
    minutes_elapsed = (end_time - start_time).total_seconds() / 60
    
    if minutes_elapsed < 1:  # נדרש לפחות דקה של נתונים
        return None
    
    # חישוב סך נקודות שנוספו
    try:
        start_score = history[0]['score']
        end_score = history[-1]['score']
        
        start_home, start_away = map(int, start_score.split('-'))
        end_home, end_away = map(int, end_score.split('-'))
        
        total_points_added = (end_home + end_away) - (start_home + start_away)
        
        # חישוב נקודות לדקה
        points_per_minute = total_points_added / minutes_elapsed
        
        # המרה לזריקות משוערות (בהנחה של 2 נקודות לזריקה בממוצע)
        shots_per_minute = points_per_minute / 2
        
        return shots_per_minute
    except (ValueError, ZeroDivisionError):
        return None

def determine_shot_rate_color(shot_rate):
    """קובע צבע לפי קצב זריקות"""
    if shot_rate is None:
        return None
    
    if shot_rate <= 3.0:
        return "red"  # קצב איטי
    elif shot_rate <= 4.0:
        return None  # קצב רגיל, ללא סימון
    else:
        return "blue"  # קצב מהיר

def detect_opportunities(game_id):
    """מזהה הזדמנויות בהימורים לפי הלוגיקה החדשה"""
    result = {
        "opening_vs_start": None,
        "spread_flag": None,
        "ou_flag": None,
        "shot_rate": None,
        "shot_rate_color": None,
        "type": "neutral",
        "reason": ""
    }
    
    if game_id not in games_data:
        return result
    
    game = games_data[game_id]
    opening = opening_lines.get(game_id, {})
    current = current_lines.get(game_id, {})
    start = starting_lines.get(game_id, {})
    live = live_lines.get(game_id, {})
    
    # 1. השוואת נתוני פתיחה מול נתוני תחילת משחק
    if opening and start:
        opening_spread = opening.get('spread', 0)
        opening_total = opening.get('total', 0)
        start_spread = start.get('spread', 0)
        start_total = start.get('total', 0)
        
        # הבדל של לפחות 2 נקודות בשניהם
        if abs(start_spread - opening_spread) >= 2 and abs(start_total - opening_total) >= 2:
            # קביעה אם חיובי או שלילי
            is_positive = ((start_spread > opening_spread) and (start_total > opening_total)) or \
                         ((start_spread < opening_spread) and (start_total < opening_total))
            
            result["opening_vs_start"] = "green" if is_positive else "red"
            if is_positive:
                result["type"] = "green"
                result["reason"] = "הבדל חיובי בין פתיחה להתחלה"
            else:
                result["type"] = "red"
                result["reason"] = "הבדל שלילי בין פתיחה להתחלה"
    
    # 2. זיהוי שינויים במשחק חי
    if game['status'] == 'live' and start and live:
        start_spread = start.get('spread', 0)
        start_total = start.get('total', 0)
        live_spread = live.get('spread', 0)
        live_total = live.get('total', 0)
        
        # שינוי של 7+ נקודות בליין
        if abs(live_spread - start_spread) >= 7:
            result["spread_flag"] = "green"
            result["type"] = "green"
            result["reason"] = "שינוי משמעותי בליין במהלך המשחק"
        
        # שינוי של 10+ נקודות באובר אנדר
        if abs(live_total - start_total) >= 10:
            result["ou_flag"] = "green"
            result["type"] = "green"
            result["reason"] = "שינוי משמעותי באובר/אנדר במהלך המשחק"
    
    # 3. ניתוח קצב משחק
    shot_rate = calculate_shot_rate(game_id)
    shot_rate_color = determine_shot_rate_color(shot_rate)
    
    result["shot_rate"] = shot_rate
    result["shot_rate_color"] = shot_rate_color
    
    # אם לא נקבע סוג לפי הסעיפים הקודמים, קבע לפי קצב זריקות
    if result["type"] == "neutral" and shot_rate_color:
        result["type"] = shot_rate_color
        if shot_rate_color == "red":
            result["reason"] = "קצב משחק איטי"
        elif shot_rate_color == "blue":
            result["reason"] = "קצב משחק מהיר"
    
    return result

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
            
            # חישוב שינויים
            opening_spread = opening_lines.get(game_id, {}).get('spread')
            current_spread = current_lines.get(game_id, {}).get('spread')
            start_spread = starting_lines.get(game_id, {}).get('spread')
            live_spread = live_lines.get(game_id, {}).get('spread')
            
            opening_total = opening_lines.get(game_id, {}).get('total')
            current_total = current_lines.get(game_id, {}).get('total')
            start_total = starting_lines.get(game_id, {}).get('total')
            live_total = live_lines.get(game_id, {}).get('total')
            
            # בניית אובייקט המשחק לתצוגה
            game_info = {
                'id': game_id,
                'sportType': 'כדורסל' if game['sport_id'] == '3' else 'כדורגל',
                'league': game['league'],
                'date': format_date(game.get('time')),
                'time': format_time(game.get('time')),
                'matchup': f"{game['home']} vs {game['away']}",
                'status': game['status'],
                
                # ליינים שונים - פורמט והתאמה לעיצוב
                'opening_spread': format_spread(opening_spread),
                'opening_total': format_total(opening_total),
                'current_spread': format_spread(current_spread),
                'current_total': format_total(current_total),
                'start_spread': format_spread(start_spread) if game['status'] == 'live' else '',
                'start_total': format_total(start_total) if game['status'] == 'live' else '',
                'live_spread': format_spread(live_spread) if game['status'] == 'live' else '',
                'live_total': format_total(live_total) if game['status'] == 'live' else '',
                
                # שינויים בליין
                'spread_diff': format_diff(current_spread, opening_spread) if opening_spread and current_spread else '',
                'total_diff': format_diff(current_total, opening_total) if opening_total and current_total else '',
                'live_spread_diff': format_diff(live_spread, start_spread) if start_spread and live_spread else '',
                'live_total_diff': format_diff(live_total, start_total) if start_total and live_total else '',
                
                # מידע נוסף
                'score': game.get('score', ''),
                'timer': format_timer(game.get('timer', {})),
                
                # פרטי הזדמנות
                'opportunity_type': opportunity['type'],
                'opportunity_reason': opportunity['reason'],
                'opening_vs_start': opportunity['opening_vs_start'],
                'spread_flag': opportunity['spread_flag'],
                'ou_flag': opportunity['ou_flag'],
                'shot_rate': format_shot_rate(opportunity['shot_rate']),
                'shot_rate_color': opportunity['shot_rate_color']
            }
            
            result.append(game_info)
    
    return jsonify(result)

@app.route('/api/live-games')
def get_live_games():
    """מחזיר רק משחקים חיים"""
    with data_lock:
        live_result = []
        
        for game_id, game in games_data.items():
            if game['status'] == 'live':
                # זיהוי הזדמנויות
                opportunity = detect_opportunities(game_id)
                
                # חישוב שינויים
                opening_spread = opening_lines.get(game_id, {}).get('spread')
                start_spread = starting_lines.get(game_id, {}).get('spread')
                live_spread = live_lines.get(game_id, {}).get('spread')
                
                opening_total = opening_lines.get(game_id, {}).get('total')
                start_total = starting_lines.get(game_id, {}).get('total')
                live_total = live_lines.get(game_id, {}).get('total')
                
                # בניית אובייקט המשחק לתצוגה
                game_info = {
                    'id': game_id,
                    'sportType': 'כדורסל' if game['sport_id'] == '3' else 'כדורגל',
                    'league': game['league'],
                    'home': game['home'],
                    'away': game['away'],
                    'matchup': f"{game['home']} vs {game['away']}",
                    
                    # ליינים שונים - פורמט והתאמה לעיצוב
                    'opening_spread': format_spread(opening_spread),
                    'opening_total': format_total(opening_total),
                    'start_spread': format_spread(start_spread),
                    'start_total': format_total(start_total),
                    'live_spread': format_spread(live_spread),
                    'live_total': format_total(live_total),
                    
                    # שינויים בליין
                    'start_spread_diff': format_diff(start_spread, opening_spread) if opening_spread and start_spread else '',
                    'start_total_diff': format_diff(start_total, opening_total) if opening_total and start_total else '',
                    'live_spread_diff': format_diff(live_spread, start_spread) if start_spread and live_spread else '',
                    'live_total_diff': format_diff(live_total, start_total) if start_total and live_total else '',
                    
                    # מידע נוסף
                    'score': game.get('score', ''),
                    'timer': format_timer(game.get('timer', {})),
                    
                    # פרטי הזדמנות
                    'opportunity_type': opportunity['type'],
                    'opportunity_reason': opportunity['reason'],
                    'opening_vs_start': opportunity['opening_vs_start'],
                    'spread_flag': opportunity['spread_flag'],
                    'ou_flag': opportunity['ou_flag'],
                    'shot_rate': format_shot_rate(opportunity['shot_rate']),
                    'shot_rate_color': opportunity['shot_rate_color']
                }
                
                live_result.append(game_info)
    
    return jsonify(live_result)

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
            'sportType': 'כדורסל' if game['sport_id'] == '3' else 'כדורגל',
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
            
            # היסטוריית תוצאות
            'score_history': score_history.get(game_id, []),
            
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

def format_diff(current, original):
    """פורמט הפרש בין ליינים"""
    if current is None or original is None:
        return ""
    
    diff = float(current) - float(original)
    return f"{diff:+.1f}"  # +3.5 או -2.0

def format_timer(timer):
    """פורמט זמן משחק"""
    if not timer:
        return ""
    
    quarter = timer.get('q', '')
    minutes = timer.get('tm', '')
    seconds = timer.get('ts', '')
    
    if minutes and seconds:
        return f"רבע {quarter} ({minutes}:{seconds.zfill(2)})"
    
    return ""

def format_shot_rate(rate):
    """פורמט קצב זריקות"""
    if rate is None:
        return ""
    
    return f"{rate:.1f}"  # 3.5

# פונקציות סטטיסטיקה
def calculate_stats():
    """חישוב סטטיסטיקות כלליות"""
    stats = {
        "total_live": 0,
        "green_opportunities": 0,
        "red_opportunities": 0,
        "opportunity_percentage": 0
    }
    
    live_count = 0
    opportunity_count = 0
    
    for game_id, game in games_data.items():
        if game['status'] == 'live':
            live_count += 1
            opportunity = detect_opportunities(game_id)
            
            if opportunity['type'] == 'green':
                opportunity_count += 1
                stats["green_opportunities"] += 1
            elif opportunity['type'] == 'red':
                stats["red_opportunities"] += 1
    
    stats["total_live"] = live_count
    
    if live_count > 0:
        stats["opportunity_percentage"] = int((opportunity_count / live_count) * 100)
    
    return stats

@app.route('/api/stats')
def get_stats():
    """מחזיר סטטיסטיקות"""
    with data_lock:
        return jsonify(calculate_stats())

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
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
