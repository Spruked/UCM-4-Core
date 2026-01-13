import React from 'react';

const ReasoningTimeline = ({ timeline }) => {
  // Mock timeline data if none provided
  const mockTimeline = timeline || [
    { time: '0s', event: 'Query received', core: 'system' },
    { time: '0.2s', event: 'UCM analysis', core: 'ucm_core' },
    { time: '0.5s', event: 'KayGee resonance', core: 'kaygee' },
    { time: '0.8s', event: 'Caleon memory', core: 'caleon' },
    { time: '1.1s', event: 'Cali_X synthesis', core: 'cali_x' },
    { time: '1.4s', event: 'Governor decision', core: 'attention' },
  ];

  const getEventColor = (core) => {
    const colors = {
      system: 'bg-gray-500',
      ucm_core: 'bg-purple-500',
      kaygee: 'bg-cyan-500',
      caleon: 'bg-green-500',
      cali_x: 'bg-orange-500',
      attention: 'bg-red-500'
    };
    return colors[core] || 'bg-slate-500';
  };

  return (
    <div className="w-full h-48 overflow-y-auto">
      <div className="space-y-2">
        {mockTimeline.slice(-10).map((event, index) => (
          <div key={index} className="flex items-center space-x-3 text-sm">
            <div className="w-16 text-xs text-slate-400 font-mono">
              {event.time}
            </div>
            <div className={`w-3 h-3 rounded-full ${getEventColor(event.core)} flex-shrink-0`} />
            <div className="flex-1 text-slate-300">
              {event.event}
            </div>
            <div className="text-xs text-slate-500 capitalize">
              {event.core.replace('_', ' ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReasoningTimeline;