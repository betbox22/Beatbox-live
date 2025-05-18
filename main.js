// main.js - קוד JavaScript עבור BETBOX

// גלובליים
const API_BASE_URL = '/api';
let refreshInterval = null;
let lastUpdateTime = null;
let activeTab = 'live';
let currentStats = {};
let currentGames = [];

// פונקציית דיבאג
function debug(message, data = null) {
const now = new Date();
const timestamp = now.toLocaleTimeString('he-IL');
if (data) {
console.log(`[${timestamp}] ${message}`, data);
} else {
console.log(`[${timestamp}] ${message}`);
}
}

// אתחול האפליקציה כאשר המסמך נטען
document.addEventListener('DOMContentLoaded', function() {
debug("מסמך נטען, מתחיל אתחול אפליקציה");
initApp();
});

function initApp() {
try {
debug("מתחיל אתחול אפליקציה");
// אתחול אזור זמן נוכחי
updateCurrentTime();
setInterval(updateCurrentTime, 1000);
// טעינת נתונים ראשונית
debug("טוען נתונים ראשוניים");
loadStats();
loadGames();
// הגדרת אינטרוול עדכון כל 30 שניות
debug("מגדיר אינטרוול רענון נתונים");
refreshInterval = setInterval(function() {
loadStats();
loadGames();
}, 30000);
// הגדרת מאזינים לאירועים
debug("מגדיר מאזיני אירועים");
const refreshButton = document.getElementById('refresh-button');
if (refreshButton) {
refreshButton.addEventListener('click', refreshData);
} else {
debug("אזהרה: לא נמצא כפתור רענון");
}
const leagueFilter = document.getElementById('league-filter');
if (leagueFilter) {
leagueFilter.addEventListener('change', filterGames);
} else {
debug("אזהרה: לא נמצא סנן ליגה");
}
const opportunityFilter = document.getElementById('opportunity-filter');
if (opportunityFilter) {
opportunityFilter.addEventListener('change', filterGames);
} else {
debug("אזהרה: לא נמצא סנן הזדמנויות");
}
const minLineMovement = document.getElementById('min-line-movement');
if (minLineMovement) {
minLineMovement.addEventListener('input', filterGames);
} else {
debug("אזהרה: לא נמצא שדה תנועת ליין מינימלית");
}
// הגדרת מאזינים לטאבים
const tabs = document.querySelectorAll('.tab');
if (tabs.length > 0) {
tabs.forEach(tab => {
tab.addEventListener('click', function() {
activeTab = this.dataset.tab;
tabs.forEach(t => t.classList.remove('active'));
this.classList.add('active');
filterGames();
});
});
} else {
debug("אזהרה: לא נמצאו טאבים");
}
// הגדרת מאזין לסגירת מודאל פרטי משחק
const closeModalButton = document.querySelector('.close');
if (closeModalButton) {
closeModalButton.addEventListener('click', function() {
const modal = document.getElementById('game-details-modal');
if (modal) modal.style.display = 'none';
});
} else {
debug("אזהרה: לא נמצא כפתור סגירת מודאל");
}
// סגירת מודאל בלחיצה מחוץ לתוכן
window.addEventListener('click', function(event) {
const modal = document.getElementById('game-details-modal');
if (modal && event.target === modal) {
modal.style.display = 'none';
}
});
debug("אתחול אפליקציה הסתיים בהצלחה");
} catch (error) {
console.error('שגיאה באתחול האפליקציה:', error);
}
}

function updateCurrentTime() {
try {
const now = new Date();
const timeString = now.toLocaleTimeString('he-IL');
const timeElement = document.getElementById('current-time');
if (timeElement) {
timeElement.textContent = timeString;
}
} catch (error) {
console.error('שגיאה בעדכון זמן נוכחי:', error);
}
}

async function loadStats() {
try {
debug("טוען סטטיסטיקות");
showLoader(true);
const timestamp = new Date().getTime();
const response = await fetch(`${API_BASE_URL}/stats?_t=${timestamp}`);
debug(`קיבלתי תשובה מ-API/stats: ${response.status}`);
if (!response.ok) {
throw new Error(`שגיאה בטעינת סטטיסטיקות: ${response.status}`);
}
currentStats = await response.json();
debug("נתוני סטטיסטיקות התקבלו", currentStats);
updateStatsUI(currentStats);
} catch (error) {
console.error('שגיאה בטעינת סטטיסטיקות:', error);
} finally {
showLoader(false);
}
}

