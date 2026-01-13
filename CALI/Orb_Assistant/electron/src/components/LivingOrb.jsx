import React, { useEffect, useRef, useState } from 'react';
import './LivingOrb.css';

const colorForHealth = (health) => {
  if (health >= 0.8) return 'var(--orb-color-good)';
  if (health >= 0.6) return 'var(--orb-color-warn)';
  return 'var(--orb-color-bad)';
};

const resolveBridgeUrl = (fallbackUrl) => {
  if (typeof window === 'undefined') return fallbackUrl;
  const plugin = window.UCM_4_Core;
  if (plugin && (plugin.bridgeUrl || plugin.ws)) {
    return plugin.bridgeUrl || plugin.ws;
  }
  return fallbackUrl;
};

const LivingOrb = ({ bridgeUrl = 'ws://localhost:8765' }) => {
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const [resolvedBridgeUrl, setResolvedBridgeUrl] = useState(bridgeUrl);
  const [health, setHealth] = useState(1.0);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [statusLine, setStatusLine] = useState('Connecting to CALI...');
  const [lastText, setLastText] = useState('');
  const [permissions, setPermissions] = useState({
    desktop: true,
    browser: true,
    voice: true,
    listening: true,
  });

  // --- speech synthesis helper ---
  const speak = (text) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.05;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    setResolvedBridgeUrl(resolveBridgeUrl(bridgeUrl));
  }, [bridgeUrl]);

  // --- websocket connection ---
  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(resolvedBridgeUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setStatusLine(
            resolvedBridgeUrl !== bridgeUrl ? 'UCM_4_Core linked via plugin bridge' : 'Orb linked to CALI bridge'
          );
          setIsListening(true);
          ws.send(JSON.stringify({ type: 'orb_status_request' }));
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'cali_status') {
              const healthScore = msg.data?.health ?? 1.0;
              setHealth(healthScore);
              setStatusLine('Cognition online');
            } else if (msg.type === 'query_result') {
              const text = msg.data?.text || msg.data?.state?.text || 'Response received';
              setLastText(text);
              setHealth(msg.data?.confidence ?? health);
              if ((msg.data?.confidence ?? 0) > 0.75) {
                speak(text);
              }
            } else if (msg.type === 'status_response') {
              const h = msg.data?.health_score ?? 1.0;
              setHealth(h);
              setStatusLine(`Orb healthy (${(h * 100).toFixed(0)}%)`);
            }
          } catch (err) {
            console.error('Orb parse error:', err);
          }
        };

        ws.onclose = () => {
          setStatusLine('Bridge disconnected – retrying...');
          setIsListening(false);
          reconnectRef.current = setTimeout(connect, 2000);
        };

        ws.onerror = (err) => {
          console.error('Bridge error:', err);
          ws.close();
        };
      } catch (err) {
        console.error('Bridge connection failed:', err);
        reconnectRef.current = setTimeout(connect, 3000);
      }
    };

    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [bridgeUrl, resolvedBridgeUrl]);

  const handleClick = () => {
    const promptText = window.prompt('Ask CALI:', lastText || '');
    if (!promptText) return;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'orb_query', text: promptText, core: 'kaygee' }));
      setStatusLine('Query dispatched...');
    }
  };

  const togglePermission = (key) => {
    setPermissions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const color = colorForHealth(health);
  const coreClasses = ['living-orb-core'];
  if (isListening) coreClasses.push('listening');
  if (isSpeaking) coreClasses.push('speaking');

  return (
    <div className="living-orb-shell" onClick={handleClick} title="Click to ask CALI">
      <div className={coreClasses.join(' ')} style={{ color }}>
        <div className="living-orb-glow" style={{ background: color }} />
        <div className="living-orb-rings">
          <span />
          <span />
          <span />
        </div>
        <div className="living-orb-surface" />
      </div>
      <div className="living-orb-status">
        <strong>{(health * 100).toFixed(0)}%</strong>
        <span>{statusLine}</span>
      </div>
      <div className="permission-toggles" onClick={(e) => e.stopPropagation()}>
        {[
          ['desktop', 'Desktop'],
          ['browser', 'Browser'],
          ['voice', 'Voice'],
          ['listening', 'Listening'],
        ].map(([key, label]) => (
          <div
            key={key}
            className={`permission-toggle ${permissions[key] ? 'on' : 'off'}`}
            onClick={() => togglePermission(key)}
            title={`${label} permission: ${permissions[key] ? 'on' : 'off'}`}
          >
            <span className="dot" />
            <span>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LivingOrb;
