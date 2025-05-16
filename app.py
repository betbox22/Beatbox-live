<td>-</td>
                    <td>${game.opening_spread || '-'}</td>
                    <td>-</td>
                    <td id="current-spread-${game.id}" class="${compareValues(game.current_spread, game.opening_spread)}">${game.current_spread || '-'}</td>
                    <td>${game.opening_total || '-'}</td>
                    <td>-</td>
                    <td id="current-total-${game.id}" class="${compareValues(game.current_total, game.opening_total)}">${game.current_total || '-'}</td>
                    <td>-</td>
                    <td>-</td>
                `;
            }
            
            return row;
        }
        
        // פונקציית עזר להשוואת ערכים
        function compareValues(current, original) {
            if (!current || !original) return "";
            
            const diff = parseFloat(current) - parseFloat(original);
            if (Math.abs(diff) >= 2) {
                return diff > 0 ? "cell-highlight-green" : "cell-highlight-red";
            }
            return "";
        }
        
        // משיכת משחקים מהשרת
        async function fetchGames() {
            try {
                // סינון
                const sportFilter = document.getElementById('sport-filter').value;
                const leagueFilter = document.getElementById('league-filter').value;
                const opportunitiesFilter = document.getElementById('opportunities-filter').value;
                const minLineMovement = document.getElementById('min-line-movement').value;
                const statusFilter = document.getElementById('status-filter').value;
                
                // בניית URL עם פרמטרים
                let url = '/api/games';
                const params = new URLSearchParams();
                
                if (sportFilter !== 'all') {
                    params.append('sport_type', sportFilter);
                }
                
                if (statusFilter !== 'all') {
                    params.append('status', statusFilter);
                }
                
                const response = await fetch(url + (params.toString() ? `?${params.toString()}` : ''));
                const games = await response.json();
                
                // משיכת סטטיסטיקות
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                // עדכון ממשק משתמש
                updateDashboard(stats);
                updateGamesTable(games, { 
                    leagueFilter, 
                    opportunitiesFilter, 
                    minLineMovement: parseFloat(minLineMovement),
                    statusFilter
                });
                updateLastRefreshTime();
            } catch (error) {
                console.error('Error fetching games:', error);
            }
        }
        
        // עדכון טבלת המשחקים
        function updateGamesTable(games, filters) {
            const tableBody = document.getElementById('games-table-body');
            tableBody.innerHTML = '';
            
            // סינון משחקים לפי הפילטרים
            const filteredGames = games.filter(game => {
                // סינון לפי ליגה
                if (filters.leagueFilter !== 'all' && !game.league.includes(filters.leagueFilter)) {
                    return false;
                }
                
                // סינון לפי סטטוס
                if (filters.statusFilter !== 'all' && game.status !== filters.statusFilter) {
                    return false;
                }
                
                // סינון לפי סוג הזדמנות
                if (filters.opportunitiesFilter !== 'all') {
                    if (filters.opportunitiesFilter === 'green' && game.opportunity_type !== 'green') {
                        return false;
                    } else if (filters.opportunitiesFilter === 'red' && game.opportunity_type !== 'red') {
                        return false;
                    } else if (filters.opportunitiesFilter === 'blue' && game.opportunity_type !== 'blue') {
                        return false;
                    }
                }
                
                // סינון לפי תנועת ליין מינימלית
                if (filters.minLineMovement > 0) {
                    // בדיקה אם יש תנועת ליין מספקת
                    let spreadDiff = 0;
                    let totalDiff = 0;
                    
                    if (game.status === 'live') {
                        spreadDiff = parseFloat(game.live_spread_diff || 0);
                        totalDiff = parseFloat(game.live_total_diff || 0);
                    } else {
                        const currentSpread = parseFloat(game.current_spread || 0);
                        const openingSpread = parseFloat(game.opening_spread || 0);
                        const currentTotal = parseFloat(game.current_total || 0);
                        const openingTotal = parseFloat(game.opening_total || 0);
                        
                        spreadDiff = Math.abs(currentSpread - openingSpread);
                        totalDiff = Math.abs(currentTotal - openingTotal);
                    }
                    
                    if (Math.abs(spreadDiff) < filters.minLineMovement && Math.abs(totalDiff) < filters.minLineMovement) {
                        return false;
                    }
                }
                
                return true;
            });
            
            // מיון - קודם משחקים חיים ואז עתידיים
            filteredGames.sort((a, b) => {
                // אם אחד חי והשני לא, החי קודם
                if (a.status === 'live' && b.status !== 'live') return -1;
                if (a.status !== 'live' && b.status === 'live') return 1;
                
                // אם שניהם באותו סטטוס, מיין לפי זמן התחלה
                if (a.time && b.time) {
                    return parseFloat(a.time) - parseFloat(b.time);
                }
                
                return 0;
            });
            
            // הוספת שורות לטבלה
            filteredGames.forEach(game => {
                tableBody.appendChild(createGameRow(game));
            });
        }
        
        // הצגת חלון פרטי משחק
        async function showGameDetails(gameId) {
            // משיכת פרטי משחק מהשרת
            try {
                const response = await fetch(`/api/games/${gameId}/details`);
                const gameDetails = await response.json();
                
                const modalTitle = document.getElementById('game-details-title');
                const modalBody = document.getElementById('game-details-body');
                
                modalTitle.textContent = `${gameDetails.homeTeam} - ${gameDetails.awayTeam}`;
                
                // יצירת תוכן המודאל
                let modalContent = '';
                
                // טבלת רבעים
                modalContent += `
                <div class="score-section">
                    <h3 class="section-title">תוצאה</h3>
                    <table class="quarters-table">
                        <thead>
                            <tr>
                                <th>קבוצה</th>
                                <th>Q1</th>
                                <th>Q2</th>
                                <th>Half</th>
                                <th>Q3</th>
                                <th>Q4</th>
                                <th>T</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="team-name"><span class="team-indicator home-indicator"></span>${gameDetails.homeTeam}</td>
                `;
                
                // הוספת נתוני רבעים לקבוצת בית
                if (gameDetails.quarters && gameDetails.quarters.length > 0) {
                    // הוספת נק' רבעונים
                    const homeQuarters = gameDetails.quarters.map(q => q.home || 0);
                    const homeHalf = (homeQuarters[0] || 0) + (homeQuarters[1] || 0);
                    
                    modalContent += `
                        <td>${homeQuarters[0] || 0}</td>
                        <td>${homeQuarters[1] || 0}</td>
                        <td>${homeHalf}</td>
                        <td>${homeQuarters[2] || 0}</td>
                        <td>${homeQuarters[3] || 0}</td>
                        <td class="team-score">${gameDetails.homeScore || 0}</td>
                    `;
                } else {
                    modalContent += `
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td class="team-score">${gameDetails.homeScore || 0}</td>
                    `;
                }
                
                modalContent += `
                            </tr>
                            <tr>
                                <td class="team-name"><span class="team-indicator away-indicator"></span>${gameDetails.awayTeam}</td>
                `;
                
                // הוספת נתוני רבעים לקבוצת חוץ
                if (gameDetails.quarters && gameDetails.quarters.length > 0) {
                    // הוספת נק' רבעונים
                    const awayQuarters = gameDetails.quarters.map(q => q.away || 0);
                    const awayHalf = (awayQuarters[0] || 0) + (awayQuarters[1] || 0);
                    
                    modalContent += `
                        <td>${awayQuarters[0] || 0}</td>
                        <td>${awayQuarters[1] || 0}</td>
                        <td>${awayHalf}</td>
                        <td>${awayQuarters[2] || 0}</td>
                        <td>${awayQuarters[3] || 0}</td>
                        <td class="team-score">${gameDetails.awayScore || 0}</td>
                    `;
                } else {
                    modalContent += `
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                        <td class="team-score">${gameDetails.awayScore || 0}</td>
                    `;
                }
                
                modalContent += `
                            </tr>
                        </tbody>
                    </table>
                </div>
                `;
                
                // סטטיסטיקות משחק
                modalContent += `
                <div class="stats-section">
                    <h3 class="section-title">סטטיסטיקה</h3>
                    <div class="stats-summary">
                        <div class="stats-item">
                            <div class="value">${gameDetails.totalFouls?.home || 0}</div>
                            <div class="label">עבירות</div>
                        </div>
                        <div class="stats-item">
                            <div class="value">${gameDetails.totalPoints2?.home || 0}</div>
                            <div class="label">2 pts</div>
                        </div>
                        <div class="stats-item">
                            <div class="value">${gameDetails.totalPoints3?.home || 0}</div>
                            <div class="label">3 pts</div>
                        </div>
                        <div class="stats-item">
                            <div class="value">${gameDetails.percentage2pt || 0}%</div>
                            <div class="label">2pt %</div>
                        </div>
                        <div class="stats-item">
                            <div class="value">${gameDetails.percentage3pt || 0}%</div>
                            <div class="label">3pt %</div>
                        </div>
                        <div class="stats-item">
                            <div class="value">${gameDetails.totalFouls?.away || 0}</div>
                            <div class="label">עבירות</div>
                        </div>
                    </div>
                    
                    <div class="fouls-indicator">
                        ${generateFoulsIndicator(gameDetails.totalFouls?.home || 0)}
                    </div>
                </div>
                `;
                
                // מידע על השוק וליינים
                modalContent += `
                <div class="lines-section">
                    <h3 class="section-title">התפתחות ליינים</h3>
                    <table class="details-table">
                        <thead>
                            <tr>
                                <th>זמן</th>
                                <th>ליין</th>
                                <th>O/U</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                // הוספת היסטוריית תנועת ליינים
                if (gameDetails.movementHistory && gameDetails.movementHistory.length > 0) {
                    gameDetails.movementHistory.forEach(movement => {
                        modalContent += `
                            <tr>
                                <td>${movement.time}</td>
                                <td>${movement.spread}</td>
                                <td>${movement.total}</td>
                            </tr>
                        `;
                    });
                } else {
                    modalContent += `
                        <tr>
                            <td colspan="3">אין נתונים זמינים</td>
                        </tr>
                    `;
                }
                
                modalContent += `
                        </tbody>
                    </table>
                </div>
                `;
                
                // מידע על קצב זריקות
                modalContent += `
                <div class="stats-section">
                    <h3 class="section-title">קצב משחק</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">קצב זריקות לדקה</div>
                            <div class="stat-value ${gameDetails.shotsPerMinute >= 4 ? 'value-blue' : 'value-red'}">${gameDetails.shotsPerMinute || 0}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">סטטוס קצב</div>
                            <div class="stat-value ${gameDetails.shotsPerMinute >= 4 ? 'value-blue' : 'value-red'}">
                                ${gameDetails.shotsPerMinute >= 4 ? 'מהיר' : 'איטי'}
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // הזדמנות
                if (gameDetails.opportunity_type && gameDetails.opportunity_type !== 'neutral') {
                    const opportunityClass = 
                        gameDetails.opportunity_type === 'green' ? 'opportunity-green' : 
                        gameDetails.opportunity_type === 'red' ? 'opportunity-red' : 
                        gameDetails.opportunity_type === 'blue' ? 'opportunity-blue' : '';
                    
                    const opportunityText = 
                        gameDetails.opportunity_type === 'green' ? 'הזדמנות חיובית' : 
                        gameDetails.opportunity_type === 'red' ? 'הזדמנות שלילית' : 
                        gameDetails.opportunity_type === 'blue' ? 'הזדמנות מיוחדת' : '';
                    
                    modalContent += `
                    <div class="opportunity-section">
                        <h3 class="section-title">ניתוח הזדמנות</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-label">סוג הזדמנות</div>
                                <div class="stat-value ${opportunityClass}">${opportunityText}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">סיבה</div>
                                <div class="stat-value">${gameDetails.opportunity_reason || 'שילוב גורמים'}</div>
                            </div>
                        </div>
                    </div>
                    `;
                }
                
                modalBody.innerHTML = modalContent;
                
                // הצגת המודאל
                const modal = document.getElementById('game-details-modal');
                modal.style.display = 'flex';
                
            } catch (error) {
                console.error('Error fetching game details:', error);
            }
        }
        
        // סגירת חלון פרטי משחק
        function closeGameDetails() {
            const modal = document.getElementById('game-details-modal');
            modal.style.display = 'none';
        }
        
        // יצירת אינדיקטור עבירות
        function generateFoulsIndicator(fouls) {
            let indicators = '';
            for (let i = 0; i < 5; i++) {
                indicators += `<div class="indicator ${i < fouls ? 'active' : ''}"></div>`;
            }
            return indicators;
        }
        
        // מאזין אירועים לשינוי פילטרים
        document.getElementById('sport-filter').addEventListener('change', fetchGames);
        document.getElementById('league-filter').addEventListener('change', fetchGames);
        document.getElementById('opportunities-filter').addEventListener('change', fetchGames);
        document.getElementById('status-filter').addEventListener('change', fetchGames);
        document.getElementById('min-line-movement').addEventListener('input', fetchGames);
        
        // מאזין אירועים לחץ על הלשונית
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                fetchGames();
            });
        });
        
        // מאזין אירועים לתאריכים
        document.querySelectorAll('.date-tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.date-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                fetchGames();
            });
        });
        
        // מאזין אירועים לסגירת מודאל בלחיצה על הרקע
        document.getElementById('game-details-modal').addEventListener('click', function(event) {
            if (event.target === this) {
                closeGameDetails();
            }
        });
        
        // אינטרוול לעדכון זמן נוכחי
        setInterval(updateCurrentTime, 1000);
        
        // אינטרוול לרענון נתונים
        let refreshInterval;
        
        function startAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
            refreshInterval = setInterval(fetchGames, 30000); // כל 30 שניות
        }
        
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }
        
        // מאזין אירועים לריענון אוטומטי
        document.getElementById('auto-refresh').addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
        
        // אתחול האתר
        function init() {
            updateCurrentTime();
            fetchGames();
            startAutoRefresh();
        }
        
        // הפעלת האתר בטעינת הדף
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
