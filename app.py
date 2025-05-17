@app.route('/api/games')
def get_games():
    # קריאה ל-API של B365 והחזרת נתונים
    params = {
        "sport_id": SPORT_ID,
        "token": B365_TOKEN
    }
    
    # נוסיף פרמטר לוגיקה מניעת מטמון
    params["_t"] = int(time.time())
    
    try:
        response = requests.get(B365_API_URL, params=params, timeout=15)
        
        # בדיקה אם התשובה תקינה
        if response.status_code != 200:
            error_msg = f"שגיאה בקריאה ל-API: סטטוס {response.status_code}"
            app.logger.error(error_msg)
            return jsonify({"error": error_msg, "details": response.text[:200]}), 500
        
        try:
            games_data = response.json()
        except Exception as e:
            error_msg = f"שגיאה בפענוח JSON: {str(e)}"
            app.logger.error(error_msg)
            return jsonify({"error": error_msg, "details": response.text[:200]}), 500
        
        # בדיקה אם יש תוצאות
        if 'results' not in games_data or not games_data['results']:
            app.logger.warning("אין תוצאות מה-API של B365")
            return jsonify({"warning": "אין משחקים זמינים כרגע", "raw_data": games_data}), 200
        
        # ספירת משחקים לפי סטטוס
        live_count = sum(1 for g in games_data['results'] if g.get('time_status') == '1')
        upcoming_count = sum(1 for g in games_data['results'] if g.get('time_status') == '0')
        
        app.logger.info(f"התקבלו {len(games_data['results'])} משחקים, מתוכם {live_count} חיים ו-{upcoming_count} עתידיים")
        
        # נוסיף תחילת עיבוד נתונים
        processed_games = 0
        error_games = 0
        
        # עיבוד נתוני משחקים
        for game in games_data['results']:
            game_id = game.get('id')
            if not game_id:
                app.logger.warning(f"נמצא משחק ללא ID: {game}")
                continue
                
            try:
                # חילוץ נתוני ליין
                lines_data = extract_lines_from_game(game)
                
                # שמירת ליינים להיסטוריה
                try:
                    data_changed = save_game_lines(game_id, lines_data)
                except Exception as e:
                    app.logger.error(f"שגיאה בשמירת נתוני ליין למשחק {game_id}: {str(e)}")
                    # נמשיך בכל זאת
                    data_changed = False
                
                # חישוב הזדמנויות רק אם הנתונים השתנו
                if data_changed:
                    try:
                        opportunity = calculate_opportunities(game_id, lines_data)
                        if opportunity and opportunity['type'] != 'neutral':
                            save_opportunity(game_id, opportunity)
                    except Exception as e:
                        app.logger.error(f"שגיאה בחישוב הזדמנויות למשחק {game_id}: {str(e)}")
                
                # קבלת הזדמנות קיימת אם יש
                try:
                    opportunity = get_opportunity(game_id)
                except Exception as e:
                    app.logger.error(f"שגיאה בקריאת הזדמנויות למשחק {game_id}: {str(e)}")
                    opportunity = None
                
                # הוספת מידע על הזדמנויות ונתוני ליין למשחק
                try:
                    add_opportunity_and_lines_to_game(game, opportunity)
                except Exception as e:
                    app.logger.error(f"שגיאה בהוספת נתוני הזדמנויות למשחק {game_id}: {str(e)}")
                
                processed_games += 1
            except Exception as e:
                app.logger.error(f"שגיאה כללית בעיבוד משחק {game_id}: {str(e)}")
                error_games += 1
        
        app.logger.info(f"הסתיים עיבוד נתונים: {processed_games} משחקים עובדו בהצלחה, {error_games} נכשלו")
        
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
        app.logger.error(error_msg)
        return jsonify({"error": error_msg}), 500
