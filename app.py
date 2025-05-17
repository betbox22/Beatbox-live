# טיפול שלב שני
# יבוא ספריות נדרשות
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

# הגדרת הטוקן לשימוש ב-API
B365_TOKEN = "219761-iALwqep7Hy1aCl"
B365_API_URL = "http://api.b365api.com/v3/events/inplay"
SPORT_ID = 18  # קוד ספורט עבור כדורסל

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/games')
def get_games():
    # קריאה ל-API של B365 והחזרת נתונים
    params = {
        "sport_id": SPORT_ID,
        "token": B365_TOKEN
    }
    
    # אם יש פרמטרים נוספים מהבקשה, הוסף אותם
    for key, value in request.args.items():
        params[key] = value
    
    response = requests.get(B365_API_URL, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "שגיאה בקריאה ל-API"}), 500

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    # קריאה ל-API של B365 עבור משחק ספציפי
    params = {
        "event_id": game_id,
        "token": B365_TOKEN
    }
    
    response = requests.get(B365_API_URL, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "שגיאה בקריאה ל-API"}), 500

@app.route('/api/stats')
def get_stats():
    # החזרת סטטיסטיקות מחושבות (לדוגמה)
    stats = {
        "opportunity_percentage": 48,
        "red_opportunities": 12,
        "green_opportunities": 18,
        "total_live": 15,
        "total_upcoming": 23
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
