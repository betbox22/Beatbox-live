// משתנים גלובליים
let liveGames = [];
let refreshInterval;

// כאשר הדף נטען
document.addEventListener('DOMContentLoaded', function() {
    // טען משחקים בפעם הראשונה
    fetchLiveGames();
    
    // הגדר רענון אוטומטי כל 30 שניות
    refreshInterval = setInterval(fetchLiveGames, 30000);
    
    // הוסף מאזין לכפתור הרענון הידני (אם קיים)
    const refreshButton = document.getElementById('refresh-button');
    if (refreshButton) {
        refreshButton.addEventListener('click', fetchLiveGames);
    }
});

/**
 * מביא משחקים חיים מהשרת ומציג אותם
 */
function fetchLiveGames() {
    fetch('/api/games')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(games => {
            liveGames = games;
            displayGames(games);
        })
        .catch(error => {
            console.error('Error fetching live games:', error);
            // אפשר להוסיף כאן הודעת שגיאה למשתמש
        });
}

/**
 * מציג את המשחקים החיים בדף
 * @param {Array} games - רשימת משחקים
 */
function displayGames(games) {
    const gamesContainer = document.getElementById('games-container');
    
    // אם אין משחקים, הצג הודעה
    if (!games || games.length === 0) {
        gamesContainer.innerHTML = '<div class="no-games">אין משחקים חיים כרגע</div>';
        return;
    }
    
    // מיין משחקים לפי ליגות
    const gamesByLeague = groupGamesByLeague(games);
    
    // נקה את המכולה
    gamesContainer.innerHTML = '';
    
    // עבור על כל ליגה והוסף את המשחקים שלה
    for (const league in gamesByLeague) {
        const leagueGames = gamesByLeague[league];
        
        // צור כותרת ליגה
        const leagueHeader = document.createElement('div');
        leagueHeader.className = 'league-header';
        leagueHeader.textContent = league;
        gamesContainer.appendChild(leagueHeader);
        
        // צור מכולה למשחקי הליגה
        const leagueContainer = document.createElement('div');
        leagueContainer.className = 'league-games';
        
        // הוסף כל משחק בליגה
        leagueGames.forEach(game => {
            const gameElement = createGameElement(game);
            leagueContainer.appendChild(gameElement);
        });
        
        gamesContainer.appendChild(leagueContainer);
    }
}

/**
 * מקבץ משחקים לפי ליגה
 * @param {Array} games - רשימת משחקים
 * @returns {Object} - אובייקט עם משחקים מקובצים לפי ליגה
 */
function groupGamesByLeague(games) {
    const gamesByLeague = {};
    
    games.forEach(game => {
        const league = game.league || 'ליגה לא ידועה';
        
        if (!gamesByLeague[league]) {
            gamesByLeague[league] = [];
        }
        
        gamesByLeague[league].push(game);
    });
    
    return gamesByLeague;
}

/**
 * יוצר אלמנט HTML עבור משחק
 * @param {Object} game - נתוני המשחק
 * @returns {HTMLElement} - אלמנט HTML של המשחק
 */
function createGameElement(game) {
    const gameElement = document.createElement('div');
    gameElement.className = 'game-card';
    gameElement.id = `game-${game.id}`;
    
    // קבע צבע רקע לפי סוג ההזדמנות
    if (game.opportunity_type === 'green') {
        gameElement.classList.add('opportunity-positive');
    } else if (game.opportunity_type === 'red') {
        gameElement.classList.add('opportunity-negative');
    }
    
    // הוסף תוכן HTML למשחק
    gameElement.innerHTML = `
        <div class="game-header">
            <div class="game-period">רבע ${game.period}</div>
            <div class="game-time">${game.time_remaining}</div>
            <div class="refresh-odds" onclick="refreshGameOdds('${game.bet365_id}')">
                <i class="fas fa-sync-alt"></i>
            </div>
        </div>
        <div class="teams-container">
            <div class="team home-team">
                <div class="team-name">${game.home_team}</div>
                <div class="team-score">${game.home_score}</div>
                <div class="team-spread" id="home-spread-${game.id}"></div>
            </div>
            <div class="vs">VS</div>
            <div class="team away-team">
                <div class="team-name">${game.away_team}</div>
                <div class="team-score">${game.away_score}</div>
                <div class="team-spread" id="away-spread-${game.id}"></div>
            </div>
        </div>
        <div class="odds-container">
            <div class="total-container">
                <div class="label">סה"כ:</div>
                <div class="total-value" id="total-${game.id}"></div>
                ${getDirectionArrow(game.total_direction)}
            </div>
            <div class="spread-container">
                <div class="label">ספרד:</div>
                <div class="spread-value" id="spread-${game.id}"></div>
                ${getDirectionArrow(game.spread_direction)}
            </div>
        </div>
        ${game.opportunity_reason ? `<div class="opportunity-reason">${game.opportunity_reason}</div>` : ''}
    `;
    
    // עדכן את ערכי הספרד והטוטאל
    updateGameLines(game);
    
    return gameElement;
}

