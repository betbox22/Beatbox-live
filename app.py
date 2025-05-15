from flask import Flask, jsonify, request, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='static')

API_TOKEN = os.environ.get('API_TOKEN', '219761-iALwqep7Hy1aCl')
API_BASE_URL = "https://api.b365api.com/v3"

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/live-games')
def get_live_games():
    sport_id = request.args.get('sport_id', '18')
    url = f"{API_BASE_URL}/events/inplay"
    params = {"sport_id": sport_id, "token": API_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        games = []
        
        for game in data.get('results', []):
            game_id = game.get('id', '')
            league = game.get('league', {}).get('name', '')
            home = game.get('home', {}).get('name', '')
            away = game.get('away', {}).get('name', '')
            score = game.get('ss', '0-0')
            
            games.append({
                'id': game_id,
                'sportType': 'כדורסל',
                'league': league,
                'matchup': f"{home} vs {away}",
                'time': 'משחק חי',
                'score': score,
                'openingLine': 'ליין פתיחה',
                'startingLine': 'ליין התחלה',
                'currentLine': 'ליין נוכחי',
                'difference': '+0.0',
                'opportunity': '',
                'opportunityType': 'neutral'
            })
        
        return jsonify(games)
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
