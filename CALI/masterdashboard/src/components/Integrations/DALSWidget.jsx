import React from 'react';

const DALSWidget = ({ data }) => {
  const status = data?.status || 'idle';
  const throughput = data?.throughput || 0;
  const latency = data?.latency || 0;
  const activeTasks = data?.active_tasks || 0;

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'processing': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-slate-200">DALS</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)} bg-slate-700`}>
          {status.toUpperCase()}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Throughput</span>
          <span className="text-cyan-400">{throughput}/s</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Latency</span>
          <span className={latency > 100 ? 'text-red-400' : latency > 50 ? 'text-yellow-400' : 'text-green-400'}>
            {latency}ms
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Active Tasks</span>
          <span className="text-purple-400">{activeTasks}</span>
        </div>
      </div>
    </div>
  );
};

export default DALSWidget;