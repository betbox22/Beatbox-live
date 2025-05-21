from flask import Flask, jsonify, render_template, request
import requests
from datetime import datetime
import time
import json
import os

app = Flask(__name__)

# קבועים
API_TOKEN = "219761-iALwqep7Hy1aCl"
INPLAY_API_URL = f"http://api.b365api.com/v3/events/inplay?sport_id=18&token={API_TOKEN}"
ODDS_API_URL = f"https://api.b365api.com/v2/event/odds?token={API_TOKEN}&event_id="

# הגדרות קוד המרה
OPPORTUNITY_TYPES = {
    "green": "חיובי",
    "red": "שלילי",
    "neutral": "ניטרלי"
}

@app.route('/')
def index():
    """
    עמוד הבית
    """
    return render_template('index.html')

@app.route('/api/games')
def get_games():
    """
    מחזיר את כל המשחקים החיים עם הליינים המעודכנים
    """
    live_games = fetch_live_games()
    return jsonify(live_games)

@app.route('/api/game/<game_id>/odds')
def get_game_odds(game_id):
    """
    מחזיר את הליינים המעודכנים עבור משחק ספציפי
    """
    if not game_id or not str(game_id).isdigit():
        return jsonify({"error": "Invalid game ID"}), 400
    
    # בהנחה שקיבלנו bet365_id
    odds_data = fetch_odds_data(game_id)
    if odds_data:
        # עיבוד הנתונים לפורמט שהלקוח מצפה לו
        formatted_odds = {
            "home_spread": None,
            "away_spread": None,
            "total": None,
            "is_home_favorite": False
        }
        
        if 'results' in odds_data:
            for market in odds_data['results']:
                # חילוץ ספרד
                if market.get('market_id') == '18_1':
                    for odd in market.get('odds', []):
                        if 'handicap' in odd:
                            handicap_value = float(odd['handicap'])
                            if handicap_value > 0:
                                formatted_odds['home_spread'] = handicap_value
                                formatted_odds['away_spread'] = -handicap_value
                                formatted_odds['is_home_favorite'] = False
                            else:
                                formatted_odds['home_spread'] = handicap_value
                                formatted_odds['away_spread'] = -handicap_value
                                formatted_odds['is_home_favorite'] = True
                            break
                
                # חילוץ טוטאל
                elif market.get('market_id') == '18_2':
                    for odd in market.get('odds', []):
                        if 'handicap' in odd and odd.get('name') == 'Over':
                            formatted_odds['total'] = float(odd['handicap'])
                            break
        
        return jsonify(formatted_odds)
    
    return jsonify({"error": "Odds data not available"}), 404

