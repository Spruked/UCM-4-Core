import React from 'react';
import DALSWidget from './DALSWidget';
import GOATWidget from './GOATWidget';
import TrueMarkMintWidget from './TrueMarkMintWidget';
import CertSigMintWidget from './CertSigMintWidget';

const IntegrationPanel = ({ metrics }) => {
  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4 text-cyan-400 border-b border-slate-700 pb-2">
        System Integrations
      </h2>

      <div className="space-y-4">
        <DALSWidget data={metrics?.dals} />
        <GOATWidget data={metrics?.goat} />
        <TrueMarkMintWidget data={metrics?.truemark} />
        <CertSigMintWidget data={metrics?.certsig} />
      </div>

      {/* Unified Vault Status */}
      <div className="mt-6 p-3 bg-slate-800 rounded-lg">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Unified Vault</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-slate-400">Entries:</div>
          <div className="text-cyan-400">{metrics?.vault?.entries || 0}</div>
          <div className="text-slate-400">Load:</div>
          <div className="text-green-400">{(metrics?.vault?.load || 0).toFixed(2)}</div>
          <div className="text-slate-400">Integrity:</div>
          <div className="text-purple-400">{(metrics?.vault?.integrity || 0).toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
};

export default IntegrationPanel;