async function loadGames() {
try {
debug("טוען משחקים");
showLoader(true);
const timestamp = new Date().getTime();
debug(`שולח בקשה ל-API/games?_t=${timestamp}`);
// מפעיל בקשת fetch עם timeout
const fetchPromise = fetch(`${API_BASE_URL}/games?_t=${timestamp}`);
const timeoutPromise = new Promise((_, reject) =>
setTimeout(() => reject(new Error('בקשה לשרת נכשלה עקב timeout')), 10000)
);
const response = await Promise.race([fetchPromise, timeoutPromise]);
debug(`קיבלתי תגובה מהשרת: ${response.status}`);
if (!response.ok) {
let errorMessage = `שגיאה בטעינת משחקים: ${response.status}`;
try {
const errorData = await response.json();
errorMessage += ` - ${errorData.error || errorData.message || response.statusText}`;
} catch {
errorMessage += ` - ${response.statusText}`;
}
throw new Error(errorMessage);
}
// נסיון לפרסר את התגובה כ-JSON
const data = await response.json();
debug(`התקבלו נתונים מהשרת, סוג: ${typeof data}`);
if (typeof data !== 'object') {
throw new Error('התגובה מהשרת אינה אובייקט תקין');
}
// בדיקה אם יש שדה results ואם הוא מערך
if (!data.results || !Array.isArray(data.results)) {
debug("אין תוצאות במידע שהתקבל", data);
document.getElementById('games-table-body').innerHTML =
`<tr><td colspan="7">אין משחקים זמינים כרגע</td></tr>`;
return;
}
debug(`נמצאו ${data.results.length} משחקים`);
// בדיקת כל אחד מהמשחקים לתקינות
const validGames = data.results.filter(game => game && typeof game === 'object' && game.id);
debug(`מתוך ${data.results.length} משחקים, ${validGames.length} תקינים`);
if (validGames.length === 0) {
document.getElementById('games-table-body').innerHTML =
`<tr><td colspan="7">אין משחקים תקינים בנתונים שהתקבלו</td></tr>`;
return;
}
// שמירת המשחקים התקינים במשתנה הגלובלי
currentGames = validGames;
// סינון והצגת המשחקים
filterGames();
// עדכון זמן טעינה אחרון
lastUpdateTime = new Date();
const lastUpdateElement = document.getElementById('last-update-time');
if (lastUpdateElement) {
lastUpdateElement.textContent = `עודכן לאחרונה: ${lastUpdateTime.toLocaleTimeString('he-IL')}`;
}
} catch (error) {
console.error('שגיאה בטעינת משחקים:', error);
document.getElementById('games-table-body').innerHTML =
`<tr><td colspan="7">שגיאה בטעינת נתונים: ${error.message}</td></tr>`;
} finally {
showLoader(false);
}
}

function updateStatsUI(stats) {
try {
debug("מעדכן ממשק סטטיסטיקות");
const opportunityPercentage = document.getElementById('opportunity-percentage');
if (opportunityPercentage) {
opportunityPercentage.textContent = `${stats.opportunity_percentage || 0}%`;
}
const redOpportunities = document.getElementById('red-opportunities');
if (redOpportunities) {
redOpportunities.textContent = stats.red_opportunities || 0;
}
const greenOpportunities = document.getElementById('green-opportunities');
if (greenOpportunities) {
greenOpportunities.textContent = stats.green_opportunities || 0;
}
const blueOpportunities = document.getElementById('blue-opportunities');
if (blueOpportunities) {
blueOpportunities.textContent = stats.blue_opportunities || 0;
}
const totalLive = document.getElementById('total-live');
if (totalLive) {
totalLive.textContent = stats.total_live || 0;
}
const totalUpcoming = document.getElementById('total-upcoming');
if (totalUpcoming) {
totalUpcoming.textContent = stats.total_upcoming || 0;
}
} catch (error) {
console.error('שגיאה בעדכון ממשק סטטיסטיקות:', error);
}
}

