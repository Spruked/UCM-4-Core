import React, { useState, useEffect } from 'react';

const MetricsChart = ({ title, data, color = '#00ffcc', height = 200 }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Generate mock time-series data
    const generateData = () => {
      const now = Date.now();
      return Array.from({ length: 20 }, (_, i) => ({
        time: now - (19 - i) * 30000, // 30 second intervals
        value: Math.random() * 100
      }));
    };

    setChartData(generateData());

    // Update every 5 seconds
    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = [...prev.slice(1), {
          time: Date.now(),
          value: Math.random() * 100
        }];
        return newData;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const maxValue = Math.max(...chartData.map(d => d.value));
  const minValue = Math.min(...chartData.map(d => d.value));

  const points = chartData.map((point, index) => {
    const x = (index / (chartData.length - 1)) * 100;
    const y = 100 - ((point.value - minValue) / (maxValue - minValue || 1)) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h3 className="font-bold mb-3">{title}</h3>
      <div style={{ height: `${height}px` }} className="relative">
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
              <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100" height="100" fill="url(#grid)" />

          {/* Chart line */}
          <polyline
            fill="none"
            stroke={color}
            strokeWidth="2"
            points={points}
          />

          {/* Gradient fill */}
          <polygon
            fill={`url(#gradient-${title.replace(/\s+/g, '-')})`}
            points={`0,100 ${points} 100,100`}
            opacity="0.3"
          />

          <defs>
            <linearGradient id={`gradient-${title.replace(/\s+/g, '-')}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.8"/>
              <stop offset="100%" stopColor={color} stopOpacity="0"/>
            </linearGradient>
          </defs>
        </svg>

        {/* Current value display */}
        <div className="absolute top-2 right-2 text-right">
          <div className="text-2xl font-mono" style={{ color }}>
            {chartData[chartData.length - 1]?.value.toFixed(1) || 0}
          </div>
          <div className="text-xs text-gray-400">Current</div>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div>
          <div className="text-gray-400">Peak</div>
          <div className="font-mono">{maxValue.toFixed(1)}</div>
        </div>
        <div>
          <div className="text-gray-400">Avg</div>
          <div className="font-mono">
            {(chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length).toFixed(1)}
          </div>
        </div>
        <div>
          <div className="text-gray-400">Min</div>
          <div className="font-mono">{minValue.toFixed(1)}</div>
        </div>
      </div>
    </div>
  );
};

export default MetricsChart;