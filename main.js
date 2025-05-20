// Global state
let allGames = [];
let activeTab = 'live';
let leagueFilter = 'all';
let opportunityFilter = 'all';
let minLineMovement = 0;
let refreshTimer = null;

// DOM elements
const currentTimeElement = document.getElementById('current-time');
const lastUpdateTimeElement = document.getElementById('last-update-time');
const loaderElement = document.getElementById('loader');
const gamesTableBody = document.getElementById('games-table-body');
const statsElements = {
    opportunityPercentage: document.getElementById('opportunity-percentage'),
    redOpportunities: document.getElementById('red-opportunities'),
    greenOpportunities: document.getElementById('green-opportunities'),
    blueOpportunities: document.getElementById('blue-opportunities'),
    totalLive: document.getElementById('total-live'),
    totalUpcoming: document.getElementById('total-upcoming')
};
const modal = document.getElementById('game-details-modal');
const modalContent = document.getElementById('game-details-content');
const modalClose = document.querySelector('.close');

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize filters
    document.getElementById('league-filter').addEventListener('change', updateFilters);
    document.getElementById('opportunity-filter').addEventListener('change', updateFilters);
    document.getElementById('min-line-movement').addEventListener('change', updateFilters);
    
    // Initialize tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });
    
    // Initialize refresh button
    document.getElementById('refresh-button').addEventListener('click', () => {
        refreshData(true);
    });
    
    // Initialize modal close button
    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Start auto refresh and clock
    updateClock();
    setInterval(updateClock, 1000);
    refreshData(true);
    startAutoRefresh();
});

// Update current time display
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('he-IL');
    currentTimeElement.textContent = timeStr;
}

// Start auto refresh timer
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
        refreshData(false);
    }, 30000); // 30 seconds refresh
}

// Update filters and refresh display
function updateFilters() {
    leagueFilter = document.getElementById('league-filter').value;
    opportunityFilter = document.getElementById('opportunity-filter').value;
    minLineMovement = parseFloat(document.getElementById('min-line-movement').value) || 0;
    
    displayFilteredGames();
}

// Switch between tabs
function switchTab(tab) {
    // Update active tab
    activeTab = tab;
    
    // Update UI
    document.querySelectorAll('.tab').forEach(tabElement => {
        if (tabElement.dataset.tab === tab) {
            tabElement.classList.add('active');
        } else {
            tabElement.classList.remove('active');
        }
    });
    
    // Update displayed games
    displayFilteredGames();
}