function filterGames() {
try {
debug(`סינון משחקים, מצב טאב: ${activeTab}, מספר משחקים: ${currentGames.length}`);
// אם אין משחקים, הצג הודעה מתאימה
if (!currentGames || currentGames.length === 0) {
document.getElementById('games-table-body').innerHTML =
`<tr><td colspan="7">אין משחקים זמינים כרגע</td></tr>`;
return;
}
// קריאה לערכי הסינון
const leagueFilter = document.getElementById('league-filter')?.value || 'all';
const opportunityFilter = document.getElementById('opportunity-filter')?.value || 'all';
const minLineMovementValue = document.getElementById('min-line-movement')?.value || '0';
const minLineMovement = parseFloat(minLineMovementValue) || 0;
debug(`פילטרים: ליגה=${leagueFilter}, הזדמנות=${opportunityFilter}, תנועת-ליין=${minLineMovement}`);
// סינון לפי מצב משחק (חי/עתידי)
let filteredGames = currentGames.filter(game => {
// נגישות בטוחה לנתונים
if (!game) return false;
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
try {
// בדיקת ליגה
if (leagueFilter !== 'all') {
const league = (game.league && game.league.name) ? game.league.name : '';
if (league && !league.includes(leagueFilter)) return false;
}
// בדיקת סוג הזדמנות
if (opportunityFilter !== 'all') {
const opportunityType = game.opportunity_type || 'neutral';
if (opportunityType !== opportunityFilter) return false;
}
// בדיקת מינימום תנועת ליין
const spreadDiff = Math.abs(game.live_spread_diff || 0);
const totalDiff = Math.abs(game.live_total_diff || 0);
if (spreadDiff < minLineMovement && totalDiff < minLineMovement) return false;
return true;
} catch (e) {
debug(`שגיאה בפילטור משחק: ${e.message}`);
return false;
}
});
debug(`לאחר כל הסינונים: ${filteredGames.length} משחקים`);
// רינדור הטבלה
renderGamesTable(filteredGames);
} catch (error) {
console.error('שגיאה בסינון משחקים:', error);
document.getElementById('games-table-body').innerHTML =
`<tr><td colspan="7">שגיאה בעיבוד הנתונים: ${error.message}</td></tr>`;
}
}

function renderGamesTable(games) {
try {
debug(`מתחיל רינדור טבלת משחקים, ${games.length} משחקים`);
const tableBody = document.getElementById('games-table-body');
if (!tableBody) {
debug("שגיאה: לא נמצא אלמנט games-table-body");
return;
}
// ניקוי הטבלה
tableBody.innerHTML = '';
// בדיקה אם יש משחקים
if (!games || games.length === 0) {
tableBody.innerHTML = '<tr><td colspan="7">לא נמצאו משחקים</td></tr>';
return;
}
// רינדור כל משחק
let rowsRendered = 0;
games.forEach((game, index) => {
try {
// יצירת שורה חדשה
const row = document.createElement('tr');
// בדיקת נתונים קריטיים
const hasHomeTeam = game.home && game.home.name;
const hasAwayTeam = game.away && game.away.name;
if (!hasHomeTeam || !hasAwayTeam) {
debug(`שגיאה: משחק ${index} חסרים נתוני קבוצות`, game);
return; // דלג על המשחק הזה
}
// צביעת רקע לפי סוג הזדמנות
const opportunityType = game.opportunity_type || 'neutral';
if (opportunityType === 'green') {
row.classList.add('highlight-green');
} else if (opportunityType === 'red') {
row.classList.add('highlight-red');
}
// הגדרת שורה לחיצה שתפתח את פרטי המשחק
row.classList.add('clickable');
row.addEventListener('click', () => {
if (game.id) showGameDetails(game.id);
});
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
rowsRendered++;
} catch (e) {
debug(`שגיאה ברינדור משחק ${index}: ${e.message}`);
}
});
debug(`רינדור טבלה הסתיים, הוצגו ${rowsRendered} משחקים מתוך ${games.length}`);
} catch (error) {
console.error('שגיאה ברינדור טבלת משחקים:', error);
const tableBody = document.getElementById('games-table-body');
if (tableBody) {
tableBody.innerHTML = `<tr><td colspan="7">שגיאה בהצגת הנתונים: ${error.message}</td></tr>`;
}
}
}

