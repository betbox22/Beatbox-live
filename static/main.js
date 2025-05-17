// הוסף את זה בתחילת הקובץ main.js

// פונקציית דיבאג מורחבת
function debug(message, data = null) {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('he-IL');
    
    if (data) {
        console.log(`[${timestamp}] ${message}`, data);
    } else {
        console.log(`[${timestamp}] ${message}`);
    }
    
    // אופציונלי: הוסף לוג על המסך
    /*
    const debugPanel = document.getElementById('debug-panel');
    if (debugPanel) {
        const logItem = document.createElement('div');
        logItem.textContent = `[${timestamp}] ${message}`;
        debugPanel.appendChild(logItem);
        debugPanel.scrollTop = debugPanel.scrollHeight;
    }
    */
}

// מודיפיקציה לפונקציית loadGames
async function loadGames() {
    try {
        showLoader(true);
        debug("מתחיל לטעון משחקים...");
        
        // הוספת חותמת זמן למניעת מטמון
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
        
        let data;
        try {
            data = await response.json();
            debug("התקבלו נתונים מהשרת", data);
        } catch (e) {
            debug("שגיאה בפענוח JSON", e);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">שגיאה בפענוח נתונים: ${e.message}</td></tr>`;
            return;
        }
        
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
        
        debug("בדיקת מבנה הנתונים", { 
            hasResults: 'results' in data, 
            resultsType: data.results ? typeof data.results : 'null',
            resultsLength: data.results ? data.results.length : 0
        });
        
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
        
        // הגדרת currentGames שימנע חפצים ריקים
        currentGames = data.results.filter(game => game && game.id);
        debug("משחקים לאחר סינון ראשוני", currentGames.length);
        
        // ניסיון להציג את המשחקים
        try {
            filterGames();
        } catch (e) {
            debug("שגיאה בסינון וטעינת משחקים", e);
            document.getElementById('games-table-body').innerHTML = 
                `<tr><td colspan="7">שגיאה בעיבוד הנתונים: ${e.message}</td></tr>`;
        }
        
        // עדכון זמן עדכון אחרון
        lastUpdateTime = new Date();
        const lastUpdateElement = document.getElementById('last-update-time');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = `עודכן לאחרונה: ${lastUpdateTime.toLocaleTimeString('he-IL')}`;
        }
    } catch (error) {
        debug('שגיאה כללית בטעינת משחקים:', error);
        document.getElementById('games-table-body').innerHTML = 
            `<tr><td colspan="7">שגיאה בטעינת נתונים: ${error.message}</td></tr>`;
    } finally {
        showLoader(false);
    }
}

// מודיפיקציה לרנדור המשחקים
function renderGamesTable(games) {
    debug(`מתחיל לרנדר טבלת משחקים עם ${games ? games.length : 0} משחקים`);
    
    const tableBody = document.getElementById('games-table-body');
    
    if (!tableBody) {
        debug("לא נמצא אלמנט games-table-body בדף");
        return;
    }
    
    // ניקוי הטבלה
    tableBody.innerHTML = '';
    
    // בדיקה אם יש משחקים
    if (!games || games.length === 0) {
        debug("אין משחקים להצגה");
        tableBody.innerHTML = '<tr><td colspan="7">לא נמצאו משחקים</td></tr>';
        return;
    }
    
    debug(`מרנדר ${games.length} משחקים`);
    
    // רינדור כל משחק
    games.forEach((game, index) => {
        try {
            debug(`מרנדר משחק ${index + 1}/${games.length}, ID: ${game.id}`);
            
            const row = document.createElement('tr');
            
            // צביעת רקע לפי סוג הזדמנות
            if (game.opportunity_type === 'green') {
                row.classList.add('highlight-green');
            } else if (game.opportunity_type === 'red') {
                row.classList.add('highlight-red');
            }
            
            // הגדרת שורה לחיצה שתפתח את פרטי המשחק
            row.classList.add('clickable');
            row.addEventListener('click', () => showGameDetails(game.id));
            
            // בניית תאי הטבלה עם בדיקות null
            row.innerHTML = `
                <td>${game.league?.name || ''}</td>
                <td>
                    ${game.home?.name || 'בית'}<br>
                    <small>${game.away?.name || 'חוץ'}</small>
                </td>
                <td>${formatGameTime(game)}</td>
                <td>${formatGameScore(game)}</td>
                <td class="${getDirectionClass(game.spread_direction || 'neutral')}">
                    ${formatSpread(game.live_spread)}<br>
                    <small>${formatDiff(game.live_spread_diff)}</small>
                </td>
                <td class="${getDirectionClass(game.total_direction || 'neutral')}">
                    ${formatTotal(game.live_total)}<br>
                    <small>${formatDiff(game.live_total_diff)}</small>
                </td>
                <td class="${game.opportunity_type || 'neutral'}">
                    ${formatOpportunityType(game.opportunity_type)}<br>
                    <small>${game.opportunity_reason || ''}</small>
                </td>
            `;
            
            tableBody.appendChild(row);
        } catch (e) {
            debug(`שגיאה ברינדור משחק ${index + 1}, ID: ${game?.id}:`, e);
        }
    });
    
    debug("סיים רינדור טבלת משחקים");
}