def fetch_live_games():
    """
    מושך משחקים חיים מ-API של Bet365
    
    Returns:
        list: רשימת משחקים חיים עם כל הנתונים הדרושים
    """
    games = []
    try:
        response = requests.get(INPLAY_API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') == 1 and 'results' in data:
                # מכין כל משחק עם נתונים מעובדים
                for game in data['results']:
                    # מחלץ את הליינים עבור כל משחק
                    lines = extract_lines_from_game(game)
                    
                    # מכין מידע על הזדמנויות
                    opportunity_data = extract_opportunities(game)
                    
                    # הוספת הנתונים המעובדים לאובייקט המשחק
                    game_data = {
                        'id': game.get('id'),
                        'league': game.get('league', {}).get('name', 'Unknown'),
                        'home_team': game.get('home', {}).get('name', 'Home'),
                        'away_team': game.get('away', {}).get('name', 'Away'),
                        'home_score': lines['home_team_points'],
                        'away_score': lines['away_team_points'],
                        'home_spread': lines['home_spread'],
                        'away_spread': lines['away_spread'],
                        'total': lines['total'],
                        'is_home_favorite': lines['is_home_favorite'],
                        'period': game.get('timer', {}).get('q', '1'),
                        'time_remaining': format_timer(game.get('timer', {})),
                        'bet365_id': game.get('bet365_id'),
                        'timestamp': datetime.now().isoformat(),
                        'opportunity_type': opportunity_data.get('opportunity_type', 'neutral'),
                        'opportunity_reason': opportunity_data.get('opportunity_reason', ''),
                        'spread_direction': game.get('spread_direction', 'neutral'),
                        'total_direction': game.get('total_direction', 'neutral'),
                        'spread_flag': game.get('spread_flag', 'neutral'),
                        'live_spread': game.get('live_spread'),
                        'live_total': game.get('live_total')
                    }
                    games.append(game_data)
        
        # מיין את המשחקים לפי ליגה
        games.sort(key=lambda g: g['league'])
                    
    except Exception as e:
        print(f"Error fetching live games: {e}")
    
    return games

def extract_lines_from_game(game_data):
    """
    מחלץ את הליינים ממשחק בזמן אמת
    
    Args:
        game_data (dict): נתוני משחק מ-API של Bet365
    
    Returns:
        dict: מילון עם הליינים המחולצים (ספרד וטוטאל)
    """
    lines = {
        'home_spread': None,
        'away_spread': None,
        'total': None,
        'is_home_favorite': False,
        'home_team_points': 0,
        'away_team_points': 0
    }
    
    # חילוץ תוצאות (אם קיימות)
    if 'ss' in game_data and game_data['ss']:
        try:
            scores = game_data['ss'].split('-')
            if len(scores) == 2:
                lines['home_team_points'] = int(scores[0])
                lines['away_team_points'] = int(scores[1])
        except (ValueError, IndexError):
            pass
    
    # בדיקה האם קיים event_id של Bet365 (מפתח להצגת ליינים)
    if 'bet365_id' not in game_data:
        return lines
    
    # קריאה ל-API לקבלת נתוני ליינים עדכניים
    odds_data = fetch_odds_data(game_data['bet365_id'])
    
    # חילוץ הליינים מנתוני ה-API
    if odds_data and 'results' in odds_data:
        # חיפוש קוד השוק עבור ספרד בכדורסל (18_1)
        for market in odds_data['results']:
            # חילוץ ספרד (handicap)
            if market.get('market_id') == '18_1':  # קוד לספרד בכדורסל
                for odd in market.get('odds', []):
                    if 'handicap' in odd:
                        handicap_value = float(odd['handicap'])
                        if handicap_value > 0:
                            lines['home_spread'] = handicap_value
                            lines['away_spread'] = -handicap_value
                            lines['is_home_favorite'] = False
                        else:
                            lines['home_spread'] = handicap_value
                            lines['away_spread'] = -handicap_value
                            lines['is_home_favorite'] = True
                        break
            
            # חילוץ טוטאל (over/under)
            elif market.get('market_id') == '18_2':  # קוד לטוטאל בכדורסל
                for odd in market.get('odds', []):
                    if 'handicap' in odd and odd.get('name') == 'Over':
                        lines['total'] = float(odd['handicap'])
                        break

    # אם הספרד ריק, נחשב אותו לפי התוצאות הנוכחיות ונתוני המשחק שכבר קיימים
    if lines['home_spread'] is None:
        # נסה להשתמש בנתוני live_spread אם קיימים
        if 'live_spread' in game_data and game_data['live_spread'] is not None:
            try:
                spread_value = float(game_data['live_spread'])
                if 'spread_direction' in game_data and game_data['spread_direction'] == 'down':
                    lines['is_home_favorite'] = True
                    lines['home_spread'] = -abs(spread_value)
                    lines['away_spread'] = abs(spread_value)
                else:
                    lines['is_home_favorite'] = False
                    lines['home_spread'] = abs(spread_value)
                    lines['away_spread'] = -abs(spread_value)
            except (ValueError, TypeError):
                pass
        # או לפי הפרש הנקודות אם אין נתונים אחרים
        elif lines['home_team_points'] != 0 and lines['away_team_points'] != 0:
            point_diff = lines['home_team_points'] - lines['away_team_points']
            if point_diff > 0:
                lines['is_home_favorite'] = True
                lines['home_spread'] = -abs(point_diff)
                lines['away_spread'] = abs(point_diff)
            else:
                lines['is_home_favorite'] = False
                lines['home_spread'] = abs(point_diff)
                lines['away_spread'] = -abs(point_diff)
    
    # אם הטוטאל ריק, נסה להשתמש בנתוני live_total אם קיימים
    if lines['total'] is None and 'live_total' in game_data and game_data['live_total'] is not None:
        try:
            lines['total'] = float(game_data['live_total'])
        except (ValueError, TypeError):
            pass
    
    return lines

def fetch_odds_data(bet365_id):
    """
    פונקציה לקבלת נתוני אודס (קווי הימור) ממשחק ספציפי
    
    Args:
        bet365_id (str): מזהה המשחק ב-Bet365
    
    Returns:
        dict: מידע על קווי ההימור מה-API
    """
    url = f"{ODDS_API_URL}{bet365_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching odds data: {e}")
    
    return None

def extract_opportunities(game_data):
    """
    מחלץ מידע על הזדמנויות הימור מנתוני המשחק
    
    Args:
        game_data (dict): נתוני משחק מ-API של Bet365
    
    Returns:
        dict: מידע על הזדמנויות
    """
    opportunity_data = {
        'opportunity_type': 'neutral',
        'opportunity_reason': ''
    }
    
    # בדיקה האם יש נתוני הזדמנות במשחק
    if 'opportunity_type' in game_data:
        opportunity_data['opportunity_type'] = game_data['opportunity_type']
    
    if 'opportunity_reason' in game_data:
        opportunity_data['opportunity_reason'] = game_data['opportunity_reason']
    
    return opportunity_data

def format_timer(timer):
    """
    מעצב את תצוגת השעון במשחק
    
    Args:
        timer (dict): נתוני טיימר מ-API
    
    Returns:
        str: מחרוזת מעוצבת של הזמן
    """
    if not timer:
        return "00:00"
    
    minutes = int(timer.get('tm', 0))
    seconds = int(timer.get('ts', 0))
    
    return f"{minutes:02d}:{seconds:02d}"

if __name__ == '__main__':
    app.run(debug=True)
