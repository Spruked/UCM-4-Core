import React, { useState, useEffect } from 'react';
import MonitoringOrb from './components/MonitoringOrb';
import NotificationsPanel from './components/NotificationsPanel';
import ActivityLogs from './components/ActivityLogs';
import MetricsChart from './components/MetricsChart';

function App() {
  const [councilState, setCouncilState] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [screenStream, setScreenStream] = useState(null);
  const [helpActive, setHelpActive] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCore, setSelectedCore] = useState('ucm_core');
  const [executingFunctions, setExecutingFunctions] = useState(new Set());

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws/council');

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to Core 4 Council');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received council state:', data);
      setCouncilState(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected');
    };

    return () => ws.close();
  }, []);

  const handlePermissionRequest = async (type, stream) => {
    if (type === 'screen') {
      setScreenStream(stream);

      // Send to council for monitoring
      const ws = new WebSocket('ws://localhost:8001/ws/assist');
      ws.onopen = () => {
        ws.send(JSON.stringify({
          action: 'begin_monitoring',
          stream_id: stream.id
        }));
      };
    }
  };

  const handleHelpRequest = (isActive) => {
    setHelpActive(isActive);

    // Notify council that user needs assistance
    const ws = new WebSocket('ws://localhost:8001/ws/assist');
    ws.onopen = () => {
      ws.send(JSON.stringify({
        action: isActive ? 'help_requested' : 'help_cancelled',
        timestamp: Date.now()
      }));
    };
  };

  const executeCoreFunction = (coreId, functionName) => {
    const functionKey = `${coreId}-${functionName}`;
    setExecutingFunctions(prev => new Set([...prev, functionKey]));
    
    const ws = new WebSocket('ws://localhost:8001/ws/assist');
    ws.onopen = () => {
      ws.send(JSON.stringify({
        action: 'execute_function',
        core_id: coreId,
        function_name: functionName,
        timestamp: Date.now()
      }));
      console.log(`Executing ${functionName} on ${coreId}`);
      
      // Clear executing state after 3 seconds
      setTimeout(() => {
        setExecutingFunctions(prev => {
          const newSet = new Set(prev);
          newSet.delete(functionKey);
          return newSet;
        });
      }, 3000);
    };
  };

  // Screen preview for the user (shows what council sees)
  const [previewUrl, setPreviewUrl] = useState(null);
  useEffect(() => {
    if (screenStream) {
      setPreviewUrl(URL.createObjectURL(screenStream));
    }
  }, [screenStream]);

  const coreDetails = {
    ucm_core: {
      name: 'UCM Core',
      description: 'Philosophical Framework & Consciousness',
      color: 'cyan',
      functions: ['Pattern Recognition', 'Ethical Reasoning', 'Consciousness Mapping'],
      status: 'Active'
    },
    kaygee: {
      name: 'KayGee',
      description: 'Cognitive Resonance & Learning',
      color: 'purple',
      functions: ['Neural Training', 'Memory Formation', 'Pattern Synthesis'],
      status: 'Active'
    },
    caleon: {
      name: 'Caleon',
      description: 'Consciousness Continuity & Voice',
      color: 'green',
      functions: ['Voice Synthesis', 'Emotional Processing', 'Continuity Maintenance'],
      status: 'Active'
    },
    cali_x: {
      name: 'Cali X',
      description: 'Pattern Synthesis & Integration',
      color: 'amber',
      functions: ['Cross-Modal Integration', 'Creative Synthesis', 'Adaptive Learning'],
      status: 'Active'
    }
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Active Speaker Display */}
      <div className="mb-8 flex justify-center">
        <div className="relative">
          <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
            <div className="text-center">
              <div className="text-xs">ACTIVE SPEAKER</div>
              <div className="text-2xl font-bold">
                {councilState?.active_speaker?.replace('_', ' ').toUpperCase() || 'IDLE'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Council State Grid */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {Object.entries(councilState?.council || {}).map(([coreId, data]) => {
          const hasExecutingFunction = coreDetails[coreId]?.functions?.some(func => 
            executingFunctions.has(`${coreId}-${func}`)
          );
          
          return (
            <div
              key={coreId}
              className="bg-gray-800 p-4 rounded-lg cursor-pointer hover:bg-gray-700 transition relative"
              onClick={() => {
                setSelectedCore(coreId);
                setActiveTab('cores');
              }}
            >
              {hasExecutingFunction && (
                <div className="absolute top-2 right-2 w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
              )}
              <h3 className="font-bold mb-2">{coreId.replace('_', ' ').toUpperCase()}</h3>
              <div className="text-3xl font-mono mb-2">
                {(data?.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-400">{data?.verdict || 'Idle'}</div>
              <button className="mt-2 px-3 py-1 bg-cyan-600 hover:bg-cyan-500 rounded text-sm transition">
                View Details
              </button>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="bg-green-600 hover:bg-green-500 p-3 rounded font-bold transition">
            🔄 Sync Council
          </button>
          <button className="bg-blue-600 hover:bg-blue-500 p-3 rounded font-bold transition">
            📊 Generate Report
          </button>
          <button className="bg-purple-600 hover:bg-purple-500 p-3 rounded font-bold transition">
            🧠 Train Models
          </button>
          <button className="bg-red-600 hover:bg-red-500 p-3 rounded font-bold transition">
            🚨 Emergency Stop
          </button>
        </div>
      </div>
    </div>
  );

  const renderCoresTab = () => {
    const core = coreDetails[selectedCore];
    const data = councilState?.council?.[selectedCore];

    return (
      <div className="space-y-6">
        {/* Core Header */}
        <div className={`bg-${core.color}-900 p-6 rounded-lg`}>
          <h2 className="text-3xl font-bold mb-2">{core.name}</h2>
          <p className="text-gray-300 mb-4">{core.description}</p>
          <div className="flex items-center gap-4">
            <span className={`px-3 py-1 rounded-full text-sm bg-${core.color}-600`}>
              {core.status}
            </span>
            <span className="text-2xl font-mono">
              {(data?.confidence * 100).toFixed(1)}% Confidence
            </span>
          </div>
        </div>

        {/* Core Functions */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="font-bold mb-3">Core Functions</h3>
          <div className="grid grid-cols-1 gap-2">
            {core.functions.map((func, idx) => {
              const functionKey = `${selectedCore}-${func}`;
              const isExecuting = executingFunctions.has(functionKey);
              
              return (
                <div key={idx} className="flex justify-between items-center p-3 bg-gray-700 rounded">
                  <span>{func}</span>
                  <button 
                    className={`px-3 py-1 rounded text-sm transition ${
                      isExecuting 
                        ? 'bg-gray-600 cursor-not-allowed' 
                        : 'bg-cyan-600 hover:bg-cyan-500'
                    }`}
                    onClick={() => !isExecuting && executeCoreFunction(selectedCore, func)}
                    disabled={isExecuting}
                  >
                    {isExecuting ? 'Executing...' : 'Execute'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Core Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-2">Performance</h3>
            <div className="space-y-2 text-sm">
              <div>Response Time: 45ms</div>
              <div>Memory Usage: 2.3GB</div>
              <div>CPU Usage: 67%</div>
            </div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-2">Activity Log</h3>
            <ActivityLogs coreId={selectedCore} />
          </div>
        </div>

        {/* Core Controls */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="font-bold mb-3">Advanced Controls</h3>
          <div className="grid grid-cols-3 gap-3">
            <button className="bg-yellow-600 hover:bg-yellow-500 p-2 rounded font-bold text-sm transition">
              ⚙️ Configure
            </button>
            <button className="bg-orange-600 hover:bg-orange-500 p-2 rounded font-bold text-sm transition">
              🔄 Restart
            </button>
            <button className="bg-red-600 hover:bg-red-500 p-2 rounded font-bold text-sm transition">
              🛑 Shutdown
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      {/* Real-time Metrics Charts */}
      <div className="grid grid-cols-2 gap-4">
        <MetricsChart title="CPU Usage (%)" color="#00ffcc" />
        <MetricsChart title="Memory Usage (%)" color="#aa00ff" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <MetricsChart title="Network I/O (Mbps)" color="#ffaa00" />
        <MetricsChart title="Response Time (ms)" color="#00ff88" />
      </div>

      {/* Performance Metrics */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-2">Core Performance</h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-400">STT Latency</div>
            <div className="text-2xl font-mono">{councilState?.performance?.stt_latency?.toFixed(3) || 0}s</div>
          </div>
          <div>
            <div className="text-gray-400">TTS Latency</div>
            <div className="text-2xl font-mono">{councilState?.performance?.tts_latency?.toFixed(3) || 0}s</div>
          </div>
          <div>
            <div className="text-gray-400">Cache Hit Rate</div>
            <div className="text-2xl font-mono">{Math.round((councilState?.performance?.cache_hit_rate || 0) * 100)}%</div>
          </div>
        </div>
      </div>

      {/* Memory Matrix */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-2">Memory Matrix</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-3xl font-mono">{councilState?.memory_entries || 0}</div>
            <div className="text-sm text-gray-400">Total Entries</div>
          </div>
          <div>
            <div className="text-3xl font-mono">94.2%</div>
            <div className="text-sm text-gray-400">Memory Efficiency</div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-3">System Health</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span>Overall Health</span>
            <span className="font-mono text-green-400">98.7%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-green-500 h-2 rounded-full" style={{width: '98.7%'}}></div>
          </div>

          <div className="flex justify-between">
            <span>Error Rate</span>
            <span className="font-mono text-yellow-400">0.3%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-yellow-500 h-2 rounded-full" style={{width: '0.3%'}}></div>
          </div>

          <div className="flex justify-between">
            <span>Uptime</span>
            <span className="font-mono text-cyan-400">99.9%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-cyan-500 h-2 rounded-full" style={{width: '99.9%'}}></div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-6">
      {/* Council Configuration */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-3">Council Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Update Frequency</label>
            <select className="w-full bg-gray-700 p-2 rounded">
              <option>Real-time (1Hz)</option>
              <option>High (0.5Hz)</option>
              <option>Medium (0.2Hz)</option>
              <option>Low (0.1Hz)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1">Confidence Threshold</label>
            <input type="range" min="0" max="1" step="0.1" defaultValue="0.7"
                   className="w-full" />
            <div className="text-xs text-gray-400 mt-1">Current: 70%</div>
          </div>
        </div>
      </div>

      {/* Core Settings */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-3">Individual Core Settings</h3>
        <div className="space-y-3">
          {Object.entries(coreDetails).map(([coreId, core]) => (
            <div key={coreId} className="flex justify-between items-center p-3 bg-gray-700 rounded">
              <div>
                <div className="font-bold">{core.name}</div>
                <div className="text-sm text-gray-400">{core.description}</div>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 rounded text-sm">
                  Configure
                </button>
                <button className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-sm">
                  Reset
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Actions */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="font-bold mb-3 text-red-400">System Actions</h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="bg-red-600 hover:bg-red-500 p-3 rounded font-bold transition">
            🔄 Full System Reset
          </button>
          <button className="bg-yellow-600 hover:bg-yellow-500 p-3 rounded font-bold transition">
            💾 Backup Data
          </button>
          <button className="bg-purple-600 hover:bg-purple-500 p-3 rounded font-bold transition">
            📤 Export Logs
          </button>
          <button className="bg-blue-600 hover:bg-blue-500 p-3 rounded font-bold transition">
            🔧 Maintenance Mode
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Monitoring Orb (always visible) */}
      <MonitoringOrb
        onPermissionRequest={handlePermissionRequest}
        onHelpRequest={handleHelpRequest}
        isActive={helpActive}
      />

      {/* Notifications Panel */}
      <NotificationsPanel />

      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex flex-col items-center">
          <div className="flex items-center gap-4 mb-2">
            <img src="/CALILOGO128.png" alt="Cali Logo" className="w-8 h-8 rounded-full" />
            <h1 className="text-2xl font-bold">Core 4 Council Dashboard</h1>
          </div>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-1 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'cores', label: 'Cores', icon: '🧠' },
            { id: 'performance', label: 'Performance', icon: '⚡' },
            { id: 'settings', label: 'Settings', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-t-lg font-bold transition ${
                activeTab === tab.id
                  ? 'bg-gray-700 text-cyan-400'
                  : 'bg-gray-800 hover:bg-gray-700'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'cores' && renderCoresTab()}
        {activeTab === 'performance' && renderPerformanceTab()}
        {activeTab === 'settings' && renderSettingsTab()}
      </div>

      {/* Screen Preview (when permissions granted) */}
      {previewUrl && (
        <div className="fixed bottom-20 right-20 bg-gray-800 p-4 rounded-lg shadow-xl w-96">
          <h3 className="font-bold mb-2 text-yellow-400">Screen Preview</h3>
          <video src={previewUrl} autoPlay muted className="w-full rounded border border-gray-600" />
        </div>
      )}

      {/* Voice Commands Log */}
      {helpActive && (
        <div className="fixed bottom-20 left-6 bg-gray-800 p-4 rounded-lg shadow-xl w-80">
          <h3 className="font-bold mb-2 text-green-400">Active Help Session</h3>
          <div className="text-sm text-gray-300 space-y-1">
            <div>🎤 Microphone: Listening</div>
            <div>📹 Screen: Monitoring</div>
            <div>🧠 Council: Analyzing</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;