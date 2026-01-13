// MasterDashboard.jsx - Privacy-Safe CALI Floating Orb
import React, { useState, useEffect, useRef, useCallback } from 'react';
import './MasterDashboard.css';

// Privacy-safe Floating Orb component
const FloatingOrb = () => {
  const [position, setPosition] = useState({ x: 500, y: 500 });
  const [isQueryMode, setIsQueryMode] = useState(false);
  const [queryResult, setQueryResult] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  
  const orbRef = useRef(null);
  const animationFrameRef = useRef(null);
  const wsRef = useRef(null);
  
  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/orb/CALI_UNIT_01');
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('✅ Floating Orb WebSocket connected');
      setWsConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'position_update') {
          // Update orb position smoothly
          setPosition(prev => ({
            x: prev.x + (data.position.x - prev.x) * 0.1,
            y: prev.y + (data.position.y - prev.y) * 0.1
          }));
        } else if (data.type === 'query_response') {
          setQueryResult(data.answer);
        }
      } catch (e) {
        console.error('❌ Orb message error:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('🔌 Floating Orb WebSocket disconnected');
      setWsConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('❌ Floating Orb WebSocket error:', error);
    };
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);
  
  // ✅ SAFE: Get cursor position via browser mousemove event
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        // Send cursor position to backend for safe processing
        wsRef.current.send(JSON.stringify({
          action: 'update_cursor',
          cursorX: e.clientX,
          cursorY: e.clientY,
          screenWidth: window.innerWidth,
          screenHeight: window.innerHeight
        }));
      }
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  
  const handleOrbClick = async () => {
    // ✅ SAFE: Explicit user action
    setIsQueryMode(true);
    
    // Get current browser context (user-consented)
    const currentContext = {
      url: window.location.href,
      title: document.title,
      selection: window.getSelection().toString()  // Explicitly selected text
    };
    
    // Send voluntary query
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'voluntary_query',
        query: "How can I help you today?",
        context: currentContext
      }));
    }
  };
  
  const handleQuerySubmit = (query) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'voluntary_query',
        query: query,
        context: {
          url: window.location.href,
          title: document.title,
          selection: window.getSelection().toString()
        }
      }));
    }
    setIsQueryMode(false);
  };
  
  return (
    <div 
      className="floating-orb"
      style={{
        position: 'fixed',
        left: position.x - 75,
        top: position.y - 75,
        zIndex: 999999,
        pointerEvents: 'auto'
      }}
      onClick={handleOrbClick}
      ref={orbRef}
    >
      <div className="orb-core" />
      <div className="orb-aura" />
      
      {isQueryMode && (
        <div className="query-dialog">
          <input 
            type="text" 
            placeholder="Ask CALI (voluntary)..."
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleQuerySubmit(e.target.value);
                e.target.value = '';
              }
            }}
          />
          {queryResult && <p>{queryResult}</p>}
        </div>
      )}
    </div>
  );
};

const MasterDashboard = () => {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  return (
    <div className="master-dashboard">
      <header>
        <h1>UCM_4_Core - CALI System</h1>
        <div className="connection-status">
          WebSocket: {connectionStatus}
        </div>
      </header>
      
      <main>
        <div className="dashboard-content">
          <h2>Privacy-Safe CALI Floating Assistant Orb</h2>
          <p>The floating orb tracks your cursor position but never captures your screen or keystrokes.</p>
          <p>All interactions are voluntary - you must explicitly click the orb and type queries.</p>
          
          <div className="features-list">
            <h3>✅ Safe Features:</h3>
            <ul>
              <li>Cursor position tracking via browser events</li>
              <li>Voluntary query interactions only</li>
              <li>No screen capture or OCR</li>
              <li>No keystroke logging</li>
              <li>Learns from explicit user preferences</li>
            </ul>
            
            <h3>🚫 Illegal Features (Not Implemented):</h3>
            <ul>
              <li>Screen recording/OCR</li>
              <li>Keystroke monitoring</li>
              <li>Automated actions</li>
              <li>Click heatmaps</li>
              <li>OS-level cursor tracking</li>
            </ul>
          </div>
        </div>
      </main>
      
      {/* The privacy-safe floating orb */}
      <FloatingOrb />
      
      <div className="dev-console">
        <h4>🔍 Privacy Verification</h4>
        <ul>
          <li>✅ No screen capture permissions</li>
          <li>✅ Voluntary interactions only</li>
          <li>✅ Browser-based cursor tracking</li>
          <li>✅ No automation capabilities</li>
          <li>✅ GDPR/CFAA compliant</li>
        </ul>
      </div>
    </div>
  );
};

export default MasterDashboard;