# יבוא ספריות נדרשות
from flask import Flask, jsonify, request, send_from_directory
import requests
import os
import json
import time
import tempfile
from datetime import datetime
import logging

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרת האפליקציה כאשר הקבצים הסטטיים נמצאים בשורש הפרויקט
app = Flask(__name__, static_folder='.', static_url_path='')

# הגדרת הטוקן והכתובת לשימוש ב-API
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # קוד ספורט עבור כדורסל

# פונקציה לקבלת תיקייה לאחסון
def get_storage_dir():
    # בדוק אם אנחנו על שרת Render
    if 'RENDER' in os.environ:
        # השתמש בתיקייה זמנית
        return tempfile.gettempdir()
    else:
        # השתמש בתיקייה נוכחית
        return '.'

# מיקום קובץ היסטוריית ליינים
LINES_HISTORY_FILE = os.path.join(get_storage_dir(), 'lines_history.json')

# מיקום קובץ הזדמנויות
OPPORTUNITIES_FILE = os.path.join(get_storage_dir(), 'opportunities.json')

# בדיקות תקינות תצורה
def validate_configuration():
    issues = []
    
    # בדיקת API URL
    if not B365_API_URL or not B365_API_URL.startswith("http"):
        issues.append(f"כתובת API לא תקינה: {B365_API_URL}")
    
    # בדיקת טוקן
    if not B365_TOKEN or len(B365_TOKEN) < 10:
        issues.append(f"טוקן API לא תקין: {B365_TOKEN}")
    
    # בדיקת יכולת כתיבה לקבצי היסטוריה
    storage_dir = get_storage_dir()
    test_file = os.path.join(storage_dir, "test_write.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        issues.append(f"בעיה בהרשאות כתיבה לתיקייה {storage_dir}: {str(e)}")
    
    if issues:
        for issue in issues:
            logger.error(f"בעיית תצורה: {issue}")
        return False
    
    logger.info("בדיקת תצורה עברה בהצלחה")
    return True

# הפעלת בדיקת תצורה
is_config_valid = validate_configuration()

# פונקציה לשמירת היסטוריית ליינים
def save_game_lines(game_id, lines_data):
    try:
        # בדוק אם תיקיית האב קיימת
        parent_dir = os.path.dirname(LINES_HISTORY_FILE)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # טעינת היסטוריה קיימת
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
    except Exception as e:
        logger.error(f"שגיאה בשמירת נתוני ליין: {str(e)}")
        # במקרה של שגיאה, נחזיר True כדי שהמערכת תמשיך לפעול
        return True

# פונקציה לקבלת היסטוריית ליינים
def get_game_lines_history(game_id):
    try:
        if not os.path.exists(LINES_HISTORY_FILE):
            return []
        
        with open(LINES_HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        return history.get(game_id, [])
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logger.error(f"שגיאה בקריאת היסטוריית ליינים: {str(e)}")
        return []

# פונקציה לשמירת הזדמנויות
def save_opportunity(game_id, opportunity_data):
    try:
        # בדוק אם תיקיית האב קיימת
        parent_dir = os.path.dirname(OPPORTUNITIES_FILE)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # טעינת הזדמנויות קיימות
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
            
        return True
    except Exception as e:
        logger.error(f"שגיאה בשמירת הזדמנויות: {str(e)}")
        return False

# פונקציה לקבלת הזדמנויות
def get_opportunity(game_id):
    try:
        if not os.path.exists(OPPORTUNITIES_FILE):
            return None
        
        with open(OPPORTUNITIES_FILE, 'r') as f:
            opportunities = json.load(f)
        
        return opportunities.get(game_id, None)
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logger.error(f"שגיאה בקריאת הזדמנויות: {str(e)}")
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
        "token": B365_TOKEN,
        "_t": int(time.time())  # מניעת מטמון
    }
    
    logger.info(f"מבצע קריאה ל-API של B365: {B365_API_URL}")
    
    try:
        response = requests.get(B365_API_URL, params=params, timeout=15)
        logger.info(f"התקבלה תשובה מ-B365 עם סטטוס: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"שגיאה בקריאה ל-API: סטטוס {response.status_code}"
            logger.error(error_msg)
            return jsonify({"error": error_msg, "details": response.text[:200]}), 500
        
        try:
            games_data = response.json()
        except Exception as e:
            error_msg = f"שגיאה בפענוח JSON: {str(e)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg, "details": response.text[:200]}), 500
        
        # בדיקה אם יש תוצאות
        if 'results' not in games_data or not games_data['results']:
            logger.warning("אין תוצאות מה-API של B365")
            return jsonify({"warning": "אין משחקים זמינים כרגע", "raw_data": games_data}), 200
        
        # ספירת משחקים לפי סטטוס
        live_count = sum(1 for g in games_data['results'] if g.get('time_status') == '1')
        upcoming_count = sum(1 for g in games_data['results'] if g.get('time_status') == '0')
        
        logger.info(f"התקבלו {len(games_data['results'])} משחקים, מתוכם {live_count} חיים ו-{upcoming_count} עתידיים")
        
        # עיבוד נתוני משחקים ושמירת ליינים
        processed_games = 0
        error_games = 0
        
        for game in games_data['results']:
            game_id = game.get('id')
            if not game_id:
                logger.warning(f"נמצא משחק ללא ID")
                continue
                
            try:
                # חילוץ נתוני ליין
                lines_data = extract_lines_from_game(game)
                
                # שמירת ליינים להיסטוריה
                try:
                    data_changed = save_game_lines(game_id, lines_data)
                except Exception as e:
                    logger.error(f"שגיאה בשמירת נתוני ליין למשחק {game_id}: {str(e)}")
                    data_changed = False
                
                # חישוב הזדמנויות רק אם הנתונים השתנו
                if data_changed:
                    try:
                        opportunity = calculate_opportunities(game_id, lines_data)
                        if opportunity and opportunity['type'] != 'neutral':
                            save_opportunity(game_id, opportunity)
                    except Exception as e:
                        logger.error(f"שגיאה בחישוב הזדמנויות למשחק {game_id}: {str(e)}")
                
                # קבלת הזדמנות קיימת אם יש
                try:
                    opportunity = get_opportunity(game_id)
                except Exception as e:
                    logger.error(f"שגיאה בקריאת הזדמנויות למשחק {game_id}: {str(e)}")
                    opportunity = None
                
                # הוספת מידע על הזדמנויות ונתוני ליין למשחק
                try:
                    add_opportunity_and_lines_to_game(game, opportunity)
                except Exception as e:
                    logger.error(f"שגיאה בהוספת נתוני הזדמנויות למשחק {game_id}: {str(e)}")
                
                processed_games += 1
            except Exception as e:
                logger.error(f"שגיאה כללית בעיבוד משחק {game_id}: {str(e)}")
                error_games += 1
        
        logger.info(f"הסתיים עיבוד נתונים: {processed_games} משחקים עובדו בהצלחה, {error_games} נכשלו")
        
        # הוספת מידע נוסף לתשובה
        response_data = games_data.copy()
        response_data['_meta'] = {
            'processed': processed_games,
            'errors': error_games,
            'timestamp': datetime.now().isoformat()
        }
        
        # הגדרות לאי-שמירת מטמון
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        error_msg = f"שגיאה בקריאה ל-API: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    # קריאה ל-API של B365 עבור משחק ספציפי
    params = {
        "event_id": game_id,
        "token": B365_TOKEN
    }
    
    try:
        response = requests.get(B365_API_URL, params=params, timeout=15)
        logger.info(f"התקבלה תשובה עבור משחק {game_id} עם סטטוס: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"שגיאה בקריאה ל-API עבור משחק {game_id}: סטטוס {response.status_code}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500
        
        try:
            game_data = response.json()
        except Exception as e:
            error_msg = f"שגיאה בפענוח JSON למשחק {game_id}: {str(e)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500
        
        # הוספת מידע נוסף על ליינים והזדמנויות
        if 'results' in game_data and game_data['results']:
            game = game_data['results'][0]
            
            # קבלת הזדמנות קיימת אם יש
            try:
                opportunity = get_opportunity(game_id)
            except Exception as e:
                logger.error(f"שגיאה בקריאת הזדמנויות למשחק {game_id}: {str(e)}")
                opportunity = None
            
            # הוספת מידע על הזדמנויות ונתוני ליין למשחק
            try:
                add_opportunity_and_lines_to_game(game, opportunity)
            except Exception as e:
                logger.error(f"שגיאה בהוספת נתוני הזדמנויות למשחק {game_id}: {str(e)}")
        
        return jsonify(game_data)
    except Exception as e:
        error_msg = f"שגיאה בקריאת פרטי משחק {game_id}: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/stats')
def get_stats():
    # חישוב סטטיסטיקות מתוך הזדמנויות
    try:
        opportunities = {}
        if os.path.exists(OPPORTUNITIES_FILE):
            try:
                with open(OPPORTUNITIES_FILE, 'r') as f:
                    opportunities = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                opportunities = {}
        
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
            response = requests.get(B365_API_URL, params=params, timeout=10)
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
            logger.error(f"שגיאה בספירת משחקים: {str(e)}")
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
        logger.error(f"שגיאה בחישוב סטטיסטיקות: {str(e)}")
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
    try:
        history = get_game_lines_history(game_id)
        return jsonify(history)
    except Exception as e:
        logger.error(f"שגיאה בקריאת היסטוריית ליינים למשחק {game_id}: {str(e)}")
        return jsonify([])

@app.route('/api/health')
def health_check():
    """בדיקת בריאות מערכת"""
    # בדיקה פשוטה לB365 API
    try:
        response = requests.get(B365_API_URL, params={"token": B365_TOKEN, "sport_id": SPORT_ID}, timeout=5)
        api_status = response.status_code == 200
    except Exception as e:
        logger.error(f"שגיאה בבדיקת API: {str(e)}")
        api_status = False
    
    return jsonify({
        "status": "ok" if is_config_valid and api_status else "error",
        "config_valid": is_config_valid,
        "api_available": api_status,
        "environment": "production" if 'RENDER' in os.environ else "development",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/check-b365')
def check_b365():
    """בדיקה ידנית של API B365"""
    try:
        logger.info("התחלת בדיקה ידנית של B365 API")
        response = requests.get(B365_API_URL, params={"token": B365_TOKEN, "sport_id": SPORT_ID}, timeout=10)
        
        logger.info(f"התקבלה תשובה עם סטטוס: {response.status_code}")
        
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
                    "message": "התחברות לAPI הצליחה אבל אין משחקים",
                    "raw_response": data,
                    "timestamp": datetime.now().isoformat()
                })
        else:
            return jsonify({
                "status": "error",
                "message": f"שגיאה בחיבור לAPI: {response.status_code}",
                "response_text": response.text[:500],
                "timestamp": datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"שגיאה בבדיקה: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

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
    
    # טיפול ישיר במידע שנראה בתמונה שנייה
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
        except (ValueError, IndexError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"שגיאה בחישוב ליינים מתוצאה: {str(e)}")
    
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
        lines_data['total']# עיגול הערכים לחצי הקרוב (מקובל בהימורים)
    if lines_data['spread']:
        lines_data['spread'] = round(lines_data['spread'] * 2) / 2
    
    if lines_data['total']:
        lines_data['total'] = round(lines_data['total'] * 2) / 2
    
    return lines_data

# פונקציה לחישוב הזדמנויות
def calculate_opportunities(game_id, current_lines):
    try:
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
    except Exception as e:
        logger.error(f"שגיאה בחישוב הזדמנויות למשחק {game_id}: {str(e)}")
        return {
            'type': 'neutral',
            'reason': '',
            'spread_diff': 0,
            'total_diff': 0,
            'time_status': current_lines.get('time_status'),
            'timestamp': datetime.now().isoformat()
        }

# פונקציה להוספת מידע על הזדמנויות ונתוני ליין למשחק
def add_opportunity_and_lines_to_game(game, opportunity):
    try:
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
        else:
            # אם אין היסטוריה, נשים ערכי ברירת מחדל
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
        
        # הוספת מידע על הזדמנויות
        if opportunity:
            game['opportunity_type'] = opportunity.get('type', 'neutral')
            game['opportunity_reason'] = opportunity.get('reason', '')
        else:
            game['opportunity_type'] = 'neutral'
            game['opportunity_reason'] = ''
    except Exception as e:
        logger.error(f"שגיאה בהוספת מידע למשחק: {str(e)}")
        # הגדרת ערכי ברירת מחדל
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
