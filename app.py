# יבוא ספריות נדרשות
from flask import Flask, jsonify, request, send_from_directory
import requests
import os

# הגדרת האפליקציה כאשר הקבצים הסטטיים נמצאים בשורש הפרויקט
app = Flask(__name__, static_folder='.', static_url_path='')

# הגדרת הטוקן לשימוש ב-API
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # קוד ספורט עבור כדורסל

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
        return jsonify(response.json())
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
        return jsonify(response.json())
    except Exception as e:
        app.logger.error(f"Error fetching game details: {str(e)}")
        return jsonify({"error": f"שגיאה בקריאה ל-API: {str(e)}"}), 500

@app.route('/api/stats')
def get_stats():
    # החזרת סטטיסטיקות מחושבות (לדוגמה)
    # במקרה אמיתי, אלה יחושבו מתוך משחקים אמיתיים
    stats = {
        "opportunity_percentage": 48,
        "red_opportunities": 12,
        "green_opportunities": 18,
        "total_live": 15,
        "total_upcoming": 23
    }
    return jsonify(stats)

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
