import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './PriceChart.css';

function PriceChart({ prices }) {
  const [goldData, setGoldData] = useState([]);
  const [silverData, setSilverData] = useState([]);
  const [selectedMetal, setSelectedMetal] = useState('GOLD');

  useEffect(() => {
    if (prices.GOLD && prices.SILVER) {
      const timestamp = new Date().toLocaleTimeString();
      
      setGoldData(prev => {
        const newData = [...prev, { time: timestamp, price: prices.GOLD }];
        return newData.slice(-20);
      });
      
      setSilverData(prev => {
        const newData = [...prev, { time: timestamp, price: prices.SILVER }];
        return newData.slice(-20);
      });
    }
  }, [prices]);

  const currentData = selectedMetal === 'GOLD' ? goldData : silverData;
  const currentPrice = prices[selectedMetal];

  return (
    <div className="price-chart">
      <div className="chart-header">
        <div className="metal-selector">
          <button 
            className={selectedMetal === 'GOLD' ? 'active' : ''}
            onClick={() => setSelectedMetal('GOLD')}
          >
            Altın
          </button>
          <button 
            className={selectedMetal === 'SILVER' ? 'active' : ''}
            onClick={() => setSelectedMetal('SILVER')}
          >
            Gümüş
          </button>
        </div>
        
        <div className="current-price">
          <span className="price-label">{selectedMetal}:</span>
          <span className="price-value">${currentPrice?.toFixed(2)}</span>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={currentData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis 
              dataKey="time" 
              stroke="#888"
              fontSize={12}
            />
            <YAxis 
              stroke="#888"
              fontSize={12}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#2a2a2a',
                border: '1px solid #444',
                borderRadius: '4px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke={selectedMetal === 'GOLD' ? '#FFD700' : '#C0C0C0'}
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default PriceChart;
