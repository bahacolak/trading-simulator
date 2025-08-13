import React, { useState } from 'react';
import config from '../config';
import './TradePanel.css';

function TradePanel({ token, currentPrices, onTradeComplete }) {
  const [symbol, setSymbol] = useState('GOLD');
  const [side, setSide] = useState('buy');
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleTrade = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/v1/trading/trade`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symbol: symbol,
          side: side,
          quantity: quantity
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.success ? data.message : 'İşlem başarılı!');
        setQuantity(1);
        onTradeComplete();
      } else {
        setMessage(data.detail || data.message || 'İşlem başarısız');
      }
    } catch (error) {
      setMessage('Bağlantı hatası');
    } finally {
      setLoading(false);
    }
  };

  const currentPrice = currentPrices[symbol];
  const totalCost = currentPrice * quantity;

  return (
    <div className="trade-panel">
      <h3>İşlem Paneli</h3>
      
      {message && (
        <div className={`message ${message.includes('başarılı') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleTrade}>
        <div className="form-group">
          <label>Metal:</label>
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
            <option value="GOLD">Altın</option>
            <option value="SILVER">Gümüş</option>
          </select>
        </div>

        <div className="form-group">
          <label>İşlem Türü:</label>
          <div className="trade-type-buttons">
            <button
              type="button"
              className={`trade-btn ${side === 'buy' ? 'buy active' : 'buy'}`}
              onClick={() => setSide('buy')}
            >
              Al
            </button>
            <button
              type="button"
              className={`trade-btn ${side === 'sell' ? 'sell active' : 'sell'}`}
              onClick={() => setSide('sell')}
            >
              Sat
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Miktar:</label>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={quantity}
            onChange={(e) => setQuantity(parseFloat(e.target.value) || 0)}
            required
          />
        </div>

        <div className="price-info">
          <div className="price-row">
            <span>Güncel Fiyat:</span>
            <span>${currentPrice?.toFixed(2)}</span>
          </div>
          <div className="price-row total">
            <span>Toplam Tutar:</span>
            <span>${totalCost?.toFixed(2)}</span>
          </div>
        </div>

        <button 
          type="submit" 
          className={`submit-btn ${side}`}
          disabled={loading || !quantity || quantity <= 0}
        >
          {loading ? 'İşleniyor...' : (side === 'buy' ? 'Al' : 'Sat')}
        </button>
      </form>
    </div>
  );
}

export default TradePanel;
