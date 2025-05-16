import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // מצב (state) של היישום
  const [games, setGames] = useState([]);
  const [stats, setStats] = useState({
    opportunity_percentage: 0,
    red_opportunities: 0,
    green_opportunities: 0,
    total_live: 0
  });
  const [filters, setFilters] = useState({
    sportFilter: 'כדורסל',
    leagueFilter: 'all',
    opportunitiesFilter: 'all',
    minLineMovement: 0
  });
  const [currentTime, setCurrentTime] = useState('');
  const [lastUpdateTime, setLastUpdateTime] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedGame, setSelectedGame] = useState(null);

  // עדכון השעה הנוכחית
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('he-IL'));
    };
    
    updateTime();
    const interval = setInterval(updateTime, 1000);
    
    return () => clearInterval(interval);
  }, []);

  // פורמט תאריך/זמן לעדכון אחרון
  const formatDateTime = (date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
  };

  // משיכת משחקים מהשרת
  const fetchGames = async () => {
    try {
      // בניית URL עם פרמטרים
      let url = '/api/games';
      const params = new URLSearchParams();
      
      if (filters.sportFilter !== 'all') {
        params.append('sport_type', filters.sportFilter);
      }
      
      const response = await fetch(url + (params.toString() ? `?${params.toString()}` : ''));
      const gamesData = await response.json();
      
      // משיכת סטטיסטיקות
      const statsResponse = await fetch('/api/stats');
      const statsData = await statsResponse.json();
      
      setGames(gamesData);
      setStats(statsData);
      setLastUpdateTime(formatDateTime(new Date()));
    } catch (error) {
      console.error('Error fetching games:', error);
    }
  };

  // הגדרת רענון אוטומטי
  useEffect(() => {
    let interval;
    
    if (autoRefresh) {
      fetchGames(); // טעינה ראשונית
      interval = setInterval(fetchGames, 30000); // רענון כל 30 שניות
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, filters]);

  // סינון משחקים לפי הפילטרים
  const getFilteredGames = () => {
    return games.filter(game => {
      // סינון לפי ליגה
      if (filters.leagueFilter !== 'all' && !game.league.includes(filters.leagueFilter)) {
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
        const spreadDiff = parseFloat(game.live_spread_diff || 0);
        const totalDiff = parseFloat(game.live_total_diff || 0);
        
        if (Math.abs(spreadDiff) < filters.minLineMovement && Math.abs(totalDiff) < filters.minLineMovement) {
          return false;
        }
      }
      
      return true;
    });
  };

  // טעינת פרטי משחק
  const fetchGameDetails = async (gameId) => {
    try {
      const response = await fetch(`/api/game/${gameId}`);
      const gameDetails = await response.json();
      setSelectedGame(gameDetails);
    } catch (error) {
      console.error('Error fetching game details:', error);
    }
  };

  // יצירת מחוון קצב זריקות
  const renderShotRate = (shotRate, shotRateColor) => {
    if (!shotRate) return "-";
    
    let indicator = null;
    if (shotRateColor === "red") {
      indicator = <span className="shot-indicator shot-red"></span>;
    } else if (shotRateColor === "blue") {
      indicator = <span className="shot-indicator shot-blue"></span>;
    }
    
    return (
      <>
        {indicator}
        {shotRate}
      </>
    );
  };

  // טיפול בשינוי פילטרים
  const handleFilterChange = (e) => {
    const { id, value } = e.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [id === 'sport-filter' ? 'sportFilter' : 
       id === 'league-filter' ? 'leagueFilter' :
       id === 'opportunities-filter' ? 'opportunitiesFilter' :
       id === 'min-line-movement' ? 'minLineMovement' : id]: value
    }));
  };

  // הצגת פרטי משחק במודאל
  const GameDetailsModal = () => {
    if (!selectedGame) return null;

    return (
      <div className="game-details-modal" onClick={() => setSelectedGame(null)}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <span className="close-modal" onClick={() => setSelectedGame(null)}>&times;</span>
          <h2>{selectedGame.home} vs {selectedGame.away}</h2>
          <div className="game-stats">
            <div className="score-section">
              <h3>תוצאה: {selectedGame.score || '-'}</h3>
              <p>
                זמן: {selectedGame.timer?.q 
                  ? `רבע ${selectedGame.timer.q} (${selectedGame.timer.tm}:${selectedGame.timer.ts})` 
                  : '-'}
              </p>
            </div>
            
            <div className="lines-section">
              <h3>מידע על ליינים:</h3>
              <table className="details-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>ספרד</th>
                    <th>אובר/אנדר</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>פתיחה</td>
                    <td>{selectedGame.opening?.spread || '-'}</td>
                    <td>{selectedGame.opening?.total || '-'}</td>
                  </tr>
                  <tr>
                    <td>התחלה</td>
                    <td>{selectedGame.starting?.spread || '-'}</td>
                    <td>{selectedGame.starting?.total || '-'}</td>
                  </tr>
                  <tr>
                    <td>לייב</td>
                    <td>{selectedGame.live?.spread || '-'}</td>
                    <td>{selectedGame.live?.total || '-'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div className="opportunity-section">
              <h3>ניתוח הזדמנות:</h3>
              <p className={`opportunity-${selectedGame.opportunity.type}`}>
                {selectedGame.opportunity.reason || 'אין הזדמנות'}
              </p>
              {selectedGame.opportunity.shot_rate && (
                <p>קצב זריקות: {selectedGame.opportunity.shot_rate.toFixed(1)}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // הרכיב הראשי
  return (
    <div className="App">
      <header>
        <h1 className="title">BETBOX - ניתוח משחקי כדורסל חיים</h1>
        <div id="current-time">{currentTime}</div>
      </header>
      
      <div className="container">
        <div className="dashboard">
          <div className="stat-card">
            <div className="stat-value percentage">{stats.opportunity_percentage}%</div>
            <div className="stat-label">אחוז הזדמנויות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.red_opportunities}</div>
            <div className="stat-label">הזדמנויות כושלות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value value-green">{stats.green_opportunities}</div>
            <div className="stat-label">הזדמנויות ירוקות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_live}</div>
            <div className="stat-label">משחקים חיים</div>
          </div>
        </div>
        
        <div className="filter-controls">
          <div className="filter-group">
            <span className="filter-label">תנועת ליין (מינימום):</span>
            <input 
              type="number" 
              id="min-line-movement" 
              value={filters.minLineMovement} 
              min="0" 
              step="0.5"
              onChange={handleFilterChange}
            />
          </div>
          
          <div className="filter-group">
            <span className="filter-label">הזדמנויות:</span>
            <select 
              id="opportunities-filter" 
              value={filters.opportunitiesFilter} 
              onChange={handleFilterChange}
            >
              <option value="all">הכל</option>
              <option value="green">ירוקות</option>
              <option value="red">אדומות</option>
              <option value="blue">כחולות</option>
            </select>
          </div>
          
          <div className="filter-group">
            <span className="filter-label">ליגה:</span>
            <select 
              id="league-filter" 
              value={filters.leagueFilter} 
              onChange={handleFilterChange}
            >
              <option value="all">הכל</option>
              <option value="NBA">NBA</option>
              <option value="Euroleague">יורוליג</option>
              <option value="Spain">ספרד</option>
              <option value="Israel">ישראל</option>
            </select>
          </div>
          
          <div className="filter-group">
            <span className="filter-label">ספורט:</span>
            <select 
              id="sport-filter" 
              value={filters.sportFilter} 
              onChange={handleFilterChange}
            >
              <option value="all">הכל</option>
              <option value="כדורסל">כדורסל</option>
              <option value="כדורגל">כדורגל</option>
            </select>
          </div>
        </div>
        
        <table className="games-table">
          <thead>
            <tr>
              <th>ספורט</th>
              <th>ליגה</th>
              <th>משחק</th>
              <th>זמן</th>
              <th>תוצאה</th>
              <th>ליין פתיחה</th>
              <th>ליין התחלה</th>
              <th>ליין נוכחי</th>
              <th>O/U פתיחה</th>
              <th>O/U התחלה</th>
              <th>O/U נוכחי</th>
              <th>קצב זריקות</th>
              <th>הזדמנות</th>
            </tr>
          </thead>
          <tbody>
            {getFilteredGames().length > 0 ? (
              getFilteredGames().map(game => (
                <tr 
                  key={game.id} 
                  id={`game-row-${game.id}`}
                  className={`clickable-row ${game.opportunity_type === "green" ? 'row-opportunity-green' : 
                    game.opportunity_type === "red" ? 'row-opportunity-red' : 
                    game.opportunity_type === "blue" ? 'row-opportunity-blue' : ''}`}
                  onClick={() => fetchGameDetails(game.id)}
                >
                  <td>{game.sportType}</td>
                  <td className="value-gold">{game.league}</td>
                  <td>
                    <div className="team-name">
                      {game.matchup}
                      {game.status === 'live' && <span className="live-indicator">חי</span>}
                    </div>
                  </td>
                  <td>{game.timer || game.time || ''}</td>
                  <td>{game.score || '-'}</td>
                  <td>{game.opening_spread || '-'}</td>
                  <td 
                    id={`start-spread-${game.id}`} 
                    className={game.opening_vs_start === 'green' ? 'cell-highlight-green' : 
                      game.opening_vs_start === 'red' ? 'cell-highlight-red' : ''}
                  >
                    {game.start_spread || '-'}
                  </td>
                  <td 
                    id={`live-spread-${game.id}`} 
                    className={game.spread_flag === 'green' ? 'cell-highlight-green' : ''}
                  >
                    {game.live_spread || '-'}
                  </td>
                  <td>{game.opening_total || '-'}</td>
                  <td 
                    id={`start-total-${game.id}`} 
                    className={game.opening_vs_start === 'green' ? 'cell-highlight-green' : 
                      game.opening_vs_start === 'red' ? 'cell-highlight-red' : ''}
                  >
                    {game.start_total || '-'}
                  </td>
                  <td 
                    id={`live-total-${game.id}`} 
                    className={game.ou_flag === 'green' ? 'cell-highlight-green' : ''}
                  >
                    {game.live_total || '-'}
                  </td>
                  <td 
                    id={`shot-rate-${game.id}`} 
                    className={game.shot_rate_color === 'red' ? 'value-red' : 
                      game.shot_rate_color === 'blue' ? 'value-blue' : ''}
                  >
                    {renderShotRate(game.shot_rate, game.shot_rate_color)}
                  </td>
                  <td 
                    className={game.opportunity_type === 'green' ? 'value-green' : 
                      game.opportunity_type === 'red' ? 'value-red' : 
                      game.opportunity_type === 'blue' ? 'value-blue' : ''}
                  >
                    {game.opportunity_type !== 'neutral' ? 'כן' : '-'}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="13" style={{ textAlign: 'center' }}>
                  אין משחקים התואמים את הפילטרים
                </td>
              </tr>
            )}
          </tbody>
        </table>
        
        <div className="refresh-info">
          <div className="last-update">עדכון אחרון: {lastUpdateTime}</div>
          <div className="auto-refresh">
            <input 
              type="checkbox" 
              id="auto-refresh" 
              checked={autoRefresh} 
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <label htmlFor="auto-refresh">רענון אוטומטי: כל 30 שניות</label>
          </div>
        </div>
      </div>
      
      <footer>
        &copy; {new Date().getFullYear()} BETBOX - כל הזכויות שמורות
      </footer>
      
      {/* המודאל של פרטי המשחק */}
      <GameDetailsModal />
    </div>
  );
}

export default App;
