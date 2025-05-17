# יבוא ספריות נדרשות
from flask import Flask, jsonify, request, send_from_directory
import requests
import os
import json
from datetime import datetime

# הגדרת האפליקציה כאשר הקבצים הסטטיים נמצאים בשורש הפרויקט
app = Flask(__name__, static_folder='.', static_url_path='')

# הגדרת הטוקן לשימוש ב-API
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # קוד ספורט עבור כדורסל

# מיקום קובץ היסטוריית ליינים
LINES_HISTORY_FILE = 'lines_history.json'

# מיקום קובץ הזדמנויות
OPPORTUNITIES_FILE = 'opportunities.json'

# פונקציה לשמירת היסטוריית ליינים
def save_game_lines(game_id, lines_data):
    history = {}
    if os.path.exists(LINES_HISTORY_FILE):
        try:
            with open(LINES_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = {}
    
    # שמירת נתוני ליין חדשים
    if game_id not in history:
        history[game_id] = []
    
    # בדיקה אם הנתונים השתנו מאז העדכון האחרון
    if history[game_id] and all(history[game_id][-1].get(key) == value 
                              for key, value in lines_data.items() 
                              if key != 'timestamp'):
        return False  # אין שינוי בנתונים
    
    # הוספת נתוני ליין עם חותמת זמן
    lines_data['timestamp'] = datetime.now().isoformat()
    history[game_id].append(lines_data)
    
    # שמירה לקובץ
    with open(LINES_HISTORY_FILE, 'w') as f:
        json.dump(history, f)
    
    return True  # נשמרו נתונים חדשים

# פונקציה לקבלת היסטוריית ליינים
def get_game_lines_history(game_id):
    if not os.path.exists(LINES_HISTORY_FILE):
        return []
    
    try:
        with open(LINES_HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        return history.get(game_id, [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# פונקציה לשמירת הזדמנויות
def save_opportunity(game_id, opportunity_data):
    opportunities = {}
    if os.path.exists(OPPORTUNITIES_FILE):
        try:
            with open(OPPORTUNITIES_FILE, 'r') as f:
                opportunities = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            opportunities = {}
    
    # שמירת נתוני הזדמנות חדשים
    opportunities[game_id] = opportunity_data
    
    # שמירה לקובץ
    with open(OPPORTUNITIES_FILE, 'w') as f:
        json.dump(opportunities, f)

# פונקציה לקבלת הזדמנויות
def get_opportunity(game_id):
    if not os.path.exists(OPPORTUNITIES_FILE):
        return None
    
    try:
        with open(OPPORTUNITIES_FILE, 'r') as f:
            opportunities = json.load(f)
        
        return opportunities.get(game_id, None)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

@app.route('/')
def index():
    # החזרת קובץ index.html מהשורש
    return app.send_static_file('index.html')

@app.route('/api/games')
def get_games():
    # קריאה ל-API של B365 והחזרת נתונים
    params = {
        "sport_id": SPORT_ID,
        "token": B365_TOKEN
    }
    
    # אם יש פרמטרים נוספים מהבקשה, הוסף אותם
    for key, value in request.args.items():
        if key not in params:  # וודא שלא דורסים פרמטרים קיימים
            params[key] = value
    
    try:
        response = requests.get(B365_API_URL, params=params)
        response.raise_for_status()  # יזרוק שגיאה אם הסטטוס לא 200
        games_data = response.json()
        
        # עיבוד נתוני משחקים ושמירת ליינים
        if 'results' in games_data:
            for game in games_data['results']:
                game_id = game.get('id')
                if game_id:
                    # חילוץ נתוני ליין
                    lines_data = extract_lines_from_game(game)
                    
                    # שמירת ליינים להיסטוריה
                    data_changed = save_game_lines(game_id, lines_data)
                    
                    # חישוב הזדמנויות רק אם הנתונים השתנו
                    if data_changed:
                        opportunity = calculate_opportunities(game_id, lines_data)
                        if opportunity and opportunity['type'] != 'neutral':
                            save_opportunity(game_id, opportunity)
                    
                    # קבלת הזדמנות קיימת אם יש
                    opportunity = get_opportunity(game_id)
                    
                    # הוספת מידע על הזדמנויות ונתוני ליין למשחק
                    add_opportunity_and_lines_to_game(game, opportunity)
        
        return jsonify(games_data)
    except Exception as e:
        app.logger.error(f"Error fetching games: {str(e)}")
        return jsonify({"error": f"שגיאה בקריאה ל-API: {str(e)}"}), 500

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    # קריאה ל-API של B365 עבור משחק ספציפי
    params = {
        "event_id": game_id,
        "token": B365_TOKEN
    }
    
    try:
        response = requests.get(B365_API_URL, params=params)
        response.raise_for_status()
        game_data = response.json()
        
        # הוספת מידע נוסף על ליינים והזדמנויות
        if 'results' in game_data and game_data['results']:
            game = game_data['results'][0]
            
            # קבלת הזדמנות קיימת אם יש
            opportunity = get_opportunity(game_id)
            
            # הוספת מידע על הזדמנויות ונתוני ליין למשחק
            add_opportunity_and_lines_to_game(game, opportunity)
        
        return jsonify(game_data)
    except Exception as e:
        app.logger.error(f"Error fetching game details: {str(e)}")
        return jsonify({"error": f"שגיאה בקריאה ל-API: {str(e)}"}), 500

@app.route('/api/stats')
def get_stats():
    # חישוב סטטיסטיקות מתוך הזדמנויות
    try:
        opportunities = {}
        if os.path.exists(OPPORTUNITIES_FILE):
            with open(OPPORTUNITIES_FILE, 'r') as f:
                opportunities = json.load(f)
        
        # ספירת הזדמנויות לפי סוג
        green_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'green')
        red_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'red')
        blue_opportunities = sum(1 for opp in opportunities.values() if opp and opp.get('type') == 'blue')
        
        # חישוב אחוז הזדמנויות
        total_opportunities = green_opportunities + red_opportunities + blue_opportunities
        total_games = len(opportunities)
        opportunity_percentage = round((total_opportunities / total_games * 100) if total_games > 0 else 0)
        
        # ספירת משחקים חיים ועתידיים מנתוני API ריאלטיים
        total_live = 0
        total_upcoming = 0
        
        try:
            # קריאה ל-API לקבלת נתוני משחקים עדכניים
            params = {
                "sport_id": SPORT_ID,
                "token": B365_TOKEN
            }
            response = requests.get(B365_API_URL, params=params)
            if response.status_code == 200:
                games_data = response.json()
                if 'results' in games_data:
                    # ספירת משחקים לפי סטטוס
                    for game in games_data['results']:
                        status = game.get('time_status')
                        if status == '1':  # משחק חי
                            total_live += 1
                        elif status == '0':  # משחק עתידי
                            total_upcoming += 1
        except Exception as e:
            app.logger.error(f"Error counting games: {str(e)}")
            # במקרה של שגיאה, נציג לפחות את מספר המשחקים בהיסטוריה שלנו
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
        app.logger.error(f"Error calculating stats: {str(e)}")
        return jsonify({
            "opportunity_percentage": 0,
            "green_opportunities": 0,
            "red_opportunities": 0,
            "blue_opportunities": 0,
            "total_live": 0,
            "total_upcoming": 0
        })

@app.route('/api/game/<game_id>/lines_history')
def get_lines_history(game_id):
    history = get_game_lines_history(game_id)
    return jsonify(history)

# פונקציה לחילוץ נתוני ליין ממשחק
def extract_lines_from_game(game):
    """
    חילוץ נתוני ליין ממשחק - התאמה למבנה נתונים של B365
    מחזיר אובייקט עם נתוני הספרד והטוטאל
    """
    lines_data = {
        'spread': None,
        'total': None,
        'time_status': game.get('time_status'),
        'timestamp': datetime.now().isoformat(),
        'quarter': None,
        'time_remaining': None
    }
    
    # חילוץ מידע על רבע ושעון משחק
    if 'timer' in game:
        timer = game.get('timer', {})
        lines_data['quarter'] = timer.get('q')
        lines_data['time_remaining'] = timer.get('tm')
    
    # מחלץ נתוני קו ישירות מה-odds אם יש
    if 'odds' in game:
        for market_type, market_data in game['odds'].items():
            # חיפוש שוק ספרד בפורמט B365
            if market_type in ['handicap', 'handicap_line', 'ah', 'point_spread']:
                try:
                    handicap_val = float(market_data)
                    lines_data['spread'] = handicap_val
                except (ValueError, TypeError):
                    pass
            
            # חיפוש שוק טוטאל בפורמט B365
            elif market_type in ['total', 'total_line', 'ou']:
                try:
                    total_val = float(market_data)
                    lines_data['total'] = total_val
                except (ValueError, TypeError):
                    pass
    
    # טיפול ישיר בבחירות (selections) - בהתבסס על התמונה הראשונה
    # שם רואים שיש קו +18.5 בקו 1.80
    if not lines_data['spread'] and 'extra' in game:
        extra = game.get('extra', {})
        if 'handicap' in extra:
            try:
                lines_data['spread'] = float(extra['handicap'])
            except (ValueError, TypeError):
                pass
    
    # טיפול ישיר במידע מהתמונה השנייה
    # כאן אנחנו רואים ליינים כמו 3.5-, 15.5-, וכו'
    if not lines_data['spread'] and 'odds' in game:
        # ניסיון לחלץ מידע במבנה שונה
        for key, value in game['odds'].items():
            if 'ah_home' in key or 'handicap_home' in key:
                try:
                    lines_data['spread'] = float(value)
                    break
                except (ValueError, TypeError):
                    pass
    
    # לפי התמונה השנייה, מחלצים גם את הטוטאל
    if not lines_data['total'] and 'odds' in game:
        for key, value in game['odds'].items():
            if 'total' in key.lower() and 'over' in key.lower():
                try:
                    lines_data['total'] = float(value)
                    break
                except (ValueError, TypeError):
                    pass
    
    # אם עדיין אין לנו נתונים, ננסה לחלץ מהשדות המוצגים בתמונה
    if (not lines_data['spread'] or not lines_data['total']) and 'ss' in game:
        try:
            # בתמונה 1 רואים שיש תוצאה כרגע 52-38
            scores = game['ss'].split('-')
            home_score = int(scores[0].strip())
            away_score = int(scores[1].strip())
            
            # אם אין לנו ספרד, ננסה לחשב לפי התוצאה הנוכחית
            if not lines_data['spread']:
                score_diff = home_score - away_score
                if score_diff > 0:
                    # הקבוצה הביתית מובילה, אז נותנים יתרון לאורחת
                    lines_data['spread'] = round(score_diff + 3.5, 1)  # הוספת שולי ביטחון
                else:
                    # הקבוצה האורחת מובילה, נותנים יתרון לביתית
                    lines_data['spread'] = round(score_diff - 3.5, 1)  # הוספת שולי ביטחון
            
            # אם אין לנו טוטאל, ננסה להעריך לפי התוצאה והרבע
            if not lines_data['total']:
                current_total = home_score + away_score
                quarter = int(lines_data['quarter'] or 0)
                
                if quarter > 0:
                    # הערכת הטוטאל הסופי לפי הרבע הנוכחי
                    quarters_left = 4 - quarter
                    estimated_final = current_total * (4 / quarter)
                    
                    # הוספת 5% להערכה
                    lines_data['total'] = round(estimated_final * 1.05, 1)
        except (ValueError, IndexError, TypeError, ZeroDivisionError):
            pass
    
    # חישוב טוטאל לפי ממוצע נקודות ליגה אם עדיין אין לנו
    if not lines_data['total'] and 'league' in game:
        league_name = game.get('league', {}).get('name', '').lower()
        
        # נתונים מבוססים על ממוצעי ליגות
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
        
        # הגדרת ברירת מחדל אם אין ממוצע ספציפי לליגה
        default_total = 155.0
        
        # חיפוש התאמה חלקית לשם הליגה
        for league_key, avg_points in league_average_points.items():
            if league_key in league_name:
                lines_data['total'] = avg_points
                break
        
        # אם לא נמצאה התאמה, השתמש בברירת המחדל
        if not lines_data['total']:
            lines_data['total'] = default_total
    
    # עיגול הערכים לחצי הקרוב (מקובל בהימורים)
    if lines_data['spread']:
        lines_data['spread'] = round(lines_data['spread'] * 2) / 2
    
    if lines_data['total']:
        lines_data['total'] = round(lines_data['total'] * 2) / 2
    
    return lines_data

# פונקציה לחישוב הזדמנויות
def calculate_opportunities(game_id, current_lines):
    history = get_game_lines_history(game_id)
    
    if not history or len(history) < 2:
        return None
    
    # קבלת ליין פתיחה (הראשון בהיסטוריה)
    opening_lines = history[0]
    
    # נוכחי
    current_spread = current_lines.get('spread')
    current_total = current_lines.get('total')
    
    # פתיחה
    opening_spread = opening_lines.get('spread')
    opening_total = opening_lines.get('total')
    
    # חישוב הפרשים
    spread_diff = 0
    total_diff = 0
    
    if current_spread is not None and opening_spread is not None:
        spread_diff = current_spread - opening_spread
    
    if current_total is not None and opening_total is not None:
        total_diff = current_total - opening_total
    
    # זיהוי הזדמנויות לפי כללים
    opportunity_type = 'neutral'
    opportunity_reason = ''
    
    if abs(spread_diff) >= 7:
        opportunity_type = 'green'
        opportunity_reason = f'שינוי משמעותי בספרד: {spread_diff:.1f} נקודות'
    elif abs(total_diff) >= 10:
        opportunity_type = 'green'
        opportunity_reason = f'שינוי משמעותי בטוטאל: {total_diff:.1f} נקודות'
    
    return {
        'type': opportunity_type,
        'reason': opportunity_reason,
        'spread_diff': spread_diff,
        'total_diff': total_diff,
        'time_status': current_lines.get('time_status'),
        'timestamp': datetime.now().isoformat()
    }

# פונקציה להוספת מידע על הזדמנויות ונתוני ליין למשחק
def add_opportunity_and_lines_to_game(game, opportunity):
    history = get_game_lines_history(game.get('id', ''))
    
    # הוספת מידע על ליינים
    if history:
        # ליין פתיחה (ראשון בהיסטוריה)
        opening_lines = history[0]
        
        # ליין התחלה (אם יש)
        start_lines = history[1] if len(history) > 1 else opening_lines
        
        # ליין נוכחי (אחרון בהיסטוריה)
        current_lines = history[-1]
        
        # הוספת נתוני ליין למשחק
        game['opening_spread'] = opening_lines.get('spread')
        game['opening_total'] = opening_lines.get('total')
        
        game['start_spread'] = start_lines.get('spread')
        game['start_total'] = start_lines.get('total')
        
        game['live_spread'] = current_lines.get('spread')
        game['live_total'] = current_lines.get('total')
        
        # חישוב הפרשים
        if game['opening_spread'] is not None and game['live_spread'] is not None:
            game['live_spread_diff'] = game['live_spread'] - game['opening_spread']
        else:
            game['live_spread_diff'] = 0
            
        if game['opening_total'] is not None and game['live_total'] is not None:
            game['live_total_diff'] = game['live_total'] - game['opening_total']
        else:
            game['live_total_diff'] = 0
            
        # קביעת כיוון השינוי
        game['spread_direction'] = 'up' if game.get('live_spread_diff', 0) > 0 else 'down' if game.get('live_spread_diff', 0) < 0 else 'neutral'
        game['total_direction'] = 'up' if game.get('live_total_diff', 0) > 0 else 'down' if game.get('live_total_diff', 0) < 0 else 'neutral'
        
        # סימון שינויים משמעותיים
        game['spread_flag'] = 'green' if abs(game.get('live_spread_diff', 0)) >= 7 else 'neutral'
        game['ou_flag'] = 'green' if abs(game.get('live_total_diff', 0)) >= 10 else 'neutral'
        
        # סימון פתיחה מול התחלה
        if game['opening_spread'] is not None and game['start_spread'] is not None:
            opening_vs_start_spread = game['start_spread'] - game['opening_spread']
            game['opening_vs_start'] = 'green' if abs(opening_vs_start_spread) >= 1 else 'neutral'
        else:
            game['opening_vs_start'] = 'neutral'
    
    # הוספת מידע על הזדמנויות
    if opportunity:
        game['opportunity_type'] = opportunity.get('type', 'neutral')
        game['opportunity_reason'] = opportunity.get('reason', '')
    else:
        game['opportunity_type'] = 'neutral'
        game['opportunity_reason'] = ''

# טיפול במשאבים סטטיים (JavaScript, CSS, תמונות)
@app.route('/<path:path>')
def serve_static(path):
    # אם הקובץ קיים בשורש, החזר אותו
    if os.path.exists(path):
        return send_from_directory('.', path)
    # אם הקובץ לא קיים, החזר 404
    return app.send_static_file('index.html')

# מתודה לטיפול בשגיאות 404
@app.errorhandler(404)
def not_found(e):
    # החזרת הדף הראשי במקרה של 404 (שימושי לSPA)
    return app.send_static_file('index.html')

# הפעלת השרת בסביבת פיתוח
if __name__ == '__main__':
    # בסביבת הפצה, ה-WSGI server ידאג להפעיל את האפליקציה
    app.run(debug=True, host='0.0.0.0')
