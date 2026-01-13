import React from 'react';

const GlobalStatusBar = ({ metrics, isConnected, connectionStatus }) => {
  const systemHealth = metrics?.system?.health || 0;
  const cpuLoad = metrics?.system?.cpu_load || 0;
  const vaultLoad = metrics?.system?.vault_load || 0;
  const audioLatency = metrics?.audio?.latency || 0;
  const activeCore = metrics?.attention?.active_core || 'None';
  const memoryUsage = metrics?.system?.memory_usage || 0;

  const getHealthColor = (health) => {
    if (health > 0.8) return 'text-emerald-400';
    if (health > 0.6) return 'text-amber-400';
    return 'text-red-400';
  };

  const getLoadColor = (load) => {
    if (load < 0.5) return 'text-emerald-400';
    if (load < 0.8) return 'text-amber-400';
    return 'text-red-400';
  };

  const getConnectionColor = () => {
    if (connectionStatus === 'connected') return 'bg-emerald-400';
    if (connectionStatus === 'connecting') return 'bg-amber-400 animate-pulse';
    return 'bg-red-400';
  };

  return (
    <div className="h-full flex items-center justify-between px-8 bg-gradient-to-r from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl border-b border-slate-700/50 shadow-lg">
      {/* Connection Status & System Health */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${getConnectionColor()} shadow-lg`} />
          <span className="text-sm font-medium text-slate-300">
            {connectionStatus === 'connected' ? 'Connected' :
             connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-slate-400">System Health</span>
          <span className={`text-lg font-bold ${getHealthColor(systemHealth)}`}>
            {(systemHealth * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="flex items-center space-x-8">
        {/* CPU Load */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">CPU</span>
          <div className="w-24 bg-slate-700/50 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${cpuLoad > 0.8 ? 'bg-red-400' : cpuLoad > 0.6 ? 'bg-amber-400' : 'bg-emerald-400'}`}
              style={{ width: `${cpuLoad * 100}%` }}
            />
          </div>
          <span className={`text-sm font-semibold ${getLoadColor(cpuLoad)}`}>
            {(cpuLoad * 100).toFixed(0)}%
          </span>
        </div>

        {/* Memory Usage */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">Memory</span>
          <div className="w-24 bg-slate-700/50 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${memoryUsage > 0.8 ? 'bg-red-400' : memoryUsage > 0.6 ? 'bg-amber-400' : 'bg-emerald-400'}`}
              style={{ width: `${memoryUsage * 100}%` }}
            />
          </div>
          <span className={`text-sm font-semibold ${getLoadColor(memoryUsage)}`}>
            {(memoryUsage * 100).toFixed(0)}%
          </span>
        </div>

        {/* Vault Load */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">Vault</span>
          <div className="w-24 bg-slate-700/50 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${vaultLoad > 0.8 ? 'bg-red-400' : vaultLoad > 0.6 ? 'bg-amber-400' : 'bg-emerald-400'}`}
              style={{ width: `${vaultLoad * 100}%` }}
            />
          </div>
          <span className={`text-sm font-semibold ${getLoadColor(vaultLoad)}`}>
            {(vaultLoad * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Audio & Core Status */}
      <div className="flex items-center space-x-8">
        {/* Audio Latency */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">Audio Latency</span>
          <span className={`text-sm font-semibold ${audioLatency > 2 ? 'text-red-400' : audioLatency > 1 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {audioLatency.toFixed(2)}s
          </span>
        </div>

        {/* Active Core */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">Active Core</span>
          <span className="text-cyan-400 font-bold text-sm bg-slate-700/50 px-4 py-1.5 rounded-full border border-slate-600/50">
            {activeCore.replace('_', ' ')}
          </span>
        </div>

        {/* Timestamp */}
        <div className="text-xs text-slate-500 font-medium">
          {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default GlobalStatusBar;