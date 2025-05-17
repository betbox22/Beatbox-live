
// main.js - קוד JavaScript עבור BETBOX

// גלובליים
const API_BASE_URL = '/api';
let refreshInterval = null;
let lastUpdateTime = null;
let activeTab = 'live';
let currentStats = {};
let currentGames = [];

// אתחול האפליקציה כאשר המסמך נטען
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

function initApp() {
    // אתחול אזור זמן נוכחי
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // טעינת נתונים ראשונית
    loadStats();
    loadGames();
    
    // הגדרת אינטרוול עדכון כל 30 שניות
    refreshInterval = setInterval(function() {
        loadStats();
        loadGames();
    }, 30000);
    
    // הגדרת מאזינים לאירועים
    document.getElementById('refresh-button').addEventListener('click', refreshData);
    document.getElementById('league-filter').addEventListener('change', filterGames);
    document.getElementById('opportunity-filter').addEventListener('change', filterGames);
    document.getElementById('min-line-movement').addEventListener('input', filterGames);
    
    // הגדרת מאזינים לטאבים
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            activeTab = this.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            filterGames();
        });
    });
    
    // הגדרת מאזין לסגירת מודאל פרטי משחק
    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('game-details-modal').style.display = 'none';
    });
    
    // סגירת מודאל בלחיצה מחוץ לתוכן
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('game-details-modal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('he-IL');
    document.getElementById('current-time').textContent = timeString;
}

async function loadStats() {
    try {
        showLoader(true);
        const response = await fetch(`${API_BASE_URL}/stats`);
        currentStats = await response.json();
        updateStatsUI(currentStats);
    } catch (error) {
        console.error('שגיאה בטעינת סטטיסטיקות:', error);
    } finally {
        showLoader(false);
    }
}

async function loadGames() {
    try {
        showLoader(true);
        const response = await fetch(`${API_BASE_URL}/games`);
        const data = await response.json();
        
        if (data && data.results) {
            currentGames = data.results;
            filterGames();
            lastUpdateTime = new Date();
            document.getElementById('last-update-time').textContent = `עודכן לאחרונה: ${lastUpdateTime.toLocaleTimeString('he-IL')}`;
        }
    } catch (error) {
        console.error('שגיאה בטעינת משחקים:', error);
    } finally {
        showLoader(false);
    }
}

function updateStatsUI(stats) {
    document.getElementById('opportunity-percentage').textContent = `${stats.opportunity_percentage}%`;
    document.getElementById('red-opportunities').textContent = stats.red_opportunities;
    document.getElementById('green-opportunities').textContent = stats.green_opportunities;
    document.getElementById('blue-opportunities').textContent = stats.blue_opportunities;
    document.getElementById('total-live').textContent = stats.total_live;
    document.getElementById('total-upcoming').textContent = stats.total_upcoming;
}

function filterGames() {
    const leagueFilter = document.getElementById('league-filter').value;
    const opportunityFilter = document.getElementById('opportunity-filter').value;
    const minLineMovement = parseFloat(document.getElementById('min-line-movement').value) || 0;
    
    // סינון לפי מצב משחק (חי/עתידי)
    let filteredGames = currentGames.filter(game => {
        if (activeTab === 'live') {
            return game.time_status === '1'; // משחק חי
        } else if (activeTab === 'upcoming') {
            return game.time_status === '0'; // משחק עתידי
        }
        return true; // הכל
    });
    
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
    
    renderGamesTable(filteredGames);
}

function renderGamesTable(games) {
    const tableBody = document.getElementById('games-table-body');
    tableBody.innerHTML = '';
    
    if (!games || games.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="10">לא נמצאו משחקים</td></tr>';
        return;
    }
    
    games.forEach(game => {
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
        
        // בניית תאי הטבלה
        row.innerHTML = `
            <td>${game.league?.name || ''}</td>
            <td>
                ${game.home.name}<br>
                <small>${game.away.name}</small>
            </td>
            <td>${formatGameTime(game)}</td>
            <td>${formatGameScore(game)}</td>
            <td class="${getDirectionClass(game.spread_direction)}">
                ${formatSpread(game.live_spread)}<br>
                <small>${formatDiff(game.live_spread_diff)}</small>
            </td>
            <td class="${getDirectionClass(game.total_direction)}">
                ${formatTotal(game.live_total)}<br>
                <small>${formatDiff(game.live_total_diff)}</small>
            </td>
            <td class="${game.opportunity_type}">
                ${formatOpportunityType(game.opportunity_type)}<br>
                <small>${game.opportunity_reason || ''}</small>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

function showGameDetails(gameId) {
    // הצגת לואדר במודאל
    const modalContent = document.querySelector('.modal-content');
    modalContent.innerHTML = '<div class="loader"></div>';
    document.getElementById('game-details-modal').style.display = 'block';
    
    // קריאה לAPI לקבלת נתוני משחק מפורטים
    fetch(`${API_BASE_URL}/game/${gameId}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.results && data.results.length > 0) {
                renderGameDetails(data.results[0]);
            } else {
                modalContent.innerHTML = '<p>לא נמצאו נתונים למשחק זה</p>';
            }
        })
        .catch(error => {
            console.error('שגיאה בטעינת פרטי משחק:', error);
            modalContent.innerHTML = '<p>שגיאה בטעינת נתוני המשחק</p>';
        });
        
    // בנוסף, טעינת היסטוריית ליינים
    fetch(`${API_BASE_URL}/game/${gameId}/lines_history`)
        .then(response => response.json())
        .then(history => {
            renderLinesHistory(history);
        })
        .catch(error => {
            console.error('שגיאה בטעינת היסטוריית ליינים:', error);
        });
}

