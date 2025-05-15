# הוסף לחלק הייבוא (בתחילת הקובץ)
from datetime import datetime, timedelta
import json

# הוסף את הפונקציות האלה לקובץ app.py
def calculate_difference(current, opening):
    """חישוב ההפרש בין ליין נוכחי לליין פתיחה"""
    if current is None or opening is None:
        return None
    
    try:
        return float(current) - float(opening)
    except (ValueError, TypeError):
        return None

def apply_flagging_logic(opening_spread, current_spread, opening_ou, current_ou, game_start_lines=None):
    """יישום לוגיקת דגלים וסימון צבעים"""
    flags = {
        "spread_flag": None,
        "ou_flag": None,
        "combined_flag": None
    }
    
    # בדיקת ההבדל בין פתיחה למצב נוכחי
    spread_diff = calculate_difference(current_spread, opening_spread)
    ou_diff = calculate_difference(current_ou, opening_ou)
    
    # לוגיקה 1: הבדל בין פתיחה לתחילת משחק
    if spread_diff is not None and ou_diff is not None:
        if abs(spread_diff) >= 2 and abs(ou_diff) >= 2:
            # קביעה אם חיובי או שלילי
            flags["combined_flag"] = "green" if (spread_diff > 0 and ou_diff > 0) else "red"
    
    # לוגיקה 2: תנועה משמעותית במשחק חי
    if game_start_lines and 'spread' in game_start_lines:
        start_spread = game_start_lines['spread']
        live_spread_diff = calculate_difference(current_spread, start_spread)
        
        if live_spread_diff is not None and abs(live_spread_diff) >= 7:
            flags["spread_flag"] = "green"
    
    if game_start_lines and 'over_under' in game_start_lines:
        start_ou = game_start_lines['over_under']
        live_ou_diff = calculate_difference(current_ou, start_ou)
        
        if live_ou_diff is not None and abs(live_ou_diff) >= 10:
            flags["ou_flag"] = "green"
    
    return flags

def calculate_shot_rate(game):
    """חישוב קצב זריקות"""
    # פשוט לוגיקה לחישוב זריקות לדקה
    # במציאות, תצטרך מידע מדויק יותר
    
    # דוגמה סינטטית - במימוש אמיתי, השתמש בנתונים אמיתיים
    import random
    
    shots_per_minute = random.uniform(2.0, 5.0)
    
    # סימון לפי קצב זריקות
    if shots_per_minute <= 3.0:
        return {"rate": shots_per_minute, "flag": "red"}
    elif shots_per_minute <= 4.0:
        return {"rate": shots_per_minute, "flag": None}
    else:
        return {"rate": shots_per_minute, "flag": "blue"}