/**
 * מחזיר אייקון חץ לפי כיוון
 * @param {string} direction - כיוון (up, down, neutral)
 * @returns {string} - HTML של אייקון חץ
 */
function getDirectionArrow(direction) {
    if (direction === 'up') {
        return '<i class="fas fa-arrow-up up-arrow"></i>';
    } else if (direction === 'down') {
        return '<i class="fas fa-arrow-down down-arrow"></i>';
    }
    return '';
}

/**
 * מעדכן את הליינים (ספרד וטוטאל) למשחק ספציפי
 * @param {Object} game - נתוני המשחק
 */
function updateGameLines(game) {
    // הצגת ספרד
    const homeSpreadElement = document.getElementById(`home-spread-${game.id}`);
    const awaySpreadElement = document.getElementById(`away-spread-${game.id}`);
    const totalElement = document.getElementById(`total-${game.id}`);
    const spreadElement = document.getElementById(`spread-${game.id}`);
    
    if (homeSpreadElement && awaySpreadElement) {
        let homeSpreadDisplay = "-";
        let awaySpreadDisplay = "-";
        
        if (game.home_spread !== null && game.away_spread !== null) {
            if (game.is_home_favorite) {
                // הקבוצה הביתית מועדפת
                homeSpreadDisplay = `-${Math.abs(game.home_spread).toFixed(1)}`;
                awaySpreadDisplay = `+${Math.abs(game.away_spread).toFixed(1)}`;
            } else {
                // הקבוצה האורחת מועדפת
                homeSpreadDisplay = `+${Math.abs(game.home_spread).toFixed(1)}`;
                awaySpreadDisplay = `-${Math.abs(game.away_spread).toFixed(1)}`;
            }
        }
        
        homeSpreadElement.textContent = homeSpreadDisplay;
        awaySpreadElement.textContent = awaySpreadDisplay;
        
        // עדכון תצוגת ספרד מרכזית אם קיימת
        if (spreadElement) {
            const favoredTeam = game.is_home_favorite ? 'home' : 'away';
            const spreadValue = favoredTeam === 'home' ? game.home_spread : game.away_spread;
            
            if (spreadValue !== null) {
                spreadElement.textContent = Math.abs(spreadValue).toFixed(1);
            } else {
                spreadElement.textContent = "-";
            }
        }
    }
    
    // הצגת טוטאל
    if (totalElement) {
        const totalDisplay = game.total !== null ? game.total.toFixed(1) : "-";
        totalElement.textContent = totalDisplay;
    }
}

/**
 * מרענן את הליינים עבור משחק ספציפי
 * @param {string} bet365Id - המזהה של המשחק ב-Bet365
 */
function refreshGameOdds(bet365Id) {
    // הצג אנימציה של טעינה
    const refreshIcon = document.querySelector(`[onclick="refreshGameOdds('${bet365Id}')"] i`);
    if (refreshIcon) {
        refreshIcon.classList.add('rotating');
    }
    
    fetch(`/api/game/${bet365Id}/odds`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(odds => {
            // מצא את המשחק המתאים ועדכן את הליינים שלו
            const game = liveGames.find(g => g.bet365_id === bet365Id);
            if (game) {
                game.home_spread = odds.home_spread;
                game.away_spread = odds.away_spread;
                game.total = odds.total;
                game.is_home_favorite = odds.is_home_favorite;
                
                // עדכן את התצוגה
                updateGameLines(game);
            }
        })
        .catch(error => {
            console.error('Error refreshing odds:', error);
        })
        .finally(() => {
            // הסר את אנימציית הטעינה
            if (refreshIcon) {
                refreshIcon.classList.remove('rotating');
            }
        });
}

// עצור את הרענון האוטומטי כשהדף נסגר
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
