import React from 'react';
import AttentionHeatmap from './AttentionHeatmap';
import ReasoningTimeline from './ReasoningTimeline';
import ConflictResolutionGraph from './ConflictResolutionGraph';

const AttentionGovernorView = ({ metrics }) => {
  return (
    <div className="p-6 h-full">
      <h2 className="text-xl font-bold mb-6 text-cyan-400 border-b border-slate-700 pb-2">
        Attention Governor Live View
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
        {/* Attention Heatmap */}
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4 text-slate-200">Attention Heatmap</h3>
          <AttentionHeatmap attentionWeights={metrics?.attention?.weights} />
        </div>

        {/* Reasoning Timeline */}
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4 text-slate-200">Reasoning Timeline</h3>
          <ReasoningTimeline timeline={metrics?.attention?.timeline} />
        </div>

        {/* Conflict Resolution */}
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4 text-slate-200">Conflict Resolution</h3>
          <ConflictResolutionGraph conflicts={metrics?.attention?.conflicts} />
        </div>

        {/* Meta Reasoning Stats */}
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4 text-slate-200">Meta Reasoning</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-400">Overall Confidence</span>
              <span className="text-cyan-400 font-bold">
                {(metrics?.attention?.meta_confidence || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Phase Coherence</span>
              <span className="text-green-400 font-bold">
                {(metrics?.attention?.phase_coherence || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Decision Latency</span>
              <span className="text-yellow-400 font-bold">
                {(metrics?.attention?.decision_latency || 0).toFixed(2)}s
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Active Core</span>
              <span className="text-purple-400 font-bold">
                {metrics?.attention?.active_core?.replace('_', ' ') || 'None'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttentionGovernorView;