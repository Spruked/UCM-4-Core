import React from 'react';

const CoreCard = ({ coreId, data, isActive }) => {
  const confidence = data?.confidence || 0;
  const attentionWeight = data?.attention_weight || 0;
  const latency = data?.latency || 0;
  const verdict = data?.verdict || 'Idle';

  const coreNames = {
    ucm_core: 'UCM_Core_ECM',
    kaygee: 'KayGee_1.0',
    caleon: 'Caleon_Genesis',
    cali_x: 'Cali_X_One'
  };

  const coreColors = {
    ucm_core: 'border-purple-500 bg-purple-500/10',
    kaygee: 'border-cyan-500 bg-cyan-500/10',
    caleon: 'border-green-500 bg-green-500/10',
    cali_x: 'border-orange-500 bg-orange-500/10'
  };

  return (
    <div className={`p-3 rounded-lg border-l-4 transition-all duration-300 ${
      isActive
        ? `${coreColors[coreId]} shadow-lg shadow-cyan-500/20`
        : 'border-slate-600 bg-slate-800/50'
    }`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-medium text-sm text-slate-200">
          {coreNames[coreId]}
        </h3>
        {isActive && (
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
        )}
      </div>

      {/* Confidence Bar */}
      <div className="mb-2">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Confidence</span>
          <span>{(confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              confidence > 0.8 ? 'bg-green-400' :
              confidence > 0.6 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Attention Weight */}
      <div className="mb-2">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Attention</span>
          <span>{(attentionWeight * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1">
          <div
            className="h-1 rounded-full bg-cyan-400 transition-all duration-500"
            style={{ width: `${attentionWeight * 100}%` }}
          />
        </div>
      </div>

      {/* Latency */}
      <div className="flex justify-between text-xs mb-2">
        <span className="text-slate-400">Latency</span>
        <span className={latency > 1 ? 'text-red-400' : latency > 0.5 ? 'text-yellow-400' : 'text-green-400'}>
          {latency.toFixed(2)}s
        </span>
      </div>

      {/* Verdict */}
      <div className="text-xs text-slate-300 bg-slate-700/50 p-2 rounded">
        {verdict}
      </div>
    </div>
  );
};

export default CoreCard;