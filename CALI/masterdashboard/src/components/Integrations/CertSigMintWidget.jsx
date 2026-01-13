import React from 'react';

const CertSigMintWidget = ({ data }) => {
  const status = data?.status || 'idle';
  const signatures = data?.signatures || 0;
  const certificates = data?.certificates || 0;
  const validity = data?.validity || 0;

  const getStatusColor = (status) => {
    switch (status) {
      case 'signing': return 'text-blue-400';
      case 'validating': return 'text-yellow-400';
      case 'active': return 'text-green-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-slate-200">CertSig Mint</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)} bg-slate-700`}>
          {status.toUpperCase()}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Signatures</span>
          <span className="text-cyan-400">{signatures}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Certificates</span>
          <span className="text-green-400">{certificates}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Validity</span>
          <span className={validity > 0.9 ? 'text-green-400' : validity > 0.7 ? 'text-yellow-400' : 'text-red-400'}>
            {(validity * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default CertSigMintWidget;