function showGameDetails(gameId) {
try {
debug(`מציג פרטי משחק ${gameId}`);
const modalElement = document.getElementById('game-details-modal');
if (!modalElement) {
debug("שגיאה: לא נמצא אלמנט מודאל");
return;
}
// הצגת המודאל
modalElement.style.display = 'block';
// הצגת לואדר במודאל
const modalContent = document.querySelector('.modal-content');
if (!modalContent) {
debug("שגיאה: לא נמצא אלמנט תוכן מודאל");
return;
}
modalContent.innerHTML = '<div class="loader"></div>';
// קריאה לAPI לקבלת נתוני משחק מפורטים
debug(`שולח בקשה ל-API/game/${gameId}`);
fetch(`${API_BASE_URL}/game/${gameId}`)
.then(response => {
debug(`קיבלתי תגובה עבור משחק ${gameId}: ${response.status}`);
if (!response.ok) {
throw new Error(`שגיאה בקבלת פרטי משחק: ${response.status}`);
}
return response.json();
})
.then(data => {
debug(`התקבלו נתונים עבור משחק ${gameId}`);
if (data && data.results && data.results.length > 0) {
renderGameDetails(data.results[0]);
} else {
modalContent.innerHTML = `
<span class="close">&times;</span>
<h2>אין נתונים למשחק זה</h2>
<p>לא ניתן לטעון את פרטי המשחק ברגע זה. נסה שוב מאוחר יותר.</p>
`;
// הגדרת אירוע סגירת מודאל
const closeButton = modalContent.querySelector('.close');
if (closeButton) {
closeButton.addEventListener('click', function() {
modalElement.style.display = 'none';
});
}
}
})
.catch(error => {
debug(`שגיאה בטעינת פרטי משחק ${gameId}: ${error.message}`);
modalContent.innerHTML = `
<span class="close">&times;</span>
<h2>שגיאה בטעינת נתוני המשחק</h2>
<p>אירעה שגיאה בעת טעינת פרטי המשחק: ${error.message}</p>
`;
// הגדרת אירוע סגירת מודאל
const closeButton = modalContent.querySelector('.close');
if (closeButton) {
closeButton.addEventListener('click', function() {
modalElement.style.display = 'none';
});
}
});
// בנוסף, טעינת היסטוריית ליינים
debug(`שולח בקשה ל-API/game/${gameId}/lines_history`);
fetch(`${API_BASE_URL}/game/${gameId}/lines_history`)
.then(response => {
debug(`קיבלתי תגובה להיסטוריית ליינים עבור משחק ${gameId}: ${response.status}`);
if (!response.ok) {
throw new Error(`שגיאה בקבלת היסטוריית ליינים: ${response.status}`);
}
return response.json();
})
.then(history => {
debug(`התקבלה היסטוריית ליינים עבור משחק ${gameId}: ${history.length} רשומות`);
if (history && history.length > 0) {
renderLinesHistory(history);
}
})
.catch(error => {
debug(`שגיאה בטעינת היסטוריית ליינים למשחק ${gameId}: ${error.message}`);
});
} catch (error) {
console.error(`שגיאה בהצגת פרטי משחק ${gameId}:`, error);
}
}

