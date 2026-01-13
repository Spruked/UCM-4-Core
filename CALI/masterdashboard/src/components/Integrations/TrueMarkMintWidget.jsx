import React from 'react';

const TrueMarkMintWidget = ({ data }) => {
  const status = data?.status || 'idle';
  const minted = data?.minted || 0;
  const pending = data?.pending || 0;
  const verified = data?.verified || 0;

  const getStatusColor = (status) => {
    switch (status) {
      case 'minting': return 'text-blue-400';
      case 'verifying': return 'text-yellow-400';
      case 'active': return 'text-green-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-slate-200">TrueMark Mint</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)} bg-slate-700`}>
          {status.toUpperCase()}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Minted</span>
          <span className="text-green-400">{minted}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Pending</span>
          <span className="text-yellow-400">{pending}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Verified</span>
          <span className="text-purple-400">{verified}</span>
        </div>
      </div>
    </div>
  );
};

export default TrueMarkMintWidget;