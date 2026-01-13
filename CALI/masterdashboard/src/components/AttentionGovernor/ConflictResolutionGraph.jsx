import React from 'react';

const ConflictResolutionGraph = ({ conflicts }) => {
  // Mock conflict data
  const mockConflicts = conflicts || [
    { core1: 'ucm_core', core2: 'cali_x', resolution: 0.85, status: 'resolved' },
    { core1: 'kaygee', core2: 'caleon', resolution: 0.92, status: 'resolved' },
    { core1: 'ucm_core', core2: 'caleon', resolution: 0.78, status: 'pending' },
  ];

  const coreNames = {
    ucm_core: 'UCM',
    kaygee: 'KG',
    caleon: 'CLN',
    cali_x: 'CX'
  };

  return (
    <div className="w-full h-48">
      <div className="space-y-3">
        {mockConflicts.map((conflict, index) => (
          <div key={index} className="bg-slate-700 rounded p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-slate-300">
                {coreNames[conflict.core1]} ↔ {coreNames[conflict.core2]}
              </span>
              <span className={`text-xs px-2 py-1 rounded ${
                conflict.status === 'resolved' ? 'bg-green-600 text-green-100' : 'bg-yellow-600 text-yellow-100'
              }`}>
                {conflict.status}
              </span>
            </div>

            <div className="w-full bg-slate-600 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  conflict.resolution > 0.8 ? 'bg-green-400' :
                  conflict.resolution > 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                }`}
                style={{ width: `${conflict.resolution * 100}%` }}
              />
            </div>

            <div className="text-xs text-slate-400 mt-1">
              Resolution: {(conflict.resolution * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConflictResolutionGraph;