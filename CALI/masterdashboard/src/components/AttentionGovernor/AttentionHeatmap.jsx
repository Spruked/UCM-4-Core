import React from 'react';

const AttentionHeatmap = ({ attentionWeights }) => {
  const cores = ['ucm_core', 'kaygee', 'caleon', 'cali_x'];
  const coreNames = {
    ucm_core: 'UCM',
    kaygee: 'KG',
    caleon: 'CLN',
    cali_x: 'CX'
  };

  const getHeatmapColor = (weight) => {
    const intensity = Math.floor(weight * 255);
    return `rgb(${intensity}, ${Math.floor(intensity * 0.5)}, ${Math.floor(intensity * 0.8)})`;
  };

  return (
    <div className="w-full h-48 flex items-center justify-center">
      <div className="grid grid-cols-4 gap-2">
        {cores.map((fromCore) => (
          cores.map((toCore) => {
            const weight = attentionWeights?.[fromCore]?.[toCore] || 0;
            return (
              <div
                key={`${fromCore}-${toCore}`}
                className="w-12 h-12 rounded border border-slate-600 flex items-center justify-center text-xs font-bold transition-all duration-300"
                style={{
                  backgroundColor: getHeatmapColor(weight),
                  opacity: weight > 0 ? 0.8 : 0.3
                }}
                title={`${coreNames[fromCore]} → ${coreNames[toCore]}: ${(weight * 100).toFixed(0)}%`}
              >
                {(weight * 100).toFixed(0)}
              </div>
            );
          })
        ))}
      </div>

      {/* Legend */}
      <div className="absolute bottom-2 right-2 text-xs text-slate-400">
        <div>Attention Flow Matrix</div>
        <div className="flex items-center mt-1">
          <div className="w-3 h-3 bg-blue-900 rounded mr-1"></div>
          <span>Low</span>
          <div className="w-3 h-3 bg-cyan-400 rounded mx-1"></div>
          <span>High</span>
        </div>
      </div>
    </div>
  );
};

export default AttentionHeatmap;