function renderGameDetails(game) {
try {
debug(`מרנדר פרטי משחק ${game.id}`);
const modalContent = document.querySelector('.modal-content');
if (!modalContent) {
debug("שגיאה: לא נמצא אלמנט תוכן מודאל");
return;
}
// בניית HTML של פרטי המשחק
let gameDetails = `
<span class="close">&times;</span>
<h2>${game.league?.name || ''}: ${game.home?.name || 'בית'} נגד ${game.away?.name || 'חוץ'}</h2>
<div class="game-info">
<div class="game-status">
<p>סטטוס: ${formatGameStatus(game.time_status)}</p>
<p>תאריך: ${formatDate(game.time)}</p>
<p>שעה: ${formatTime(game.time)}</p>
</div>
<div class="score-info">
<h3>תוצאה</h3>
<p>${game.home?.name || 'בית'}: ${getHomeScore(game)}</p>
<p>${game.away?.name || 'חוץ'}: ${getAwayScore(game)}</p>
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
<td class="${getDirectionClass(game.spread_direction || 'neutral')}">${formatDiff(game.live_spread_diff)}</td>
</tr>
<tr>
<td>טוטאל</td>
<td>${formatTotal(game.opening_total)}</td>
<td>${formatTotal(game.start_total)}</td>
<td>${formatTotal(game.live_total)}</td>
<td class="${getDirectionClass(game.total_direction || 'neutral')}">${formatDiff(game.live_total_diff)}</td>
</tr>
</tbody>
</table>
</div>
<div class="opportunity-info ${game.opportunity_type || 'neutral'}">
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
const closeButton = modalContent.querySelector('.close');
if (closeButton) {
closeButton.addEventListener('click', function() {
const modal = document.getElementById('game-details-modal');
if (modal) modal.style.display = 'none';
});
}
} catch (error) {
console.error('שגיאה ברינדור פרטי משחק:', error);
}
}

function renderLinesHistory(history) {
try {
if (!history || history.length === 0) {
debug("אין היסטוריית ליינים להצגה");
return;
}
debug(`מרנדר היסטוריית ליינים, ${history.length} רשומות`);
// יצירת נתונים מעובדים לגרף
const chartData = history.map(line => ({
timestamp: new Date(line.timestamp),
spread: line.spread,
total: line.total
}));
// יצירת טבלת היסטוריה
const historyContainer = document.getElementById('lines-history-chart');
if (!historyContainer) {
debug("שגיאה: לא נמצא אלמנט להיסטוריית ליינים");
return;
}
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
} catch (error) {
console.error('שגיאה ברינדור היסטוריית ליינים:', error);
}
}

function refreshData() {
try {
debug("מרענן נתונים...");
loadStats();
loadGames();
} catch (error) {
console.error('שגיאה ברענון נתונים:', error);
}
}

functionfunction showLoader(show) {
try {
const loader = document.getElementById('loader');
if (!loader) {
debug("אזהרה: לא נמצא אלמנט loader");
return;
}
if (show) {
loader.classList.remove('hidden');
} else {
loader.classList.add('hidden');
}
} catch (error) {
console.error('שגיאה בהצגת/הסתרת לואדר:', error);
}
}

// פונקציות עזר לפורמט
function formatGameTime(game) {
try {
if (!game) return '-';
const timeStatus = game.time_status;
if (timeStatus === '1') {
// משחק חי
const timer = game.timer || {};
const quarter = timer.q || '';
const time = timer.tm || '';
if (quarter && time) {
return `רבע ${quarter}<br><small>${time}</small>`;
} else if (game.extra && game.extra.current_quarter) {
// מקרה שהמידע נמצא בשדה extra
return `רבע ${game.extra.current_quarter}<br><small>${game.extra.remaining_time || ''}</small>`;
} else {
// אם אין מידע מדויק, נציג לפחות שזה משחק חי
return `משחק חי<br><small>${formatTimeSince(game.time)}</small>`;
}
} else if (timeStatus === '0') {
// משחק עתידי - נציג את השעה המתוכננת
if (!game.time) return 'עתידי';
const gameDate = new Date(game.time * 1000);
const now = new Date();
// אם המשחק היום, נציג רק שעה
if (isSameDay(gameDate, now)) {
return `היום<br><small>${formatTime(game.time)}</small>`;
} else {
// אחרת נציג תאריך ושעה
return `${formatShortDate(game.time)}<br><small>${formatTime(game.time)}</small>`;
}
} else if (timeStatus === '2') {
// משחק שהסתיים
return `הסתיים<br><small>${formatTimeSince(game.time)}</small>`;
}
return '-';
} catch (error) {
console.error('שגיאה בפורמט זמן משחק:', error);
return '-';
}
}

// פונקציות עזר נוספות
function isSameDay(date1, date2) {
try {
return date1.getDate() === date2.getDate() &&
date1.getMonth() === date2.getMonth() &&
date1.getFullYear() === date2.getFullYear();
} catch (error) {
console.error('שגיאה בבדיקת אותו יום:', error);
return false;
}
}

function formatShortDate(timestamp) {
try {
if (!timestamp) return '-';
const date = new Date(timestamp * 1000);
return date.toLocaleDateString('he-IL', { day: '2-digit', month: '2-digit' });
} catch (error) {
console.error('שגיאה בפורמט תאריך מקוצר:', error);
return '-';
}
}

function formatTimeSince(timestamp) {
try {
if (!timestamp) return '';
const date = new Date(timestamp * 1000);
const now = new Date();
const diffMs = now - date;
const diffMins = Math.floor(diffMs / 60000);
if (diffMins < 60) {
return `לפני ${diffMins} דק'`;
} else {
const diffHours = Math.floor(diffMins / 60);
return `לפני ${diffHours} שעות`;
}
} catch (error) {
console.error('שגיאה בחישוב זמן שחלף:', error);
return '';
}
}

