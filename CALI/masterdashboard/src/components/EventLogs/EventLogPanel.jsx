import React, { useState, useEffect } from 'react';

const EventLogPanel = () => {
  const [activeTab, setActiveTab] = useState('system');
  const [logs, setLogs] = useState({
    system: [],
    audio: [],
    cores: [],
    mint: [],
    dals: [],
    goat: []
  });

  // Mock log data
  useEffect(() => {
    const mockLogs = {
      system: [
        { time: '10:23:45', level: 'INFO', message: 'System initialized successfully' },
        { time: '10:23:50', level: 'INFO', message: 'WebSocket connections established' },
        { time: '10:24:01', level: 'WARN', message: 'High CPU usage detected' },
        { time: '10:24:15', level: 'INFO', message: 'Memory optimization completed' },
      ],
      audio: [
        { time: '10:23:52', level: 'INFO', message: 'Audio pipeline initialized' },
        { time: '10:24:02', level: 'INFO', message: 'STT model loaded successfully' },
        { time: '10:24:05', level: 'INFO', message: 'TTS voice synthesis ready' },
        { time: '10:24:10', level: 'WARN', message: 'Audio buffer overflow detected' },
      ],
      cores: [
        { time: '10:23:55', level: 'INFO', message: 'UCM_Core initialized' },
        { time: '10:23:58', level: 'INFO', message: 'KayGee resonance calibration complete' },
        { time: '10:24:03', level: 'INFO', message: 'Caleon memory matrix loaded' },
        { time: '10:24:08', level: 'INFO', message: 'Cali_X pattern synthesis active' },
      ],
      mint: [
        { time: '10:24:00', level: 'INFO', message: 'TrueMark certificate minted' },
        { time: '10:24:12', level: 'INFO', message: 'CertSig validation completed' },
        { time: '10:24:18', level: 'WARN', message: 'Mint queue backlog detected' },
      ],
      dals: [
        { time: '10:23:48', level: 'INFO', message: 'DALS processing pipeline active' },
        { time: '10:24:06', level: 'INFO', message: 'Task distribution optimized' },
        { time: '10:24:14', level: 'WARN', message: 'High latency spike detected' },
      ],
      goat: [
        { time: '10:23:56', level: 'INFO', message: 'GOAT model training initiated' },
        { time: '10:24:04', level: 'INFO', message: 'Prediction accuracy improved to 94%' },
        { time: '10:24:16', level: 'INFO', message: 'New pattern recognition activated' },
      ]
    };

    setLogs(mockLogs);
  }, []);

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'text-red-400';
      case 'WARN': return 'text-yellow-400';
      case 'INFO': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const tabs = [
    { id: 'system', label: 'System', count: logs.system.length },
    { id: 'audio', label: 'Audio', count: logs.audio.length },
    { id: 'cores', label: 'Cores', count: logs.cores.length },
    { id: 'mint', label: 'Mint', count: logs.mint.length },
    { id: 'dals', label: 'DALS', count: logs.dals.length },
    { id: 'goat', label: 'GOAT', count: logs.goat.length },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="flex border-b border-slate-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-cyan-400 border-b-2 border-cyan-400 bg-slate-800'
                : 'text-slate-400 hover:text-slate-300'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-xs bg-slate-700 rounded-full">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {logs[activeTab].map((log, index) => (
            <div key={index} className="flex items-center space-x-3 text-sm bg-slate-800/50 rounded px-3 py-2">
              <span className="text-xs text-slate-500 font-mono w-16">
                {log.time}
              </span>
              <span className={`text-xs font-bold w-12 ${getLevelColor(log.level)}`}>
                {log.level}
              </span>
              <span className="text-slate-300 flex-1">
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EventLogPanel;