// Refresh data from API
function refreshData(showLoader = true) {
    if (showLoader) {
        loaderElement.classList.remove('hidden');
    }
    
    // Fetch games data
    fetch('/api/games')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.results) {
                allGames = data.results;
                displayFilteredGames();
                updateLastRefreshTime();
            } else {
                console.error('Invalid data format:', data);
                gamesTableBody.innerHTML = '<tr><td colspan="7">אין משחקים זמינים כרגע</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error fetching games:', error);
            gamesTableBody.innerHTML = `<tr><td colspan="7">שגיאה בטעינת נתונים: ${error.message}</td></tr>`;
        })
        .finally(() => {
            loaderElement.classList.add('hidden');
        });
    
    // Fetch stats data
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStats(data);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Display filtered games
function displayFilteredGames() {
    // Filter games based on current filters and tab
    const filteredGames = allGames.filter(game => {
        // Filter by tab
        if (activeTab === 'live' && game.time_status !== '1') {
            return false;
        }
        if (activeTab === 'upcoming' && game.time_status !== '0') {
            return false;
        }
        
        // Filter by league
        if (leagueFilter !== 'all') {
            const leagueName = game.league?.name || '';
            if (!leagueName.includes(leagueFilter)) {
                return false;
            }
        }
        
        // Filter by opportunity
        if (opportunityFilter !== 'all' && game.opportunity_type !== opportunityFilter) {
            return false;
        }
        
        // Filter by line movement
        const spreadDiff = Math.abs(game.live_spread_diff || 0);
        const totalDiff = Math.abs(game.live_total_diff || 0);
        const maxDiff = Math.max(spreadDiff, totalDiff);
        
        if (maxDiff < minLineMovement) {
            return false;
        }
        
        return true;
    });
    
    // Update table
    if (filteredGames.length === 0) {
        gamesTableBody.innerHTML = '<tr><td colspan="7">אין משחקים תואמים לסינון שנבחר</td></tr>';
        return;
    }
    
    const rows = filteredGames.map(game => {
        // Extract team names
        const homeTeam = game.home?.name || 'בית';
        const awayTeam = game.away?.name || 'חוץ';
        
        // Get score
        const score = game.ss || '-';
        
        // Get time or quarter info
        let timeInfo = '';
        if (game.time_status === '1') {
            // Live game - show quarter and time
            const quarter = game.timer?.q || '';
            const timeRemaining = game.timer?.tm || '';
            
            if (quarter && timeRemaining) {
                timeInfo = `רבע ${quarter} - ${timeRemaining}`;
            } else {
                timeInfo = 'חי';
            }
        } else if (game.time_status === '0') {
            // Upcoming game - show start time
            const startTime = new Date(game.time * 1000);
            timeInfo = startTime.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' });
        } else {
            timeInfo = 'סיום';
        }
        
        // Get line info with movement indicators
        let spreadInfo = '';
        if (game.live_spread !== null) {
            const spread = game.live_spread;
            const direction = game.spread_direction;
            
            spreadInfo = `${spread > 0 ? '+' : ''}${spread}`;
            
            if (direction === 'up') {
                spreadInfo += ' ↑';
            } else if (direction === 'down') {
                spreadInfo += ' ↓';
            }
            
            if (game.spread_flag === 'green') {
                spreadInfo = `<span class="green">${spreadInfo}</span>`;
            }
        } else {
            spreadInfo = '-';
        }
        
        let totalInfo = '';
        if (game.live_total !== null) {
            const total = game.live_total;
            const direction = game.total_direction;
            
            totalInfo = `${total}`;
            
            if (direction === 'up') {
                totalInfo += ' ↑';
            } else if (direction === 'down') {
                totalInfo += ' ↓';
            }
            
            if (game.ou_flag === 'green') {
                totalInfo = `<span class="green">${totalInfo}</span>`;
            }
        } else {
            totalInfo = '-';
        }
        
        // Opportunity info
        let opportunityInfo = '';
        const opportunityType = game.opportunity_type || 'neutral';
        
        if (opportunityType === 'green') {
            opportunityInfo = '<span class="green">✓</span>';
        } else if (opportunityType === 'red') {
            opportunityInfo = '<span class="red">✗</span>';
        } else if (opportunityType === 'blue') {
            opportunityInfo = '<span class="blue">!</span>';
        } else {
            opportunityInfo = '-';
        }
        
        // Row class for highlighting
        let rowClass = 'clickable';
        if (opportunityType === 'green') {
            rowClass += ' highlight-green';
        } else if (opportunityType === 'red') {
            rowClass += ' highlight-red';
        }
        
        return `
            <tr class="${rowClass}" data-game-id="${game.id}">
                <td>${game.league?.name || '-'}</td>
                <td>${homeTeam} - ${awayTeam}</td>
                <td>${timeInfo}</td>
                <td>${score}</td>
                <td>${spreadInfo}</td>
                <td>${totalInfo}</td>
                <td>${opportunityInfo}</td>
            </tr>
        `;
    }).join('');
    
    gamesTableBody.innerHTML = rows;
    
    // Add click event to rows
    document.querySelectorAll('tr[data-game-id]').forEach(row => {
        row.addEventListener('click', () => {
            showGameDetails(row.dataset.gameId);
        });
    });
}

// Show game details in modal
function showGameDetails(gameId) {
    // Show loader in modal
    modalContent.innerHTML = '<div class="loader"></div>';
    modal.style.display = 'block';
    
    // Fetch game details and lines history
    const detailsPromise = fetch(`/api/game/${gameId}`).then(res => res.json());
    const historyPromise = fetch(`/api/game/${gameId}/lines_history`).then(res => res.json());
    
    Promise.all([detailsPromise, historyPromise])
        .then(([details, history]) => {
            if (!details.results || details.results.length === 0) {
                throw new Error('No game details available');
            }
            
            const game = details.results[0];
            displayGameDetails(game, history);
        })
        .catch(error => {
            console.error('Error fetching game details:', error);
            modalContent.innerHTML = `<div class="error">שגיאה בטעינת פרטי המשחק: ${error.message}</div>`;
        });
}

