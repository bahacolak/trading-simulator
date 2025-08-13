import React, { useState, useEffect } from 'react';
import config from './config';
import PriceChart from './components/PriceChart';
import TradePanel from './components/TradePanel';
import PositionsTable from './components/PositionsTable';
import Login from './components/Login';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [prices, setPrices] = useState({ GOLD: 2000, SILVER: 25 });
  const [positions, setPositions] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    if (token) {
      connectWebSocket();
      fetchPositions();
    }
    return () => {
      if (ws) ws.close();
    };
  }, [token]);

  const connectWebSocket = () => {
    const websocket = new WebSocket(`${config.WS_BASE_URL}/ws`);
    
    websocket.onopen = () => {
      console.log('WebSocket bağlandı');
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPrices(data);
    };

    websocket.onclose = () => {
      console.log('WebSocket kapandı, 3 saniye sonra yeniden bağlanılacak');
      setTimeout(connectWebSocket, 3000);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket hatası:', error);
    };
  };

  const fetchPositions = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/v1/trading/positions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPositions(data);
      }
    } catch (error) {
      console.error('Pozisyonlar alınamadı:', error);
    }
  };

  const handleLogin = (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    if (ws) ws.close();
  };

  const handleTradeComplete = () => {
    fetchPositions();
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Trading Simulator</h1>
        <button className="logout-btn" onClick={handleLogout}>Çıkış</button>
      </header>
      
      <div className="main-content">
        <div className="left-panel">
          <PriceChart prices={prices} />
          <PositionsTable positions={positions} currentPrices={prices} />
        </div>
        
        <div className="right-panel">
          <TradePanel 
            token={token} 
            currentPrices={prices} 
            onTradeComplete={handleTradeComplete} 
          />
        </div>
      </div>
    </div>
  );
}

export default App;
