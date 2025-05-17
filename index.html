ב
  // טיפול בשינוי טאב
  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
    fetchData(); // טען מחדש נתונים בשינוי טאב
  };

  // פונקציית הצגת שינוי ליין
  const renderLineChange = (diff, direction) => {
    if (!diff) return "-";
    
    const absDiff = Math.abs(parseFloat(diff));
    const dirClass = direction === 'up' ? 'line-change-up' : 
                    direction === 'down' ? 'line-change-down' : '';
    const dirIcon = direction === 'up' ? '↑' : 
                   direction === 'down' ? '↓' : '';
    
    return (
      <span className={dirClass}>
        {absDiff.toFixed(1)} {dirIcon}
      </span>
    );
  };

  // פונקציית הצגת קצב זריקות
  const renderShotRate = (shotRate, color) => {
    if (!shotRate) return "-";
    
    const colorClass = color === "red" ? "shot-red" : 
                      color === "blue" ? "shot-blue" : 
                      color === "green" ? "shot-green" : 
                      color === "orange" ? "shot-orange" : "";
    
    return (
      <div>
        {colorClass && <span className={`shot-indicator ${colorClass}`}></span>}
        {typeof shotRate === 'number' ? shotRate.toFixed(1) : shotRate}
      </div>
    );
  };

  // פונקציית רינדור שורת משחק
  const renderGameRow = (game) => {
    // תאים משותפים לכל סוגי המשחקים
    const commonCells = (
      <>
        <td>{game.sportType || 'כדורסל'}</td>
        <td className="value-gold">{game.league}</td>
        <td>
          <div className="team-name">
            <span className="team-logo">{game.home?.substr(0, 1) || 'H'}</span>
            {game.home} vs {game.away}
          </div>
        </td>
      </>
    );

    // משחקים בזמן אמת
    if (activeTab === 'live') {
      return (
        <tr key={game.id} className={`clickable-row ${game.opportunity_type !== 'neutral' ? 'pulse' : ''}`} onClick={() => loadGameDetails(game.id)}>
          {commonCells}
          <td>
            <span className="status-badge status-live">
              {game.timer || 'חי'}
            </span>
          </td>
          <td className="value-blue">{game.score || '-'}</td>
          <td>{game.opening_spread || '-'}</td>
          <td className={game.opening_vs_start === 'green' ? 'cell-highlight-green' : game.opening_vs_start === 'red' ? 'cell-highlight-red' : ''}>
            {game.start_spread || '-'}
          </td>
          <td className={game.spread_flag === 'green' ? 'cell-highlight-green' : game.spread_flag === 'red' ? 'cell-highlight-red' : ''}>
            {game.live_spread || '-'}
          </td>
          <td>
            {renderLineChange(game.live_spread_diff, game.spread_direction)}
          </td>
          <td>{game.opening_total || '-'}</td>
          <td className={game.opening_vs_start === 'green' ? 'cell-highlight-green' : game.opening_vs_start === 'red' ? 'cell-highlight-red' : ''}>
            {game.start_total || '-'}
          </td>
          <td className={game.ou_flag === 'green' ? 'cell-highlight-green' : game.ou_flag === 'red' ? 'cell-highlight-red' : ''}>
            {game.live_total || '-'}
          </td>
          <td>
            {renderLineChange(game.live_total_diff, game.total_direction)}
          </td>
          <td className={`value-${game.shot_rate_color || ''}`}>
            {renderShotRate(game.shot_rate, game.shot_rate_color)}
          </td>
          <td className={`value-${game.opportunity_type}`}>
            {game.opportunity_type !== 'neutral' ? <i className="fas fa-check-circle opportunity-icon"></i> : '-'}
          </td>
        </tr>
      );
    }
    
    // משחקים עתידיים
    if (activeTab === 'upcoming') {
      return (
        <tr key={game.id} className="clickable-row" onClick={() => loadGameDetails(game.id)}>
          {commonCells}
          <td>{game.date || '-'}</td>
          <td>{game.time || '-'}</td>
          <td>{game.opening_spread || '-'}</td>
          <td className={game.spread_flag === 'green' ? 'cell-highlight-green' : game.spread_flag === 'red' ? 'cell-highlight-red' : ''}>
            {game.current_spread || '-'}
          </td>
          <td>
            {renderLineChange(game.spread_diff, game.spread_direction)}
          </td>
          <td>{game.opening_total || '-'}</td>
          <td className={game.ou_flag === 'green' ? 'cell-highlight-green' : game.ou_flag === 'red' ? 'cell-highlight-red' : ''}>
            {game.current_total || '-'}
          </td>
          <td>
            {renderLineChange(game.total_diff, game.total_direction)}
          </td>
          <td>
            <span className="status-badge status-upcoming">
              {game.time_until || 'יתחיל בקרוב'}
            </span>
          </td>
        </tr>
      );
    }
    
    // משחקים שהסתיימו
    if (activeTab === 'finished') {
      return (
        <tr key={game.id} className="clickable-row" onClick={() => loadGameDetails(game.id)}>
          {commonCells}
          <td className="value-blue">{game.final_score || game.score || '-'}</td>
          <td>{game.opening_spread || '-'}</td>
          <td className={game.spread_result === 'success' ? 'cell-highlight-green' : game.spread_result === 'fail' ? 'cell-highlight-red' : ''}>
            {game.final_spread || game.live_spread || '-'}
          </td>
          <td>{game.opening_total || '-'}</td>
          <td className={game.total_result === 'success' ? 'cell-highlight-green' : game.total_result === 'fail' ? 'cell-highlight-red' : ''}>
            {game.final_total || game.live_total || '-'}
          </td>
          <td className={`value-${game.result_type || 'neutral'}`}>
            {game.result_description || '-'}
          </td>
        </tr>
      );
    }
    
    return null;
  };

  // כותרות טבלה בהתאם לטאב הפעיל
  const renderTableHeaders = () => {
    // כותרות משותפות
    const commonHeaders = (
      <>
        <th>ספורט</th>
        <th>ליגה</th>
        <th>משחק</th>
      </>
    );
    
    // כותרות למשחקים בזמן אמת
    if (activeTab === 'live') {
      return (
        <tr>
          {commonHeaders}
          <th>זמן</th>
          <th>תוצאה</th>
          <th>ליין פתיחה</th>
          <th>ליין התחלה</th>
          <th>ליין נוכחי</th>
          <th>שינוי</th>
          <th>O/U פתיחה</th>
          <th>O/U התחלה</th>
          <th>O/U נוכחי</th>
          <th>שינוי</th>
          <th>קצב זריקות</th>
          <th>הזדמנות</th>
        </tr>
      );
    }
    
    // כותרות למשחקים עתידיים
    if (activeTab === 'upcoming') {
      return (
        <tr>
          {commonHeaders}
          <th>תאריך</th>
          <th>שעה</th>
          <th>ליין פתיחה</th>
          <th>ליין נוכחי</th>
          <th>שינוי</th>
          <th>O/U פתיחה</th>
          <th>O/U נוכחי</th>
          <th>שינוי</th>
          <th>מצב</th>
        </tr>
      );
    }
    
    // כותרות למשחקים שהסתיימו
    if (activeTab === 'finished') {
      return (
        <tr>
          {commonHeaders}
          <th>תוצאה סופית</th>
          <th>ליין פתיחה</th>
          <th>ליין סופי</th>
          <th>O/U פתיחה</th>
          <th>O/U סופי</th>
          <th>סיכום תוצאה</th>
        </tr>
      );
    }
    
    return null;
  };
  
  // גרף תנועת ליין
  const renderLineChart = (data) => {
    if (!data || data.length === 0) {
      return (
        <div className="empty-chart">
          <p>אין נתונים להצגה</p>
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" stroke="#888" />
          <YAxis stroke="#888" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#242424', 
              border: '1px solid #444',
              color: '#e1e1e1'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="spread" 
            stroke="#4caf50" 
            activeDot={{ r: 8 }}
            strokeWidth={2}
          />
          <Line 
            type="monotone" 
            dataKey="total" 
            stroke="#2196f3" 
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  // רינדור מודאל עם פרטי משחק
  const renderGameDetailsModal = () => {
    if (!isModalOpen || !selectedGame) {
      return null;
    }

    // נתוני היסטוריית ליין לדוגמה (יש להחליף בנתונים אמיתיים)
    const lineHistoryData = [
      { time: "התחלה", spread: parseFloat(selectedGame.opening_spread || 0), total: parseFloat(selectedGame.opening_total || 0) },
      { time: "רבע 1", spread: parseFloat(selectedGame.opening_spread || 0) + 2, total: parseFloat(selectedGame.opening_total || 0) + 5 },
      { time: "רבע 2", spread: parseFloat(selectedGame.opening_spread || 0) + 1, total: parseFloat(selectedGame.opening_total || 0) + 8 },
      { time: "רבע 3", spread: parseFloat(selectedGame.live_spread || selectedGame.current_spread || 0), total: parseFloat(selectedGame.live_total || selectedGame.current_total || 0) },
    ];

    // תוכן המודאל לפי סטטוס המשחק
    let modalContent;
    
    if (selectedGame.status === 'live') {
      modalContent = (
        <>
          <div className="game-header">
            <h2>{selectedGame.home} vs {selectedGame.away}</h2>
            <span className="status-badge status-live">משחק חי</span>
          </div>
          
          <div className="teams-score">
            <div className="team-score-box">
              <div>{selectedGame.home}</div>
              <div className="team-score">{selectedGame.home_score || '0'}</div>
            </div>
            
            <div className="vs-divider">VS</div>
            
            <div className="team-score-box">
              <div>{selectedGame.away}</div>
              <div className="team-score">{selectedGame.away_score || '0'}</div>
            </div>
          </div>
          
          <div className="game-period">
            {selectedGame.timer || 'זמן לא זמין'}
          </div>
          
          <div className="stats-grid">
            <div className="stats-card">
              <h4>מידע על ליינים:</h4>
              <ul className="stats-list">
                <li>
                  <span>ספרד פתיחה:</span>
                  <span>{selectedGame.opening_spread || '-'}</span>
                </li>
                <li>
                  <span>ספרד התחלה:</span>
                  <span className={selectedGame.opening_vs_start === 'green' ? 'value-green' : selectedGame.opening_vs_start === 'red' ? 'value-red' : ''}>
                    {selectedGame.start_spread || '-'}
                  </span>
                </li>
                <li>
                  <span>ספרד נוכחי:</span>
                  <span className={selectedGame.spread_flag === 'green' ? 'value-green' : selectedGame.spread_flag === 'red' ? 'value-red' : ''}>
                    {selectedGame.live_spread || '-'}
                  </span>
                </li>
                <li>
                  <span>שינוי בספרד:</span>
                  <span className={selectedGame.spread_direction === 'up' ? 'value-green' : selectedGame.spread_direction === 'down' ? 'value-red' : ''}>
                    {selectedGame.live_spread_diff ? 
                      `${Math.abs(parseFloat(selectedGame.live_spread_diff)).toFixed(1)} ${selectedGame.spread_direction === 'up' ? '↑' : '↓'}` 
                      : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>מידע על טוטאל:</h4>
              <ul className="stats-list">
                <li>
                  <span>טוטאל פתיחה:</span>
                  <span>{selectedGame.opening_total || '-'}</span>
                </li>
                <li>
                  <span>טוטאל התחלה:</span>
                  <span className={selectedGame.opening_vs_start === 'green' ? 'value-green' : selectedGame.opening_vs_start === 'red' ? 'value-red' : ''}>
                    {selectedGame.start_total || '-'}
                  </span>
                </li>
                <li>
                  <span>טוטאל נוכחי:</span>
                  <span className={selectedGame.ou_flag === 'green' ? 'value-green' : selectedGame.ou_flag === 'red' ? 'value-red' : ''}>
                    {selectedGame.live_total || '-'}
                  </span>
                </li>
                <li>
                  <span>שינוי בטוטאל:</span>
                  <span className={selectedGame.total_direction === 'up' ? 'value-green' : selectedGame.total_direction === 'down' ? 'value-red' : ''}>
                    {selectedGame.live_total_diff ? 
                      `${Math.abs(parseFloat(selectedGame.live_total_diff)).toFixed(1)} ${selectedGame.total_direction === 'up' ? '↑' : '↓'}` 
                      : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>ניתוח הזדמנות:</h4>
              <ul className="stats-list">
                <li>
                  <span>סוג הזדמנות:</span>
                  <span className={`value-${selectedGame.opportunity?.type || 'neutral'}`}>
                    {selectedGame.opportunity?.type === 'green' ? 'ירוקה' : 
                     selectedGame.opportunity?.type === 'red' ? 'אדומה' : 
                     selectedGame.opportunity?.type === 'blue' ? 'כחולה' : 
                     'אין הזדמנות'}
                  </span>
                </li>
                <li>
                  <span>סיבה:</span>
                  <span>{selectedGame.opportunity?.reason || '-'}</span>
                </li>
                <li>
                  <span>קצב זריקות:</span>
                  <span className={`value-${selectedGame.shot_rate_color || 'neutral'}`}>
                    {selectedGame.opportunity?.shot_rate ? 
                      selectedGame.opportunity.shot_rate.toFixed(1) : '-'}
                  </span>
                </li>
                <li>
                  <span>המלצה:</span>
                  <span className={`value-${selectedGame.opportunity?.type || 'neutral'}`}>
                    {selectedGame.opportunity?.recommendation || '-'}
                  </span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="line-history">
            <h3>היסטוריית ליינים:</h3>
            <div className="history-chart">
              {renderLineChart(lineHistoryData)}
            </div>
          </div>
        </>
      );
    } else if (selectedGame.status === 'upcoming') {
      modalContent = (
        <>
          <div className="game-header">
            <h2>{selectedGame.home} vs {selectedGame.away}</h2>
            <span className="status-badge status-upcoming">משחק עתידי</span>
          </div>
          
          <div className="game-period">
            יתחיל ב-{selectedGame.date || '-'} בשעה {selectedGame.time || '-'}
          </div>
          
          <div className="stats-grid">
            <div className="stats-card">
              <h4>מידע על ליינים:</h4>
              <ul className="stats-list">
                <li>
                  <span>ספרד פתיחה:</span>
                  <span>{selectedGame.opening_spread || '-'}</span>
                </li>
                <li>
                  <span>ספרד נוכחי:</span>
                  <span className={selectedGame.spread_flag === 'green' ? 'value-green' : selectedGame.spread_flag === 'red' ? 'value-red' : ''}>
                    {selectedGame.current_spread || '-'}
                  </span>
                </li>
                <li>
                  <span>שינוי בספרד:</span>
                  <span className={selectedGame.spread_direction === 'up' ? 'value-green' : selectedGame.spread_direction === 'down' ? 'value-red' : ''}>
                    {selectedGame.spread_diff ? 
                      `${Math.abs(parseFloat(selectedGame.spread_diff)).toFixed(1)} ${selectedGame.spread_direction === 'up' ? '↑' : '↓'}` 
                      : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>מידע על טוטאל:</h4>
              <ul className="stats-list">
                <li>
                  <span>טוטאל פתיחה:</span>
                  <span>{selectedGame.opening_total || '-'}</span>
                </li>
                <li>
                  <span>טוטאל נוכחי:</span>
                  <span className={selectedGame.ou_flag === 'green' ? 'value-green' : selectedGame.ou_flag === 'red' ? 'value-red' : ''}>
                    {selectedGame.current_total || '-'}
                  </span>
                </li>
                <li>
                  <span>שינוי בטוטאל:</span>
                  <span className={selectedGame.total_direction === 'up' ? 'value-green' : selectedGame.total_direction === 'down' ? 'value-red' : ''}>
                    {selectedGame.total_diff ? 
                      `${Math.abs(parseFloat(selectedGame.total_diff)).toFixed(1)} ${selectedGame.total_direction === 'up' ? '↑' : '↓'}` 
                      : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>מידע נוסף:</h4>
              <ul className="stats-list">
                <li>
                  <span>ליגה:</span>
                  <span className="value-gold">{selectedGame.league || '-'}</span>
                </li>
                <li>
                  <span>תחזית:</span>
                  <span>{selectedGame.prediction || 'אין מידע'}</span>
                </li>
                <li>
                  <span>זמן עד למשחק:</span>
                  <span className="value-blue">{selectedGame.time_until || 'מחשב...'}</span>
                </li>
              </ul>
            </div>
          </div>
        </>
      );
    } else if (selectedGame.status === 'finished') {
      modalContent = (
        <>
          <div className="game-header">
            <h2>{selectedGame.home} vs {selectedGame.away}</h2>
            <span className="status-badge status-finished">הסתיים</span>
          </div>
          
          <div className="teams-score">
            <div className="team-score-box">
              <div>{selectedGame.home}</div>
              <div className="team-score">{selectedGame.home_score || '0'}</div>
            </div>
            
            <div className="vs-divider">
              <i className="fas fa-trophy" style={{ color: 'var(--gold-color)' }}></i>
            </div>
            
            <div className="team-score-box">
              <div>{selectedGame.away}</div>
              <div className="team-score">{selectedGame.away_score || '0'}</div>
            </div>
          </div>
          
          <div className="game-period">
            תוצאה סופית: {selectedGame.final_score || selectedGame.score || '-'}
          </div>
          
          <div className="stats-grid">
            <div className="stats-card">
              <h4>מידע על ליינים:</h4>
              <ul className="stats-list">
                <li>
                  <span>ספרד פתיחה:</span>
                  <span>{selectedGame.opening_spread || '-'}</span>
                </li>
                <li>
                  <span>ספרד סופי:</span>
                  <span className={selectedGame.spread_result === 'success' ? 'value-green' : selectedGame.spread_result === 'fail' ? 'value-red' : ''}>
                    {selectedGame.final_spread || selectedGame.live_spread || '-'}
                  </span>
                </li>
                <li>
                  <span>תוצאת ספרד:</span>
                  <span className={selectedGame.spread_result === 'success' ? 'value-green' : selectedGame.spread_result === 'fail' ? 'value-red' : ''}>
                    {selectedGame.spread_result === 'success' ? 'הצלחה' : 
                     selectedGame.spread_result === 'fail' ? 'כישלון' : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>מידע על טוטאל:</h4>
              <ul className="stats-list">
                <li>
                  <span>טוטאל פתיחה:</span>
                  <span>{selectedGame.opening_total || '-'}</span>
                </li>
                <li>
                  <span>טוטאל סופי:</span>
                  <span className={selectedGame.total_result === 'success' ? 'value-green' : selectedGame.total_result === 'fail' ? 'value-red' : ''}>
                    {selectedGame.final_total || selectedGame.live_total || '-'}
                  </span>
                </li>
                <li>
                  <span>תוצאת טוטאל:</span>
                  <span className={selectedGame.total_result === 'success' ? 'value-green' : selectedGame.total_result === 'fail' ? 'value-red' : ''}>
                    {selectedGame.total_result === 'success' ? 'הצלחה' : 
                     selectedGame.total_result === 'fail' ? 'כישלון' : '-'}
                  </span>
                </li>
              </ul>
            </div>
            
            <div className="stats-card">
              <h4>סיכום התוצאה:</h4>
              <div style={{ padding: '10px 0' }}>
                <p className={`value-${selectedGame.result_type || 'neutral'}`}>
                  {selectedGame.result_description || 'אין מידע על תוצאה'}
                </p>
                <div className="tags-container">
                  {selectedGame.tags ? 
                    selectedGame.tags.map((tag, index) => (
                      <span key={index} className={`tag tag-${tag.type || 'blue'}`}>{tag.text}</span>
                    )) : ''}
                </div>
              </div>
            </div>
          </div>
        </>
      );
    }

    return (
      <div className="game-details-modal">
        <div className="modal-content">
          <span className="close-modal" onClick={() => setIsModalOpen(false)}>&times;</span>
          {modalContent}
        </div>
      </div>
    );
  };

  // רינדור של האפליקציה
  return (
    <div className="betbox-app">
      <header>
        <h1 className="title">BETBOX - ניתוח משחקי כדורסל חיים</h1>
        <div className="time-badge">{currentTime}</div>
      </header>
      
      <div className="container">
        {/* Dashboard */}
        <div className="dashboard">
          <div className="stat-card">
            <div className="stat-value percentage">{stats.opportunity_percentage || 0}%</div>
            <div className="stat-label">אחוז הזדמנויות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value value-red">{stats.red_opportunities || 0}</div>
            <div className="stat-label">הזדמנויות כושלות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value value-green">{stats.green_opportunities || 0}</div>
            <div className="stat-label">הזדמנויות ירוקות</div>
          </div>
          <div className="stat-card">
            <div className="stat-value value-blue">{stats.total_live || 0}</div>
            <div className="stat-label">משחקים חיים</div>
          </div>
          <div className="stat-card">
            <div className="stat-value value-gold">{stats.total_upcoming || 0}</div>
            <div className="stat-label">משחקים עתידיים</div>
          </div>
        </div>
        
        {/* פילטרים */}
        <div className="filter-controls">
          <div className="filter-group">
            <span className="filter-label">ספורט:</span>
            <select 
              value={filters.sport}
              onChange={(e) => handleFilterChange('sport', e.target.value)}
            >
              <option value="all">הכל</option>
              <option value="כדורסל">כדורסל</option>
              <option value="כדורגל">כדורגל</option>
            </select>
          </div>
          
          <div className="filter-group">
            <span className="filter-label">ליגה:</span>
            <select 
              value={filters.league}
              onChange={(e) => handleFilterChange('league', e.target.value)}
            >
              <option value="all">הכל</option>
              <option value="NBA">NBA</option>
              <option value="Euroleague">יורוליג</option>
              <option value="Spain">ספרד</option>
              <option value="Israel">ישראל</option>
            </select>
          </div>
          
          <div className="filter-group">
            <span className="filter-label">הזדמנויות:</span>
            <select 
              value={filters.opportunities}
              onChange={(e) => handleFilterChange('opportunities', e.target.value)}
            >
              <option value="all">הכל</option>
              <option value="green">ירוקות</option>
              <option value="red">אדומות</option>
              <option value="blue">כחולות</option>
            </select>
          </div>
          
          <div className="filter-group">
            <span className="filter-label">תנועת ליין (מינימום):</span>
            <input 
              type="number" 
              value={filters.line
  // פונקציית טעינת נתונים מה-API
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // טעינת משחקים בזמן אמת מ-API
      const apiData = await ApiService.fetchLiveGames();
      
      // מיפוי הנתונים למבנה שהאפליקציה מצפה לו
      const mappedGames = ApiService.mapGamesData(apiData);
      
      // סינון לפי סטטוס אם צריך
      const statusFilteredGames = activeTab === 'all' ? 
        mappedGames : 
        mappedGames.filter(game => game.status === activeTab);
      
      setGames(statusFilteredGames);
      
      // חישוב סטטיסטיקות
      const calculatedStats = ApiService.calculateStats(mappedGames);
      setStats(calculatedStats);
      
      // עדכון זמן עדכון אחרון
      setLastUpdate(formatDateTime(new Date()));
      
      // החלת סינון נוסף
      filterGames(statusFilteredGames);
    } catch (error) {
      console.error('שגיאה בטעינת נתונים:', error);
      setError(`שגיאה בטעינת נתונים: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  // פונקציית סינון משחקים
  const filterGames = useCallback((gamesData = games) => {
    const filtered = gamesData.filter(game => {
      // סינון לפי ליגה
      if (filters.league !== 'all' && game.league !== filters.league) {
        return false;
      }

      // סינון לפי סוג הזדמנות
      if (filters.opportunities !== 'all') {
        if (filters.opportunities === 'green' && game.opportunity_type !== 'green') {
          return false;
        } else if (filters.opportunities === 'red' && game.opportunity_type !== 'red') {
          return false;
        } else if (filters.opportunities === 'blue' && game.opportunity_type !== 'blue') {
          return false;
        }
      }

      // סינון לפי תנועת ליין
      if (filters.lineMovement > 0) {
        const spreadDiff = Math.abs(parseFloat(game.live_spread_diff || game.spread_diff || 0));
        const totalDiff = Math.abs(parseFloat(game.live_total_diff || game.total_diff || 0));

        if (spreadDiff < filters.lineMovement && totalDiff < filters.lineMovement) {
          return false;
        }
      }

      return true;
    });

    setFilteredGames(filtered);
  }, [games, filters]);

  // טעינת פרטי משחק
  const loadGameDetails = async (gameId) => {
    try {
      setLoading(true);
      
      // חיפוש המשחק במערך המשחקים הקיים
      const existingGame = games.find(game => game.id === gameId);
      
      if (existingGame) {
        // אם המשחק כבר טעון, השתמש בנתונים הקיימים
        setSelectedGame(existingGame);
      } else {
        // אחרת, טען נתונים מה-API
        const gameData = await ApiService.fetchGameStats(gameId);
        const mappedGames = ApiService.mapGamesData(gameData);
        
        if (mappedGames && mappedGames.length > 0) {
          setSelectedGame(mappedGames[0]);
        } else {
          throw new Error('לא נמצאו נתונים עבור המשחק');
        }
      }
      
      setIsModalOpen(true);
    } catch (error) {
      console.error('שגיאה בטעינת פרטי משחק:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // פורמט תאריך ושעה
  const formatDateTime = (date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
  };

  // אתחול ורענון אוטומטי
  useEffect(() => {
    fetchData();
    
    // הגדרת עדכון שעון
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('he-IL'));
    }, 1000);
    
    // הגדרת רענון אוטומטי
    let dataRefreshInterval;
    if (autoRefresh) {
      dataRefreshInterval = setInterval(() => {
        fetchData();
      }, refreshRate * 1000);
    }
    
    return () => {
      clearInterval(clockInterval);
      if (dataRefreshInterval) {
        clearInterval(dataRefreshInterval);
      }
    };
  }, [fetchData, autoRefresh, refreshRate]);

  // החלת סינון כשהמשחקים או הפילטרים משתנים
  useEffect(() => {
    filterGames();
  }, [games, filterGames]);

  // טיפול בשינוי פילטרים
  const handleFilterChange = (name, value) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value
    }));
  };

  // טיפול בשינוי טאimport React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// API מקורות
const API_CONFIG = {
  B365_API_URL: "http://api.b365api.com/v3/events/inplay",
  B365_TOKEN: "219761-iALwqep7Hy1aCl",
  SPORT_ID: 18 // כדורסל
};

// מחלקה לניהול API
class ApiService {
  // פונקציה להביא משחקים בזמן אמת
  static async fetchLiveGames() {
    try {
      const response = await fetch(
        `${API_CONFIG.B365_API_URL}?sport_id=${API_CONFIG.SPORT_ID}&token=${API_CONFIG.B365_TOKEN}`
      );
      
      if (!response.ok) {
        throw new Error(`API שגיאה: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("שגיאה בהבאת משחקים:", error);
      throw error;
    }
  }
  
  // פונקציה להביא סטטיסטיקות של משחק ספציפי
  static async fetchGameStats(gameId) {
    try {
      const response = await fetch(
        `${API_CONFIG.B365_API_URL}?event_id=${gameId}&token=${API_CONFIG.B365_TOKEN}`
      );
      
      if (!response.ok) {
        throw new Error(`API שגיאה: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`שגיאה בהבאת סטטיסטיקות למשחק ${gameId}:`, error);
      throw error;
    }
  }
  
  // מיפוי נתוני API למבנה שהאפליקציה צריכה
  static mapGamesData(apiData) {
    if (!apiData || !apiData.results) {
      return [];
    }
    
    return apiData.results.map(game => {
      // חישוב נתוני ליין ושינויים
      const spreadInfo = this.calculateSpreadInfo(game);
      const totalInfo = this.calculateTotalInfo(game);
      const shotRateInfo = this.calculateShotRate(game);
      const opportunityInfo = this.analyzeOpportunity(spreadInfo, totalInfo, shotRateInfo);
      
      return {
        id: game.id,
        sportType: "כדורסל",
        league: this.mapLeagueName(game.league?.name),
        home: game.home?.name,
        away: game.away?.name,
        status: this.mapGameStatus(game.time_status),
        timer: this.formatGameTime(game),
        score: game.ss || "-",
        home_score: parseInt(game.ss?.split('-')[0]) || 0,
        away_score: parseInt(game.ss?.split('-')[1]) || 0,
        date: game.time ? new Date(game.time * 1000).toLocaleDateString('he-IL') : "-",
        time: game.time ? new Date(game.time * 1000).toLocaleTimeString('he-IL', {hour: '2-digit', minute:'2-digit'}) : "-",
        time_until: game.time ? this.calculateTimeUntil(game.time) : "בקרוב",
        
        // נתוני ליינים
        opening_spread: spreadInfo.opening,
        start_spread: spreadInfo.start,
        live_spread: spreadInfo.current,
        current_spread: spreadInfo.current,
        live_spread_diff: spreadInfo.diff,
        spread_diff: spreadInfo.diff,
        spread_direction: spreadInfo.direction,
        spread_flag: spreadInfo.flag,
        opening_vs_start: spreadInfo.openingVsStart,
        
        // נתוני טוטאל
        opening_total: totalInfo.opening,
        start_total: totalInfo.start,
        live_total: totalInfo.current,
        current_total: totalInfo.current,
        live_total_diff: totalInfo.diff,
        total_diff: totalInfo.diff,
        total_direction: totalInfo.direction,
        ou_flag: totalInfo.flag,
        
        // נתוני קצב וניתוח
        shot_rate: shotRateInfo.rate,
        shot_rate_color: shotRateInfo.color,
        opportunity_type: opportunityInfo.type,
        opportunity: opportunityInfo
      };
    });
  }
  
  // מיפוי שם הליגה לפורמט מובן
  static mapLeagueName(leagueName) {
    if (!leagueName) return "לא ידוע";
    
    const leagueMap = {
      "NBA": "NBA",
      "Euroleague": "יורוליג",
      "Spain": "ספרד",
      "Israel": "ישראל",
      "Liga ACB": "ספרד",
      "Israel Basketball Premier League": "ישראל",
      "Champions League": "ליגת האלופות",
      "NCAA": "NCAA"
    };
    
    // בדיקה אם יש התאמה מדויקת
    if (leagueMap[leagueName]) {
      return leagueMap[leagueName];
    }
    
    // בדיקה אם יש התאמה חלקית
    for (const [key, value] of Object.entries(leagueMap)) {
      if (leagueName.includes(key)) {
        return value;
      }
    }
    
    return leagueName;
  }
  
  // מיפוי סטטוס המשחק
  static mapGameStatus(statusCode) {
    switch(statusCode) {
      case "1": return "live";
      case "0": return "upcoming";
      case "3": return "finished";
      default: return "upcoming";
    }
  }
  
  // פורמט זמן המשחק
  static formatGameTime(game) {
    if (!game) return "-";
    
    if (game.time_status === "1") {
      // משחק חי
      const timer = game.timer || {};
      const quarter = timer.q || "";
      const minutes = timer.tm || "00";
      const seconds = timer.ts || "00";
      
      if (quarter) {
        return `רבע ${quarter} (${minutes}:${seconds})`;
      } else {
        return "חי";
      }
    } else if (game.time_status === "0") {
      // משחק עתידי
      return this.formatTime(game.time);
    } else {
      // משחק שהסתיים
      return "הסתיים";
    }
  }
  
  // פורמט זמן
  static formatTime(timestamp) {
    if (!timestamp) return "-";
    
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('he-IL', {hour: '2-digit', minute:'2-digit'});
  }
  
  // חישוב זמן עד למשחק
  static calculateTimeUntil(timestamp) {
    if (!timestamp) return "בקרוב";
    
    const now = Math.floor(Date.now() / 1000);
    const diff = timestamp - now;
    
    if (diff <= 0) return "מתחיל עכשיו";
    
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    
    if (hours > 0) {
      return `עוד ${hours} שעות ו-${minutes} דקות`;
    } else {
      return `עוד ${minutes} דקות`;
    }
  }
  
  // חישוב נתוני הספרד (ליין)
  static calculateSpreadInfo(game) {
    // נתוני ספרד - במקרה אמיתי יש להשתמש בנתונים מה-API
    // כאן משתמשים בנתונים לדוגמה או מחושבים
    const openingSpread = this.extractOddsFromGame(game, 'opening', 'spread');
    const startSpread = this.extractOddsFromGame(game, 'start', 'spread');
    const liveSpread = this.extractOddsFromGame(game, 'live', 'spread');
    
    // אם אין נתוני ליין זמינים, נחזיר ערכי ברירת מחדל
    if (!openingSpread && !startSpread && !liveSpread) {
      return {
        opening: "-",
        start: "-",
        current: "-",
        diff: "0",
        direction: "neutral",
        flag: "neutral",
        openingVsStart: "neutral"
      };
    }

    // חישוב הפרש וכיוון
    let diff = "0";
    let direction = "neutral";
    
    if (openingSpread && liveSpread) {
      const openingValue = parseFloat(openingSpread);
      const liveValue = parseFloat(liveSpread);
      
      if (!isNaN(openingValue) && !isNaN(liveValue)) {
        diff = (liveValue - openingValue).toFixed(1);
        direction = diff > 0 ? "up" : diff < 0 ? "down" : "neutral";
      }
    }
    
    // קביעת דגלים וצבעים
    let flag = "neutral";
    if (Math.abs(parseFloat(diff)) >= 2) {
      flag = direction === "up" ? "green" : "red";
    }
    
    // השוואה בין פתיחה להתחלה
    let openingVsStart = "neutral";
    if (openingSpread && startSpread) {
      const openingValue = parseFloat(openingSpread);
      const startValue = parseFloat(startSpread);
      
      if (!isNaN(openingValue) && !isNaN(startValue)) {
        const startDiff = startValue - openingValue;
        openingVsStart = Math.abs(startDiff) >= 1 ? 
                         (startDiff > 0 ? "green" : "red") : 
                         "neutral";
      }
    }
    
    return {
      opening: openingSpread || "-",
      start: startSpread || "-",
      current: liveSpread || "-",
      diff,
      direction,
      flag,
      openingVsStart
    };
  }
  
  // חישוב נתוני הטוטאל
  static calculateTotalInfo(game) {
    // נתוני טוטאל - במקרה אמיתי יש להשתמש בנתונים מה-API
    const openingTotal = this.extractOddsFromGame(game, 'opening', 'total');
    const startTotal = this.extractOddsFromGame(game, 'start', 'total');
    const liveTotal = this.extractOddsFromGame(game, 'live', 'total');
    
    // אם אין נתוני טוטאל זמינים, נחזיר ערכי ברירת מחדל
    if (!openingTotal && !startTotal && !liveTotal) {
      return {
        opening: "-",
        start: "-",
        current: "-",
        diff: "0",
        direction: "neutral",
        flag: "neutral"
      };
    }

    // חישוב הפרש וכיוון
    let diff = "0";
    let direction = "neutral";
    
    if (openingTotal && liveTotal) {
      const openingValue = parseFloat(openingTotal);
      const liveValue = parseFloat(liveTotal);
      
      if (!isNaN(openingValue) && !isNaN(liveValue)) {
        diff = (liveValue - openingValue).toFixed(1);
        direction = diff > 0 ? "up" : diff < 0 ? "down" : "neutral";
      }
    }
    
    // קביעת דגלים וצבעים
    let flag = "neutral";
    if (Math.abs(parseFloat(diff)) >= 3) {
      flag = direction === "up" ? "green" : "red";
    }
    
    return {
      opening: openingTotal || "-",
      start: startTotal || "-",
      current: liveTotal || "-",
      diff,
      direction,
      flag
    };
  }
  
  // חילוץ נתוני יחס הימור מהמשחק
  static extractOddsFromGame(game, timePoint, oddsType) {
    // במקרה אמיתי, צריך לחלץ את נתוני היחס מהמשחק לפי המבנה האמיתי של ה-API
    // כאן, אנחנו משתמשים בלוגיקה לדוגמה
    
    if (!game || !game.odds) return null;
    
    // אם יש אובייקט odds במשחק, נסה לחלץ את הנתונים המבוקשים
    const odds = game.odds[timePoint]?.[oddsType];
    
    if (odds) {
      return odds.toString();
    }
    
    // אם אין נתונים ספציפיים, ננסה לחשב ערכים הגיוניים
    if (timePoint === 'live' && oddsType === 'spread') {
      // לדוגמה: ליין ספרד בזמן אמת יכול להיות מחושב מהתוצאה הנוכחית
      const homeScore = parseInt(game.ss?.split('-')[0]) || 0;
      const awayScore = parseInt(game.ss?.split('-')[1]) || 0;
      const scoreDiff = homeScore - awayScore;
      
      // ליין משוער לפי הפרש התוצאה - פשוט לדוגמה
      return (scoreDiff - 1.5).toFixed(1);
    }
    
    if (timePoint === 'live' && oddsType === 'total') {
      // לדוגמה: טוטאל בזמן אמת יכול להיות מחושב מהתוצאה הנוכחית ומהזמן שנותר
      const homeScore = parseInt(game.ss?.split('-')[0]) || 0;
      const awayScore = parseInt(game.ss?.split('-')[1]) || 0;
      const currentTotal = homeScore + awayScore;
      const quarter = parseInt(game.timer?.q) || 0;
      
      // טוטאל משוער לפי התוצאה הנוכחית והרבע - פשוט לדוגמה
      if (quarter > 0) {
        const estimatedFinalTotal = currentTotal * (4 / quarter) * 1.1;
        return estimatedFinalTotal.toFixed(1);
      }
    }
    
    if (timePoint === 'opening') {
      // ערכי ברירת מחדל הגיוניים
      return oddsType === 'spread' ? "-2.5" : "215.5";
    }
    
    if (timePoint === 'start') {
      // ערכי ברירת מחדל, מעט שונים מהפתיחה
      return oddsType === 'spread' ? "-3.0" : "217.0";
    }
    
    return null;
  }
  
  // חישוב קצב המשחק/זריקות
  static calculateShotRate(game) {
    if (!game || !game.ss || game.time_status !== "1") {
      return { rate: null, color: "neutral" };
    }
    
    // חילוץ תוצאה נוכחית
    const homeScore = parseInt(game.ss.split('-')[0]) || 0;
    const awayScore = parseInt(game.ss.split('-')[1]) || 0;
    const currentTotal = homeScore + awayScore;
    
    // חילוץ נתוני זמן
    const quarter = parseInt(game.timer?.q) || 0;
    const minutes = parseInt(game.timer?.tm) || 0;
    const seconds = parseInt(game.timer?.ts) || 0;
    
    if (quarter <= 0) {
      return { rate: null, color: "neutral" };
    }
    
    // חישוב זמן שעבר במשחק (בדקות)
    const minutesPlayed = ((quarter - 1) * 10) + (10 - minutes) - (seconds / 60);
    
    if (minutesPlayed <= 0) {
      return { rate: null, color: "neutral" };
    }
    
    // חישוב קצב נקודות לדקה
    const pointsPerMinute = currentTotal / minutesPlayed;
    
    // חישוב קצב ניקוד משוער למשחק מלא (40 דקות)
    const projectedTotal = pointsPerMinute * 40;
    
    // קביעת צבע לפי הקצב
    let color = "neutral";
    
    // בדיקה האם יש נתוני טוטאל
    const liveTotal = parseFloat(this.extractOddsFromGame(game, 'live', 'total'));
    
    if (!isNaN(liveTotal)) {
      const totalDiff = projectedTotal - liveTotal;
      
      if (Math.abs(totalDiff) >= 10) {
        color = totalDiff > 0 ? "red" : "blue";
      }
    }
    
    return {
      rate: projectedTotal,
      color
    };
  }
  
  // ניתוח הזדמנות
  static analyzeOpportunity(spreadInfo, totalInfo, shotRateInfo) {
    // לוגיקה לניתוח הזדמנויות
    
    // הזדמנות ירוקה - הפרש גדול בליינים ותנועה משמעותית
    const hasGreenOpportunity = 
      (Math.abs(parseFloat(spreadInfo.diff)) >= 3 && spreadInfo.flag === "green") ||
      (Math.abs(parseFloat(totalInfo.diff)) >= 5 && totalInfo.flag === "green");
    
    // הזדמנות אדומה - בעיקר על סמך קצב זריקות
    const hasRedOpportunity = 
      shotRateInfo.color === "red" && 
      Math.abs(shotRateInfo.rate - parseFloat(totalInfo.current)) >= 15;
    
    // הזדמנות כחולה - מצבים מעורבים
    const hasBlueOpportunity = 
      (shotRateInfo.color === "blue" && spreadInfo.flag !== "neutral") ||
      (Math.abs(parseFloat(spreadInfo.diff)) >= 2 && Math.abs(parseFloat(totalInfo.diff)) >= 3);
    
    // קביעת סוג ההזדמנות
    let type = "neutral";
    let reason = "";
    let recommendation = "";
    
    if (hasGreenOpportunity) {
      type = "green";
      reason = "שינוי משמעותי בליין מצביע על הזדמנות";
      
      if (Math.abs(parseFloat(spreadInfo.diff)) >= 3) {
        recommendation = spreadInfo.direction === "up" ? 
          "כדאי לקחת את הקבוצה המארחת" : 
          "כדאי לקחת את הקבוצה האורחת";
      } else {
        recommendation = totalInfo.direction === "up" ? 
          "כדאי לקחת אובר" : 
          "כדאי לקחת אנדר";
      }
    } else if (hasRedOpportunity) {
      type = "red";
      reason = "קצב המשחק מצביע על אי התאמה עם הליין הנוכחי";
      recommendation = "מומלץ לקחת אנדר";
    } else if (hasBlueOpportunity) {
      type = "blue";
      reason = "שילוב של קצב משחק וליין יוצר הזדמנות";
      recommendation = shotRateInfo.color === "blue" ? 
        "מומלץ לקחת אובר" : 
        "מומלץ לעקוב אחר השינויים בליין";
    }
    
    return {
      type,
      reason,
      recommendation,
      shot_rate: shotRateInfo.rate
    };
  }
  
  // חישוב סטטיסטיקות כלליות
  static calculateStats(games) {
    const stats = {
      opportunity_percentage: 0,
      red_opportunities: 0,
      green_opportunities: 0,
      total_live: 0,
      total_upcoming: 0
    };
    
    if (!games || games.length === 0) {
      return stats;
    }
    
    // ספירת משחקים לפי סטטוס
    stats.total_live = games.filter(g => g.status === 'live').length;
    stats.total_upcoming = games.filter(g => g.status === 'upcoming').length;
    
    // ספירת הזדמנויות
    stats.red_opportunities = games.filter(g => g.opportunity_type === 'red').length;
    stats.green_opportunities = games.filter(g => g.opportunity_type === 'green').length;
    
    // חישוב אחוז הזדמנויות
    const totalOpportunities = stats.red_opportunities + stats.green_opportunities;
    const totalGames = games.length;
    
    if (totalGames > 0) {
      stats.opportunity_percentage = Math.round((totalOpportunities / totalGames) * 100);
    }
    
    return stats;
  }
}

// קומפוננטת האפליקציה הראשית
const BetboxApp = () => {
  // משתני סטייט
  const [games, setGames] = useState([]);
  const [filteredGames, setFilteredGames] = useState([]);
  const [stats, setStats] = useState({
    opportunity_percentage: 0,
    red_opportunities: 0,
    green_opportunities: 0,
    total_live: 0,
    total_upcoming: 0
  });
  const [selectedGame, setSelectedGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('live');
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString('he-IL'));
  const [lastUpdate, setLastUpdate] = useState('-');
  const [filters, setFilters] = useState({
    sport: 'כדורסל',
    league: 'all',
    opportunities: 'all',
    lineMovement: 0
  });
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshRate, setRefreshRate] = useState(30);
