import React from 'react';

const GOATWidget = ({ data }) => {
  const status = data?.status || 'idle';
  const accuracy = data?.accuracy || 0;
  const predictions = data?.predictions || 0;
  const confidence = data?.confidence || 0;

  const getStatusColor = (status) => {
    switch (status) {
      case 'learning': return 'text-blue-400';
      case 'predicting': return 'text-green-400';
      case 'training': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-slate-200">GOAT</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)} bg-slate-700`}>
          {status.toUpperCase()}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Accuracy</span>
          <span className="text-green-400">{(accuracy * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Predictions</span>
          <span className="text-cyan-400">{predictions}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Confidence</span>
          <span className={confidence > 0.8 ? 'text-green-400' : confidence > 0.6 ? 'text-yellow-400' : 'text-red-400'}>
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default GOATWidget;