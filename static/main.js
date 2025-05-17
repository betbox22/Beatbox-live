// הוספת פונקציית דיבאג
function debug(message, data) {
    console.log(`[DEBUG] ${message}`, data);
    // אפשר גם להציג בממשק אם רוצים
    // document.getElementById('debug-info').innerText += `${message}\n`;
}

async function loadGames() {
    try {
        showLoader(true);
        debug("מתחיל לטעון משחקים...");
        
        // הוספת פרמטר למניעת מטמון
        const timestamp = new Date().getTime();
        const response = await fetch(`${API_BASE_URL}/games?_t=${timestamp}`);
        
        debug(`תגובה התקבלה מהשרת: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            let errorText = '';
            try {
                const errorData = await response.json();
                errorText = errorData.error || response.statusText;
            } catch (e) {
                errorText = await response.text();
            }
            
            debug("שגיאה בתגובה מהשרת", errorText);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">שגיאה בטעינת נתונים: ${response.status} ${errorText}</td></tr>`;
            return;
        }
        
        const data = await response.json();
        debug("התקבלו נתונים מהשרת", data);
        
        // בדיקה אם יש שגיאה מפורשת
        if (data.error) {
            debug("שגיאה מהשרת", data.error);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">שגיאה: ${data.error}</td></tr>`;
            return;
        }
        
        // בדיקה אם יש אזהרה
        if (data.warning) {
            debug("אזהרה מהשרת", data.warning);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">${data.warning}</td></tr>`;
            return;
        }
        
        // בדיקה שיש תוצאות
        if (!data.results || !Array.isArray(data.results) || data.results.length === 0) {
            debug("אין משחקים בתוצאות", data);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">אין משחקים זמינים כרגע</td></tr>`;
            return;
        }
        
        debug(`התקבלו ${data.results.length} משחקים`);
        
        // בדיקת תקינות המשחקים
        let validGames = 0;
        data.results.forEach(game => {
            if (game && game.id) validGames++;
            else debug("נמצא משחק לא תקין", game);
        });
        
        debug(`${validGames} משחקים תקינים מתוך ${data.results.length}`);
        
        currentGames = data.results.filter(game => game && game.id);
        debug("משחקים לאחר סינון ראשוני", currentGames);
        
        filterGames();
        
        lastUpdateTime = new Date();
        document.getElementById('last-update-time').textContent = `עודכן לאחרונה: ${lastUpdateTime.toLocaleTimeString('he-IL')}`;
    } catch (error) {
        debug('שגיאה כללית בטעינת משחקים:', error);
        document.getElementById('games-table-body').innerHTML = 
            `<tr><td colspan="7">שגיאה בטעינת נתונים: ${error.message}</td></tr>`;
    } finally {
        showLoader(false);
    }
}

function filterGames() {
    debug(`סינון משחקים, מצב טאב: ${activeTab}, מספר משחקים: ${currentGames.length}`);
    
    // בדיקה בסיסית לפני סינון
    if (!currentGames || currentGames.length === 0) {
        debug("אין משחקים לסינון");
        document.getElementById('games-table-body').innerHTML = 
            `<tr><td colspan="7">אין משחקים זמינים כרגע</td></tr>`;
        return;
    }
    
    const leagueFilter = document.getElementById('league-filter').value;
    const opportunityFilter = document.getElementById('opportunity-filter').value;
    const minLineMovement = parseFloat(document.getElementById('min-line-movement').value) || 0;
    
    debug(`פילטרים: ליגה=${leagueFilter}, הזדמנות=${opportunityFilter}, תנועת-ליין=${minLineMovement}`);
    
    // סינון לפי מצב משחק (חי/עתידי)
    let filteredGames = currentGames.filter(game => {
        if (activeTab === 'live') {
            return game.time_status === '1'; // משחק חי
        } else if (activeTab === 'upcoming') {
            return game.time_status === '0'; // משחק עתידי
        }
        return true; // הכל
    });
    
    debug(`לאחר סינון סטטוס: ${filteredGames.length} משחקים`);
    
    // בדיקה אם הסינון הראשוני השאיר משחקים
    if (filteredGames.length === 0) {
        debug(`אין משחקים לאחר סינון סטטוס ${activeTab}`);
        document.getElementById('games-table-body').innerHTML = 
            `<tr><td colspan="7">אין משחקים ${activeTab === 'live' ? 'חיים' : (activeTab === 'upcoming' ? 'עתידיים' : '')} כרגע</td></tr>`;
        return;
    }
    
    // סינון נוסף לפי הפילטרים
    filteredGames = filteredGames.filter(game => {
        // בדיקת ליגה
        if (leagueFilter !== 'all') {
            const league = game.league?.name || '';
            if (!league.includes(leagueFilter)) return false;
        }
        
        // בדיקת סוג הזדמנות
        if (opportunityFilter !== 'all') {
            if (game.opportunity_type !== opportunityFilter) return false;
        }
        
        // בדיקת מינימום תנועת ליין
        const spreadDiff = Math.abs(game.live_spread_diff || 0);
        const totalDiff = Math.abs(game.live_total_diff || 0);
        if (spreadDiff < minLineMovement && totalDiff < minLineMovement) return false;
        
        return true;
    });
    
    debug(`לאחר כל הסינונים: ${filteredGames.length} משחקים`);
    
    renderGamesTable(filteredGames);
}