// Display game details in modal
function displayGameDetails(game, history) {
    // Extract team names
    const homeTeam = game.home?.name || 'בית';
    const awayTeam = game.away?.name || 'חוץ';
    const leagueName = game.league?.name || '';
    
    // Current score
    const score = game.ss || '-';
    
    // Game status
    let statusText = '';
    if (game.time_status === '1') {
        // Live game
        const quarter = game.timer?.q || '';
        const timeRemaining = game.timer?.tm || '';
        
        if (quarter && timeRemaining) {
            statusText = `משחק חי - רבע ${quarter} - ${timeRemaining}`;
        } else {
            statusText = 'משחק חי';
        }
    } else if (game.time_status === '0') {
        // Upcoming game
        const startTime = new Date(game.time * 1000);
        statusText = `משחק עתידי - ${startTime.toLocaleString('he-IL')}`;
    } else {
        statusText = 'משחק הסתיים';
    }
    
    // Line movement info
    const spreadDiff = game.live_spread_diff || 0;
    const totalDiff = game.live_total_diff || 0;
    
    // Create line history table
    let historyTable = '';
    if (history && history.length > 0) {
        const historyRows = history.map((entry, index) => {
            const timestamp = new Date(entry.timestamp).toLocaleString('he-IL');
            const spread = entry.spread !== null ? entry.spread : '-';
            const total = entry.total !== null ? entry.total : '-';
            
            // Compare with previous entry to show changes
            let spreadChange = '';
            let totalChange = '';
            
            if (index > 0) {
                const prevSpread = history[index - 1].spread;
                const prevTotal = history[index - 1].total;
                
                if (prevSpread !== null && entry.spread !== null) {
                    const diff = entry.spread - prevSpread;
                    if (diff > 0) {
                        spreadChange = `<span class="green">↑ ${diff.toFixed(1)}</span>`;
                    } else if (diff < 0) {
                        spreadChange = `<span class="red">↓ ${diff.toFixed(1)}</span>`;
                    }
                }
                
                if (prevTotal !== null && entry.total !== null) {
                    const diff = entry.total - prevTotal;
                    if (diff > 0) {
                        totalChange = `<span class="green">↑ ${diff.toFixed(1)}</span>`;
                    } else if (diff < 0) {
                        totalChange = `<span class="red">↓ ${diff.toFixed(1)}</span>`;
                    }
                }
            }
            
            return `
                <tr>
                    <td>${timestamp}</td>
                    <td>${spread} ${spreadChange}</td>
                    <td>${total} ${totalChange}</td>
                    <td>${entry.quarter || '-'}</td>
                </tr>
            `;
        }).join('');
        
        historyTable = `
            <h3>היסטוריית קווים</h3>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>זמן</th>
                        <th>ספרד</th>
                        <th>טוטאל</th>
                        <th>רבע</th>
                    </tr>
                </thead>
                <tbody>
                    ${historyRows}
                </tbody>
            </table>
        `;
    } else {
        historyTable = '<p>אין היסטוריית קווים זמינה</p>';
    }
    
    // Opportunity details
    let opportunityDetails = '';
    if (game.opportunity_type && game.opportunity_type !== 'neutral') {
        const colorClass = game.opportunity_type;
        opportunityDetails = `
            <div class="opportunity-details ${colorClass}">
                <h3>הזדמנות זוהתה</h3>
                <p>${game.opportunity_reason || 'פרטי הזדמנות לא זמינים'}</p>
            </div>
        `;
    }
    
    // Build modal content
    modalContent.innerHTML = `
        <div class="game-header">
            <h2>${homeTeam} - ${awayTeam}</h2>
            <p class="league">${leagueName}</p>
            <p class="status">${statusText}</p>
            <p class="score">תוצאה: ${score}</p>
        </div>
        
        <div class="line-summary">
            <div class="line-item">
                <div class="line-title">ספרד נוכחי</div>
                <div class="line-value">${game.live_spread !== null ? game.live_spread : '-'
