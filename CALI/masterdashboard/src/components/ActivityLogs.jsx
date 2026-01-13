import React, { useState, useEffect } from 'react';

const ActivityLogs = ({ coreId, maxEntries = 10 }) => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Generate mock logs for demonstration
    const mockLogs = [
      { timestamp: '12:34:56', message: 'Pattern recognition completed', type: 'success' },
      { timestamp: '12:34:45', message: 'Neural network updated', type: 'info' },
      { timestamp: '12:34:32', message: 'Memory consolidation finished', type: 'success' },
      { timestamp: '12:34:21', message: 'Ethical evaluation passed', type: 'success' },
      { timestamp: '12:34:15', message: 'Cross-modal integration active', type: 'info' },
      { timestamp: '12:34:08', message: 'Consciousness mapping updated', type: 'info' },
      { timestamp: '12:34:02', message: 'Voice synthesis calibrated', type: 'success' },
      { timestamp: '12:33:58', message: 'Learning rate adjusted', type: 'warning' },
      { timestamp: '12:33:52', message: 'Pattern synthesis initiated', type: 'info' },
      { timestamp: '12:33:45', message: 'System health check passed', type: 'success' },
    ];

    setLogs(mockLogs.slice(0, maxEntries));
  }, [coreId, maxEntries]);

  const getTypeColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h3 className="font-bold mb-3">Activity Log</h3>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start gap-3 text-sm">
            <span className="text-gray-500 font-mono text-xs w-16">{log.timestamp}</span>
            <span className={`flex-1 ${getTypeColor(log.type)}`}>{log.message}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs transition">
          Clear Logs
        </button>
        <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs transition">
          Export
        </button>
      </div>
    </div>
  );
};

export default ActivityLogs;