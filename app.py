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
        
        # ספירת משחקים חיים ועתידיים
        # זה יהיה יותר מדויק אם נשמור גם היסטוריה של סטטוס משחקים
        total_live = 15  # דוגמה - יש להחליף עם מידע אמיתי
        total_upcoming = 23  # דוגמה - יש להחליף עם מידע אמיתי
        
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
        'timestamp': datetime.now().isoformat()
    }
    
    # בדיקה האם יש מידע על שווקים במשחק
    if 'markets' in game and isinstance(game['markets'], list):
        for market in game['markets']:
            # חיפוש שוק ספרד (Handicap)
            if market.get('name') in ['Handicap', 'Point Spread']:
                try:
                    # חיפוש הליין עצמו בתוך הבחירות
                    for selection in market.get('selections', []):
                        if 'handicap' in selection:
                            # שמירת ערך הספרד
                            lines_data['spread'] = float(selection['handicap'])
                            break
                except (ValueError, TypeError):
                    pass
            
            # חיפוש שוק טוטאל (Total Points)
            elif market.get('name') in ['Total Points', 'Over/Under']:
                try:
                    # חיפוש הליין עצמו בתוך הבחירות
                    for selection in market.get('selections', []):
                        if 'handicap' in selection and selection.get('name', '').lower().startswith('over'):
                            # שמירת ערך הטוטאל
                            lines_data['total'] = float(selection['handicap'])
                            break
                except (ValueError, TypeError):
                    pass
    
    # גיבוי: אם אין מידע ישיר על שווקים, ננסה למצוא באובייקט odds
    if (lines_data['spread'] is None or lines_data['total'] is None) and 'odds' in game:
        odds = game['odds']
        
        # חיפוש ספרד
        if lines_data['spread'] is None:
            spread_keys = ['handicap', 'point_spread', 'spread', 'ps']
            for key in spread_keys:
                if key in odds:
                    try:
                        lines_data['spread'] = float(odds[key])
                        break
                    except (ValueError, TypeError):
                        pass
        
        # חיפוש טוטאל
        if lines_data['total'] is None:
            total_keys = ['total', 'over_under', 'ou', 'tot']
            for key in total_keys:
                if key in odds:
                    try:
                        lines_data['total'] = float(odds[key])
                        break
                    except (ValueError, TypeError):
                        pass
    
    # חישוב ערכים משוערים אם עדיין אין לנו נתונים
    
    # אפשרות 1: ליין ספרד מחושב מהתוצאה הנוכחית (עבור משחקים חיים)
    if lines_data['spread'] is None and game.get('time_status') == '1' and game.get('ss'):
        try:
            scores = game['ss'].split('-')
            home_score = int(scores[0])
            away_score = int(scores[1])
            score_diff = home_score - away_score
            
            # מבנה התצוגה של ליין הספרד: מספר חיובי אומר שהקבוצה האורחת מקבלת נקודות
            # לכן, אם ההפרש חיובי (הביתית מובילה) אז הליין יהיה שלילי וההפך
            spread_estimate = -score_diff - 1.5  # הוספת 1.5 למרווח בטחון
            lines_data['spread'] = round(spread_estimate, 1)
        except (ValueError, IndexError):
            pass
    
    # אפשרות 2: טוטאל מחושב מהתוצאה הנוכחית והזמן שנותר במשחק
    if lines_data['total'] is None and game.get('time_status') == '1' and game.get('ss'):
        try:
            scores = game['ss'].split('-')
            home_score = int(scores[0])
            away_score = int(scores[1])
            current_total = home_score + away_score
            
            # חישוב טוטאל משוער לפי רבע והתוצאה הנוכחית
            quarter = int(game.get('timer', {}).get('q', 0))
            minutes_left = 0
            
            # חישוב זמן נותר במשחק
            if quarter > 0:
                minutes_played = (quarter - 1) * 10  # נניח שכל רבע הוא 10 דקות
                
                if 'tm' in game.get('timer', {}):
                    timer_parts = game['timer']['tm'].split(':')
                    if len(timer_parts) == 2:
                        minutes_played += 10 - (int(timer_parts[0]) + int(timer_parts[1]) / 60)
                
                minutes_left = 40 - minutes_played  # 4 רבעים * 10 דקות
                
                if minutes_left > 0:
                    # יחס הנקודות לדקה עד כה
                    points_per_minute = current_total / minutes_played if minutes_played > 0 else 0
                    
                    # חישוב צפי לסיום המשחק
                    estimated_final_total = current_total + (points_per_minute * minutes_left)
                    
                    # עיגול לחצי נקודה הקרובה בהתאם לכללי הימורים
                    lines_data['total'] = round(estimated_final_total * 2) / 2
        except (ValueError, IndexError, TypeError, ZeroDivisionError):
            pass
    
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