function renderGameDetails(game) {
    const modalContent = document.querySelector('.modal-content');
    
    // בניית HTML של פרטי המשחק
    let gameDetails = `
        <span class="close">&times;</span>
        <h2>${game.league?.name}: ${game.home.name} vs ${game.away.name}</h2>
        
        <div class="game-info">
            <div class="game-status">
                <p>סטטוס: ${formatGameStatus(game.time_status)}</p>
                <p>תאריך: ${formatDate(game.time)}</p>
                <p>שעה: ${formatTime(game.time)}</p>
            </div>
            
            <div class="score-info">
                <h3>תוצאה</h3>
                <p>${game.home.name}: ${getHomeScore(game)}</p>
                <p>${game.away.name}: ${getAwayScore(game)}</p>
            </div>
            
            <div class="line-info">
                <h3>נתוני ליין</h3>
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>פתיחה</th>
                            <th>התחלה</th>
                            <th>נוכחי</th>
                            <th>שינוי</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>ספרד</td>
                            <td>${formatSpread(game.opening_spread)}</td>
                            <td>${formatSpread(game.start_spread)}</td>
                            <td>${formatSpread(game.live_spread)}</td>
                            <td class="${getDirectionClass(game.spread_direction)}">${formatDiff(game.live_spread_diff)}</td>
                        </tr>
                        <tr>
                            <td>טוטאל</td>
                            <td>${formatTotal(game.opening_total)}</td>
                            <td>${formatTotal(game.start_total)}</td>
                            <td>${formatTotal(game.live_total)}</td>
                            <td class="${getDirectionClass(game.total_direction)}">${formatDiff(game.live_total_diff)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="opportunity-info ${game.opportunity_type}">
                <h3>הזדמנות</h3>
                <p>סוג: ${formatOpportunityType(game.opportunity_type)}</p>
                <p>סיבה: ${game.opportunity_reason || 'אין'}</p>
            </div>
        </div>
        
        <div id="lines-history-chart">
            <!-- כאן ייטען גרף היסטוריית ליינים -->
        </div>
    `;
    
    modalContent.innerHTML = gameDetails;
    
    // הגדרת אירוע סגירת מודאל
    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('game-details-modal').style.display = 'none';
    });
}

function renderLinesHistory(history) {
    if (!history || history.length === 0) {
        return;
    }
    
    // יצירת נתונים מעובדים לגרף
    const chartData = history.map(line => ({
        timestamp: new Date(line.timestamp),
        spread: line.spread,
        total: line.total
    }));
    
    // יצירת גרף פשוט
    const historyContainer = document.getElementById('lines-history-chart');
    historyContainer.innerHTML = `
        <h3>היסטוריית ליינים</h3>
        <table>
            <thead>
                <tr>
                    <th>זמן</th>
                    <th>ספרד</th>
                    <th>טוטאל</th>
                </tr>
            </thead>
            <tbody>
                ${chartData.map(data => `
                    <tr>
                        <td>${data.timestamp.toLocaleTimeString('he-IL')}</td>
                        <td>${formatSpread(data.spread)}</td>
                        <td>${formatTotal(data.total)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function refreshData() {
    loadStats();
    loadGames();
}

function showLoader(show) {
    const loader = document.getElementById('loader');
    if (show) {
        loader.classList.remove('hidden');
    } else {
        loader.classList.add('hidden');
    }
}

// פונקציות עזר לפורמט
function formatGameTime(game) {
    if (game.time_status === '1') {
        // משחק חי
        const timer = game.timer || {};
        const quarter = timer.q || '';
        const time = timer.tm || '';
        return `רבע ${quarter}<br><small>${time}</small>`;
    } else if (game.time_status === '0') {
        // משחק עתידי
        return formatTime(game.time);
    }
    return '';
}

function formatGameScore(game) {
    if (!game.ss) return '-';
    
    const scores = game.ss.split('-');
    if (scores.length !== 2) return game.ss;
    
    const homeScore = scores[0];
    const awayScore = scores[1];
    
    return `${homeScore}<br><small>${awayScore}</small>`;
}

function getHomeScore(game) {
    if (!game.ss) return '-';
    const scores = game.ss.split('-');
    return scores[0] || '-';
}

function getAwayScore(game) {
    if (!game.ss) return '-';
    const scores = game.ss.split('-');
    return scores.length > 1 ? scores[1] : '-';
}

function formatGameStatus(status) {
    switch (status) {
        case '0': return 'עתידי';
        case '1': return 'משחק חי';
        case '2': return 'הסתיים';
        case '3': return 'נדחה';
        case '4': return 'בוטל';
        default: return 'לא ידוע';
    }
}

function formatDate(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('he-IL');
}

function formatTime(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' });
}

function formatSpread(spread) {
    if (spread === null || spread === undefined) return '-';
    return spread > 0 ? `+${spread.toFixed(1)}` : spread.toFixed(1);
}

function formatTotal(total) {
    if (total === null || total === undefined) return '-';
    return total.toFixed(1);
}

function formatDiff(diff) {
    if (diff === null || diff === undefined) return '';
    return diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
}

function formatOpportunityType(type) {
    switch (type) {
        case 'green': return 'ירוקה';
        case 'red': return 'אדומה';
        case 'blue': return 'כחולה';
        default: return 'אין';
    }
}

function getDirectionClass(direction) {
    switch (direction) {
        case 'up': return 'green';
        case 'down': return 'red';
        default: return '';
    }
}