function formatGameScore(game) {
try {
if (!game || !game.ss) return '-';
const scores = game.ss.split('-');
if (scores.length !== 2) return game.ss;
const homeScore = scores[0];
const awayScore = scores[1];
return `${homeScore}<br><small>${awayScore}</small>`;
} catch (error) {
console.error('שגיאה בפורמט תוצאת משחק:', error);
return '-';
}
}

function getHomeScore(game) {
try {
if (!game || !game.ss) return '-';
const scores = game.ss.split('-');
return scores[0] || '-';
} catch (error) {
console.error('שגיאה בקבלת ניקוד ביתי:', error);
return '-';
}
}

function getAwayScore(game) {
try {
if (!game || !game.ss) return '-';
const scores = game.ss.split('-');
return scores.length > 1 ? scores[1] : '-';
} catch (error) {
console.error('שגיאה בקבלת ניקוד אורח:', error);
return '-';
}
}

function formatGameStatus(status) {
try {
switch (status) {
case '0': return 'עתידי';
case '1': return 'משחק חי';
case '2': return 'הסתיים';
case '3': return 'נדחה';
case '4': return 'בוטל';
default: return 'לא ידוע';
}
} catch (error) {
console.error('שגיאה בפורמט סטטוס משחק:', error);
return 'לא ידוע';
}
}

function formatDate(timestamp) {
try {
if (!timestamp) return '-';
const date = new Date(timestamp * 1000);
return date.toLocaleDateString('he-IL');
} catch (error) {
console.error('שגיאה בפורמט תאריך:', error);
return '-';
}
}

function formatTime(timestamp) {
try {
if (!timestamp) return '-';
const date = new Date(timestamp * 1000);
return date.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' });
} catch (error) {
console.error('שגיאה בפורמט שעה:', error);
return '-';
}
}

function formatSpread(spread) {
try {
if (spread === null || spread === undefined) return '-';
return spread > 0 ? `+${spread.toFixed(1)}` : spread.toFixed(1);
} catch (error) {
console.error('שגיאה בפורמט ספרד:', error);
return '-';
}
}

function formatTotal(total) {
try {
if (total === null || total === undefined) return '-';
return total.toFixed(1);
} catch (error) {
console.error('שגיאה בפורמט טוטאל:', error);
return '-';
}
}

function formatDiff(diff) {
try {
if (diff === null || diff === undefined) return '';
return diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
} catch (error) {
console.error('שגיאה בפורמט הפרש:', error);
return '';
}
}

function formatOpportunityType(type) {
try {
switch (type) {
case 'green': return 'ירוקה';
case 'red': return 'אדומה';
case 'blue': return 'כחולה';
default: return 'אין';
}
} catch (error) {
console.error('שגיאה בפורמט סוג הזדמנות:', error);
return 'אין';
}
}

function getDirectionClass(direction) {
try {
switch (direction) {
case 'up': return 'green';
case 'down': return 'red';
default: return '';
}
} catch (error) {
console.error('שגיאה בקבלת קלאס כיוון:', error);
return '';
}
}

// בדיקת API ישירות
async function testAPI() {
try {
debug("בודק API ישירות...");
// בדיקת בריאות
const healthResponse = await fetch(`${API_BASE_URL}/health`);
const healthData = await healthResponse.json();
debug("תוצאת בדיקת API/health:", healthData);
// בדיקת B365
const b365Response = await fetch(`${API_BASE_URL}/check-b365`);
const b365Data = await b365Response.json();
debug("תוצאת בדיקת API/check-b365:", b365Data);
return { health: healthData, b365: b365Data };
} catch (error) {
debug("שגיאה בבדיקת API ישירות:", error);
return { error: error.message };
}
}

// הוסף פונקציית בדיקה שניתן להפעיל מהקונסול
window.testAPI = testAPI;
window.forceReload = () => {
debug("מבצע טעינה מחדש בכוח...");
loadGames();
};
window.debugInfo = () => {
return {
currentGames: currentGames,
currentStats: currentStats,
lastUpdateTime: lastUpdateTime,
activeTab: activeTab
};
};
