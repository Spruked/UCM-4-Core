import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MonitoringOrb = ({ onPermissionRequest, onHelpRequest, isActive, onActionExecute }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasPermissions, setHasPermissions] = useState({
    screen: false,
    browser: false,
    microphone: false
  });
  const [helpMode, setHelpMode] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionTarget, setExecutionTarget] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [orbPos, setOrbPos] = useState({ x: window.innerWidth - 100, y: window.innerHeight - 100 });
  const [isDragging, setIsDragging] = useState(false);
  const orbRef = useRef(null);

  // Voice orb features
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [orbWs, setOrbWs] = useState(null);
  const [lastTranscription, setLastTranscription] = useState('');
  const [orbPulse, setOrbPulse] = useState({ isActive: false, intensity: 0, action: null });
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);

  // Check permissions on mount
  useEffect(() => {
    checkExistingPermissions();
  }, []);

  // Mouse tracking for repulsion field
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    const handleMouseDown = () => {
      setIsDragging(true);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  // Autonomous floating behavior like KayGee orb
  useEffect(() => {
    if (isDragging || isExpanded) return;

    let animationFrame;
    let lastCursor = { x: mousePos.x, y: mousePos.y };
    let targetPos = { ...orbPos };

    const animate = () => {
      const cursorPos = { x: mousePos.x, y: mousePos.y };
      const currentPos = { ...orbPos };

      // Calculate optimal distance from cursor (learned behavior simulation)
      const optimalDistance = 200; // Distance to maintain from cursor
      const confidence = 0.8; // Confidence in learned behavior

      // Compute distance from cursor
      const dx = cursorPos.x - currentPos.x;
      const dy = cursorPos.y - currentPos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      let finalX, finalY;

      if (distance < optimalDistance * 0.8) {
        // Too close - move away
        const angle = Math.atan2(dy, dx);
        finalX = cursorPos.x - Math.cos(angle) * optimalDistance;
        finalY = cursorPos.y - Math.sin(angle) * optimalDistance;
      } else if (distance > optimalDistance * 1.2) {
        // Too far - move closer
        const angle = Math.atan2(dy, dx);
        finalX = cursorPos.x - Math.cos(angle) * optimalDistance;
        finalY = cursorPos.y - Math.sin(angle) * optimalDistance;
      } else {
        // Good distance - maintain position with slight drift
        finalX = currentPos.x + (Math.random() - 0.5) * 4; // Increased drift for more movement
        finalY = currentPos.y + (Math.random() - 0.5) * 4;
      }

      // Keep within screen bounds
      finalX = Math.max(50, Math.min(window.innerWidth - 100, finalX));
      finalY = Math.max(50, Math.min(window.innerHeight - 100, finalY));

      // Smooth interpolation - increased speed for more visible movement
      const lerpAlpha = 0.05; // Increased from 0.02 for more responsive movement
      const maxStep = 8; // Smaller steps for smoother motion
      const newX = currentPos.x + (finalX - currentPos.x) * lerpAlpha;
      const newY = currentPos.y + (finalY - currentPos.y) * lerpAlpha;

      setOrbPos({ x: newX, y: newY });
      targetPos = { x: finalX, y: finalY };

      lastCursor = cursorPos;
      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [mousePos, isDragging, isExpanded, orbPos]);

  // Voice orb WebSocket connection (optional - falls back to mock)
  useEffect(() => {
    const connectOrbWs = () => {
      try {
        const ws = new WebSocket('ws://localhost:8000/ws/orb/master_dashboard');

        ws.onopen = () => {
          console.log('Connected to CALI Floating Orb server');
          setOrbWs(ws);
        };

        ws.onmessage = async (event) => {
          try {
            // Handle both binary audio and JSON data
            if (typeof event.data === 'string') {
              const payload = JSON.parse(event.data);

              if (payload.type === 'PULSE') {
                // Handle Pulse events for UI synchronization
                console.log('Pulse event:', payload.event, 'intensity:', payload.intensity);
                setOrbPulse({
                  isActive: payload.event !== 'speech_end' && payload.event !== 'listening_end',
                  intensity: payload.intensity,
                  action: payload.event
                });

                // Update listening/speaking states based on pulse
                if (payload.event === 'listening_start') {
                  setIsListening(true);
                } else if (payload.event === 'speech_start') {
                  setIsListening(false);
                  setIsSpeaking(true);
                } else if (payload.event === 'speech_end') {
                  setIsSpeaking(false);
                }

              } else if (payload.type === 'transcription') {
                setLastTranscription(payload.data.text);
                setIsListening(false);
                console.log('Orb transcription:', payload.data);

              } else if (payload.type === 'complete') {
                setIsSpeaking(false);
                console.log('Speech synthesis complete');

              } else if (payload.type === 'error') {
                console.error('Orb error:', payload.message);
                setIsListening(false);
                setIsSpeaking(false);
              }

            } else if (event.data instanceof Blob) {
              // Handle audio playback
              try {
                const arrayBuffer = await event.data.arrayBuffer();
                const audioContext = new AudioContext();
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                const source = audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(audioContext.destination);
                source.start(0);
              } catch (audioError) {
                console.error('Audio playback error:', audioError);
              }
            }
          } catch (err) {
            console.error('Error parsing orb message:', err);
          }
        };

        ws.onclose = () => {
          console.log('Orb WebSocket disconnected - using mock mode');
          setOrbWs(null);
          setIsListening(false);
          setIsSpeaking(false);
          setOrbPulse({ isActive: false, intensity: 0, action: null });
        };

        ws.onerror = (err) => {
          console.log('Orb WebSocket not available - using mock mode');
          setOrbWs(null);
        };
      } catch (err) {
        console.log('Orb server not available - using mock voice functionality');
        setOrbWs(null);
      }
    };

    // Try to connect, but don't require it
    connectOrbWs();
  }, []);

  const checkExistingPermissions = async () => {
    try {
      // Check screen capture permission
      const screenPerm = await navigator.permissions.query({ name: 'display-capture' });
      setHasPermissions(prev => ({ ...prev, screen: screenPerm.state === 'granted' }));
    } catch (e) {
      console.log('Screen permission check failed:', e);
    }

    // Check microphone
    try {
      const micPerm = await navigator.permissions.query({ name: 'microphone' });
      setHasPermissions(prev => ({ ...prev, microphone: micPerm.state === 'granted' }));
    } catch (e) {
      console.log('Mic permission check failed:', e);
    }
  };

  const requestPermissions = async () => {
    try {
      // Request screen capture
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: 'always' },
        audio: false
      });
      setHasPermissions(prev => ({ ...prev, screen: true }));
      onPermissionRequest('screen', stream);
    } catch (err) {
      console.error('Screen permission denied:', err);
      alert('Screen permission required for assistance. Please allow when prompted.');
    }

    // Request microphone for voice help
    try {
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasPermissions(prev => ({ ...prev, microphone: true }));
      onPermissionRequest('microphone', micStream);
    } catch (err) {
      console.error('Microphone permission denied:', err);
    }

    // Request browser tab access (Chrome Extension API if available)
    if (chrome && chrome.tabs) {
      setHasPermissions(prev => ({ ...prev, browser: true }));
      onPermissionRequest('browser', null);
    }
  };

  const executeCaliAction = async (intent, data) => {
    setIsExecuting(true);
    setExecutionTarget(intent);

    try {
      if (intent === 'SEARCH' || intent === 'INPUT') {
        // For web page interaction, we need to communicate with the active tab
        // This would typically be done via a browser extension
        if (window.chrome && window.chrome.tabs) {
          // Get active tab
          const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

          if (tab) {
            // Inject script to find and interact with input field
            await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              function: (text) => {
                const target = document.querySelector('input[type="text"], input[type="search"], textarea');
                if (target) {
                  // Move visual indicator (if we had one)
                  // For now, just type the text
                  let i = 0;
                  const typeInterval = setInterval(() => {
                    target.value += text[i];
                    i++;
                    if (i >= text.length) {
                      clearInterval(typeInterval);
                      // Submit if it's a search
                      if (target.type === 'search' || target.form) {
                        target.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
                      }
                    }
                  }, 50);
                }
              },
              args: [data.text]
            });
          }
        } else {
          // Fallback for non-extension environment - simulate typing
          console.log('Simulating action:', intent, data);
          // In a real implementation, this would use desktop automation APIs
        }
      }

      // Notify parent component
      if (onActionExecute) {
        onActionExecute(intent, data);
      }
    } catch (error) {
      console.error('Action execution failed:', error);
    } finally {
      setTimeout(() => {
        setIsExecuting(false);
        setExecutionTarget(null);
      }, 2000);
    }
  };

  // Voice functions (real WebSocket when available, mock fallback)
  const startListening = async () => {
    if (orbWs && orbWs.readyState === WebSocket.OPEN) {
      // Use real orb server
      console.log('🎤 Starting real voice listening...');
      setIsListening(true);
      orbWs.send(JSON.stringify({ action: 'listen' }));
    } else {
      // Mock fallback
      console.log('🎤 Starting mock voice listening...');
      setIsListening(true);
      setTimeout(() => {
        setIsListening(false);
        setLastTranscription('Hello CALI, how can I assist you today?');
        console.log('🎤 Mock voice listening complete');
      }, 3000);
    }
  };

  const speakText = (text, emotion = 'neutral') => {
    if (orbWs && orbWs.readyState === WebSocket.OPEN) {
      // Use real orb server
      console.log(`🗣️ Speaking via orb server: "${text}" with emotion: ${emotion}`);
      setIsSpeaking(true);
      orbWs.send(JSON.stringify({
        action: 'speak',
        text: text,
        emotion: emotion
      }));
    } else {
      // Mock fallback
      console.log(`🔊 Mock speaking: "${text}" with emotion: ${emotion}`);
      setIsSpeaking(true);
      setTimeout(() => {
        setIsSpeaking(false);
        console.log('🔊 Mock speech complete');
      }, 2000);
    }
  };

  return (
    <div
      className="fixed z-50"
      style={{
        left: orbPos.x,
        top: orbPos.y,
        transition: isDragging ? 'none' : 'all 0.3s ease-out'
      }}
    >
      {/* Floating Orb */}
      <motion.div
        ref={orbRef}
        className="relative w-16 h-16 rounded-full shadow-lg cursor-pointer overflow-hidden"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsExpanded(!isExpanded)}
        animate={{
          boxShadow: isListening
            ? '0 0 40px rgba(239, 68, 68, 0.9)' // Red glow when listening
            : isSpeaking
            ? '0 0 40px rgba(34, 197, 94, 0.9)' // Green glow when speaking
            : orbPulse.isActive
            ? `0 0 ${40 + orbPulse.intensity * 20}px rgba(34, 211, 238, ${0.6 + orbPulse.intensity * 0.4})` // Pulse glow
            : isActive || isExecuting
            ? '0 0 30px rgba(34, 211, 238, 0.8)' // Cyan glow when active/executing
            : '0 0 10px rgba(34, 211, 238, 0.4)' // Default cyan glow
        }}
        drag
        dragMomentum={false}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={() => setIsDragging(false)}
      >
        <img
          src="/CALILOGO128.png"
          alt="Cali Logo"
          className="w-full h-full object-contain"
        />

        {/* Activity indicator */}
        {(isActive || isExecuting) && (
          <motion.div
            className="absolute -top-1 -right-1 w-4 h-4 rounded-full"
            animate={{
              backgroundColor: isExecuting ? '#f59e0b' : '#ffff00',
              scale: [1, 1.5, 1]
            }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}

        {/* Voice indicators */}
        {isListening && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-red-500"
            animate={{ scale: [1, 1.1, 1], opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 0.6, repeat: Infinity }}
          />
        )}

        {isSpeaking && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-green-500"
            animate={{ scale: [1, 1.1, 1], opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 0.6, repeat: Infinity }}
          />
        )}

        {/* Execution indicator */}
        {isExecuting && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-amber-400"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 0.8, repeat: Infinity }}
          />
        )}
      </motion.div>

      {/* Expanded Menu */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="absolute bottom-20 right-0 bg-gray-800 rounded-lg p-4 shadow-xl w-72"
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.8 }}
          >
            <h3 className="text-cyan-400 font-bold mb-3">CALI Interface Controls</h3>

            {/* Execution Status */}
            {isExecuting && (
              <div className="mb-4 p-2 bg-amber-900/50 border border-amber-600 rounded">
                <div className="text-amber-400 text-sm font-bold">EXECUTING ACTION</div>
                <div className="text-amber-300 text-xs">{executionTarget}</div>
              </div>
            )}

            {/* Permissions Status */}
            <div className="mb-4">
              <div className="text-sm mb-2">Permissions:</div>
              {Object.entries(hasPermissions).map(([key, granted]) => (
                <div key={key} className="flex justify-between text-xs mb-1">
                  <span className="capitalize">{key}:</span>
                  <span className={granted ? 'text-green-400' : 'text-red-400'}>
                    {granted ? '✓ Granted' : '✗ Denied'}
                  </span>
                </div>
              ))}
            </div>

            {/* Voice Controls */}
            <div className="mb-4">
              <div className="text-sm mb-2">Voice Interface:</div>
              <div className="flex gap-2 mb-2">
                <button
                  onClick={startListening}
                  disabled={isListening || !orbWs}
                  className={`flex-1 py-2 rounded font-bold transition ${
                    isListening
                      ? 'bg-red-600 text-white'
                      : 'bg-red-500 hover:bg-red-400 text-white disabled:opacity-50'
                  }`}
                >
                  {isListening ? '🎤 Listening...' : '🎤 Listen'}
                </button>
                <button
                  onClick={() => speakText('Hello, I am CALI. How can I assist you?')}
                  disabled={isSpeaking || !orbWs}
                  className={`flex-1 py-2 rounded font-bold transition ${
                    isSpeaking
                      ? 'bg-green-600 text-white'
                      : 'bg-green-500 hover:bg-green-400 text-white disabled:opacity-50'
                  }`}
                >
                  {isSpeaking ? '🔊 Speaking...' : '🔊 Speak'}
                </button>
              </div>
              {lastTranscription && (
                <div className="text-xs text-cyan-300 bg-gray-900 p-2 rounded">
                  Last: "{lastTranscription}"
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="mb-4">
              <button
                onClick={requestPermissions}
                className="w-full bg-cyan-400 text-black py-2 rounded mb-2 font-bold hover:bg-cyan-300 transition"
              >
                Request All Permissions
              </button>

              <button
                onClick={() => executeCaliAction('SEARCH', { text: 'Hello CALI' })}
                className="w-full bg-amber-600 text-white py-2 rounded mb-2 font-bold hover:bg-amber-500 transition"
                disabled={!hasPermissions.browser || isExecuting}
              >
                Test Search Action
              </button>
            </div>

            <button
              onClick={toggleHelpMode}
              className={`w-full py-2 rounded font-bold transition ${
                helpMode
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-700 hover:bg-gray-600 text-white'
              }`}
            >
              {helpMode ? '✓ Help Active' : 'Activate Help Mode'}
            </button>

            {/* Help Mode Instructions */}
            {helpMode && (
              <div className="mt-3 p-2 bg-gray-900 rounded text-xs text-gray-300">
                <div>📹 Screen is being monitored</div>
                <div>🎤 Voice commands enabled</div>
                <div>💻 Web interaction ready</div>
                <div>📢 Say "CALI, search for [query]" to trigger</div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MonitoringOrb;