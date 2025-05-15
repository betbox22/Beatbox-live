from flask import Flask, jsonify, request, send_from_directory
import requests
import os

app = Flask(__name__)

API_TOKEN = os.environ.get('API_TOKEN', '219761-iALwqep7Hy1aCl')
API_BASE_URL = "https://api.b365api.com/v3"

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/live-games')
def get_live_games():
    sport_id = request.args.get('sport_id', 'all')
    
    basketball_games = []
    football_games = []
    
    # אם "הכל" או "כדורסל", נביא משחקי כדורסל
    if sport_id == 'all' or sport_id == '18':
        basketball_games = fetch_and_process_games('18')  # כדורסל
    
    # אם "הכל" או "כדורגל", נביא משחקי כדורגל
    if sport_id == 'all' or sport_id == '1':
        football_games = fetch_and_process_games('1')  # כדורגל
    
    return jsonify(basketball_games + football_games)

def fetch_and_process_games(sport_id):
    url = f"{API_BASE_URL}/events/inplay"
    params = {
        "sport_id": sport_id,
        "token": API_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        processed_games = []
        
        for game in data.get('results', []):
            # קבלת מידע בסיסי
            game_id = game.get('id', '')
            league_name = game.get('league', {}).get('name', '')
            home_name = game.get('home', {}).get('name', '')
            away_name = game.get('away', {}).get('name', '')
            score = game.get('ss', '0-0')
            
            # עיבוד זמן המשחק
            timer = game.get('timer', {})
            quarter = timer.get('q', '1')
            minutes = timer.get('tm', '0')
            seconds = timer.get('ts', '0')
            
            # פורמט זמן משחק שונה לפי הספורט
            if sport_id == '18':  # כדורסל
                sport_type = 'כדורסל'
                game_time = f"רבע {quarter} ({minutes}:{seconds.zfill(2)})"
            elif sport_id == '1':  # כדורגל
                sport_type = 'כדורגל'
                game_time = f"דקה {minutes}" if quarter == '1' else f"דקה {minutes} (מחצית {quarter})"
            else:
                sport_type = 'אחר'
                game_time = f"{minutes}:{seconds.zfill(2)}"
            
            # הדמיה של ליינים וזיהוי הזדמנויות
            # במציאות, נרצה לקבל את הליינים האמיתיים מה-API
            opening_line = 'Home -4.5, O/U 180.5'
            current_line = 'Away -1.5, O/U 190.5'
            
            # הדמיה של זיהוי הזדמנויות פשוט - במציאות יהיה אלגוריתם מורכב יותר
            opportunity_type = 'neutral'
            opportunity = ''
            
            # דוגמה פשוטה - אם יש פער תוצאות, נסמן כהזדמנות
            if '-' in score:
                home_score, away_score = map(int, score.split('-'))
                score_diff = home_score - away_score
                
                if abs(score_diff) > 7:
                    opportunity_type = 'green'
                    if score_diff > 0:
                        opportunity = 'המועדפת מובילה בהפרש משמעותי'
                    else:
                        opportunity = 'האנדרדוג מוביל בהפרש משמעותי'
                elif abs(score_diff) > 3:
                    opportunity_type = 'blue'
                    opportunity = 'פער נקודות משמעותי'
            
            # יצירת אובייקט המשחק לתצוגה
            processed_game = {
                'id': game_id,
                'sportType': sport_type,
                'league': league_name,
                'matchup': f"{home_name} vs {away_name}",
                'time': game_time,
                'score': score,
                'openingLine': opening_line,
                'currentLine': current_line,
                'difference': '<span class="difference-positive">+5.0</span>',
                'opportunity': opportunity,
                'opportunityType': opportunity_type
            }
            
            processed_games.append(processed_game)
        
        return processed_games
    except Exception as e:
        print(f"Error fetching games: {str(e)}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
