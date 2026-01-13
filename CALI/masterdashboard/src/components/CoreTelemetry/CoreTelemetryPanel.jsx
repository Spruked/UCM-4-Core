import React from 'react';
import CoreCard from './CoreCard';

const CoreTelemetryPanel = ({ metrics }) => {
  const cores = ['ucm_core', 'kaygee', 'caleon', 'cali_x'];

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4 text-cyan-400 border-b border-slate-700 pb-2">
        Core Telemetry
      </h2>

      <div className="space-y-3">
        {cores.map((coreId) => (
          <CoreCard
            key={coreId}
            coreId={coreId}
            data={metrics?.cores?.[coreId]}
            isActive={metrics?.attention?.active_core === coreId}
          />
        ))}
      </div>

      {/* Core Coordination Status */}
      <div className="mt-6 p-3 bg-slate-800 rounded-lg">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Coordination Status</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-slate-400">Phase Coherence:</div>
          <div className="text-green-400">{(metrics?.attention?.phase_coherence || 0).toFixed(2)}</div>
          <div className="text-slate-400">Meta Confidence:</div>
          <div className="text-cyan-400">{(metrics?.attention?.meta_confidence || 0).toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
};

export default CoreTelemetryPanel;