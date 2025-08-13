import React from 'react';
import './PositionsTable.css';

function PositionsTable({ positions, currentPrices }) {
  if (!positions || positions.length === 0) {
    return (
      <div className="positions-table">
        <h3>Açık Pozisyonlar</h3>
        <div className="no-positions">
          Henüz açık pozisyon bulunmuyor
        </div>
      </div>
    );
  }

  const formatNumber = (num) => {
    return num?.toFixed(2) || '0.00';
  };

  const getPnLClass = (pnl) => {
    if (pnl > 0) return 'positive';
    if (pnl < 0) return 'negative';
    return 'neutral';
  };

  return (
    <div className="positions-table">
      <h3>Açık Pozisyonlar</h3>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Metal</th>
              <th>Miktar</th>
              <th>Ort. Fiyat</th>
              <th>Güncel Fiyat</th>
              <th>P/L</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position, index) => {
              const currentPrice = currentPrices[position.symbol] || position.current_price;
              const pnl = (currentPrice - position.avg_price) * position.quantity;
              
              return (
                <tr key={index}>
                  <td className="symbol">
                    {position.symbol === 'GOLD' ? 'Altın' : 'Gümüş'}
                  </td>
                  <td>{formatNumber(position.quantity)}</td>
                  <td>${formatNumber(position.avg_price)}</td>
                  <td>${formatNumber(currentPrice)}</td>
                  <td className={`pnl ${getPnLClass(pnl)}`}>
                    ${formatNumber(Math.abs(pnl))}
                    {pnl > 0 && ' ↗'}
                    {pnl < 0 && ' ↘'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      <div className="summary">
        <div className="total-pnl">
          <span>Toplam P/L: </span>
          <span className={getPnLClass(
            positions.reduce((total, pos) => {
              const currentPrice = currentPrices[pos.symbol] || pos.current_price;
              return total + ((currentPrice - pos.avg_price) * pos.quantity);
            }, 0)
          )}>
            ${formatNumber(Math.abs(
              positions.reduce((total, pos) => {
                const currentPrice = currentPrices[pos.symbol] || pos.current_price;
                return total + ((currentPrice - pos.avg_price) * pos.quantity);
              }, 0)
            ))}
          </span>
        </div>
      </div>
    </div>
  );
}

export default PositionsTable;
