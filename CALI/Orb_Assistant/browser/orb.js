import React, { useEffect, useRef, useState } from 'https://esm.sh/react@18';
import { createRoot } from 'https://esm.sh/react-dom@18/client';

const colorForHealth = (h) => {
  if (h >= 0.8) return '#2dd4ff';
  if (h >= 0.6) return '#facc15';
  return '#f87171';
};

const resolveBridgeUrl = (fallbackUrl) => {
  if (typeof window === 'undefined') return fallbackUrl;
  const plugin = window.UCM_4_Core;
  if (plugin && (plugin.bridgeUrl || plugin.ws)) {
    return plugin.bridgeUrl || plugin.ws;
  }
  return fallbackUrl;
};

function OrbSurface({ bridgeUrl = 'ws://localhost:8765' }) {
  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const [resolvedBridgeUrl, setResolvedBridgeUrl] = useState(bridgeUrl);
  const [health, setHealth] = useState(1.0);
  const [status, setStatus] = useState('Connecting to CALI...');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lastText, setLastText] = useState('');
  const [permissions, setPermissions] = useState({
    desktop: true,
    browser: true,
    voice: true,
    listening: true,
  });

  const speak = (text) => {
    if (!('speechSynthesis' in window)) return;
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

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(resolvedBridgeUrl);
        wsRef.current = ws;
        ws.onopen = () => {
          setStatus(
            resolvedBridgeUrl !== bridgeUrl ? 'UCM_4_Core linked via plugin bridge' : 'Orb linked to CALI'
          );
          setIsListening(true);
          ws.send(JSON.stringify({ type: 'orb_status_request' }));
        };
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'cali_status') {
              const h = msg.data?.health ?? 1.0;
              setHealth(h);
              setStatus('Cognition online');
            } else if (msg.type === 'query_result') {
              const text = msg.data?.text || msg.data?.state?.text || 'Response received';
              setLastText(text);
              setHealth(msg.data?.confidence ?? health);
              if ((msg.data?.confidence ?? 0) > 0.75) speak(text);
            } else if (msg.type === 'status_response') {
              const h = msg.data?.health_score ?? 1.0;
              setHealth(h);
              setStatus(`Orb healthy (${(h * 100).toFixed(0)}%)`);
            }
          } catch (err) {
            console.error('Orb parse error', err);
          }
        };
        ws.onclose = () => {
          setStatus('Bridge disconnected – retrying...');
          setIsListening(false);
          retryRef.current = setTimeout(connect, 2000);
        };
        ws.onerror = (err) => {
          console.error('Bridge error', err);
          ws.close();
        };
      } catch (err) {
        console.error('Bridge connection failed', err);
        retryRef.current = setTimeout(connect, 3000);
      }
    };

    connect();
    return () => {
      if (retryRef.current) clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [bridgeUrl, resolvedBridgeUrl]);

  const handleClick = () => {
    const text = window.prompt('Ask CALI:', lastText || '');
    if (!text) return;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'orb_query', text, core: 'kaygee' }));
      setStatus('Query dispatched...');
    }
  };

  const togglePermission = (key) => {
    setPermissions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const color = colorForHealth(health);
  const coreClasses = ['orb-core'];
  if (isListening) coreClasses.push('listening');
  if (isSpeaking) coreClasses.push('speaking');

  return (
    <div className="orb-container" onClick={handleClick} title="Click to ask CALI">
      <div className={coreClasses.join(' ')} style={{ color }}>
        <div className="orb-glow" style={{ background: color }} />
        <div className="orb-rings">
          <span />
          <span />
          <span />
        </div>
      </div>
      <div className="orb-status">
        <strong>{(health * 100).toFixed(0)}%</strong>
        <span>{status}</span>
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
}

const root = createRoot(document.getElementById('root'));
root.render(<OrbSurface />);
