// src/components/FloatingOrb.jsx - Optimized with Lerp
import React, { useState, useEffect, useRef, useCallback } from 'react';
import './FloatingOrb.css';

const FloatingOrb = ({ workerId = "CALI_UNIT_01" }) => {
  const [position, setPosition] = useState({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
  const [targetPos, setTargetPos] = useState({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
  const [isMoving, setIsMoving] = useState(false);
  const [animationMode, setAnimationMode] = useState('idle'); // idle, avoiding, assisting, learning

  // Refs for animation loop
  const positionRef = useRef(position);
  const targetRef = useRef(targetPos);
  const lerpFactorRef = useRef(0.05); // Smoothness factor (learnable!)
  const frameCountRef = useRef(0);

  // Connect to UCM backend
  const wsRef = useRef(null);

  useEffect(() => {
    positionRef.current = position;
  }, [position]);

  useEffect(() => {
    targetRef.current = targetPos;
  }, [targetPos]);

  // ✅ SAFE: Listen for cursor movement (not screen capture)
  useEffect(() => {
    const handleMouseMove = (e) => {
      // Update target position based on cursor
      const cursorX = e.clientX;
      const cursorY = e.clientY;

      // Calculate avoidance vector
      const dx = cursorX - positionRef.current.x;
      const dy = cursorY - positionRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      const avoidanceDistance = 350; // pixels

      if (distance < avoidanceDistance) {
        // Cursor is too close - calculate avoidance target
        const angle = Math.atan2(dy, dx);
        const avoidDistance = avoidanceDistance * 1.3; // Extra buffer

        let newTargetX = cursorX + Math.cos(angle) * avoidDistance;
        let newTargetY = cursorY + Math.sin(angle) * avoidDistance;

        // Clamp to viewport
        newTargetX = Math.max(50, Math.min(window.innerWidth - 50, newTargetX));
        newTargetY = Math.max(50, Math.min(window.innerHeight - 50, newTargetY));

        setTargetPos({ x: newTargetX, y: newTargetY });
        setIsMoving(true);
        setAnimationMode('avoiding');

        // Send movement pattern to SKG for learning
        if (frameCountRef.current % 30 === 0) { // Sample every 30 frames
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
              action: 'learn_movement',
              pattern: {
                from: positionRef.current,
                to: { x: newTargetX, y: newTargetY },
                cursor_distance: distance,
                velocity: lerpFactorRef.current,
                timestamp: Date.now()
              }
            }));
          }
        }
      } else if (distance > avoidanceDistance * 1.5) {
        // Cursor is far away - gentle floating behavior
        const time = Date.now() * 0.001; // Convert to seconds
        const floatRadius = 100;
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;

        // Gentle floating motion
        const floatX = centerX + Math.sin(time * 0.5) * floatRadius;
        const floatY = centerY + Math.cos(time * 0.3) * floatRadius * 0.5;

        setTargetPos({ x: floatX, y: floatY });
        setAnimationMode('idle');
      }

      frameCountRef.current++;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Initialize floating motion
  useEffect(() => {
    // Start with gentle floating motion
    const time = Date.now() * 0.001;
    const floatRadius = 100;
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;

    const floatX = centerX + Math.sin(time * 0.5) * floatRadius;
    const floatY = centerY + Math.cos(time * 0.3) * floatRadius * 0.5;

    setTargetPos({ x: floatX, y: floatY });
    setAnimationMode('idle');
    console.log('🎈 Initialized floating motion');
  }, []);

  // 🎮 LERP ANIMATION LOOP
  useEffect(() => {
    let rafId;

    const lerp = (start, end, factor) => {
      return start + (end - start) * factor;
    };

    const animate = () => {
      const current = positionRef.current;
      const target = targetRef.current;

      // Dynamic lerp factor based on animation mode
      let factor = lerpFactorRef.current;
      if (animationMode === 'avoiding') factor = 0.15; // Faster avoidance
      if (animationMode === 'assisting') factor = 0.08; // Slower, intentional movement

      const newX = lerp(current.x, target.x, factor);
      const newY = lerp(current.y, target.y, factor);

      // Check if movement is complete (within 5px)
      const distanceToTarget = Math.sqrt(
        (target.x - newX) ** 2 + (target.y - newY) ** 2
      );

      if (distanceToTarget < 5) {
        setIsMoving(false);
        if (animationMode === 'avoiding') {
          setAnimationMode('idle');
        }
      } else {
        setIsMoving(true);
      }

      // Only update position if there's actual movement
      if (Math.abs(newX - current.x) > 0.1 || Math.abs(newY - current.y) > 0.1) {
        setPosition({ x: newX, y: newY });
      }

      rafId = requestAnimationFrame(animate);
    };

    console.log('🎮 Starting animation loop');
    rafId = requestAnimationFrame(animate);
    return () => {
      console.log('🛑 Stopping animation loop');
      cancelAnimationFrame(rafId);
    };
  }, [animationMode]);

  // WebSocket connection to UCM for SKG learning
  useEffect(() => {
    console.log('🔌 Attempting to connect to orb server...');

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/ws/orb/${workerId}`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('✅ Orb connected to UCM SKG server');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('📨 Received WS message:', data);

            // Update lerp factor based on learned preferences
            if (data.type === 'lerp_optimization') {
              lerpFactorRef.current = data.optimal_velocity;
              console.log('🎯 Updated lerp factor:', lerpFactorRef.current);
            }

            // ECM-driven drift target (e.g., user prefers orb on right side)
            if (data.type === 'drift_preference') {
              const { preferred_quadrant } = data;
              const centerX = window.innerWidth / 2;
              const centerY = window.innerHeight / 2;

              const quadrantTargets = {
                'top_left': { x: centerX - 200, y: centerY - 200 },
                'top_right': { x: centerX + 200, y: centerY - 200 },
                'bottom_left': { x: centerX - 200, y: centerY + 200 },
                'bottom_right': { x: centerX + 200, y: centerY + 200 },
                'center': { x: centerX, y: centerY }
              };

              const newTarget = quadrantTargets[preferred_quadrant] || quadrantTargets['center'];
              setTargetPos(newTarget);
              console.log('🎯 Updated drift target:', newTarget);
            }
          } catch (error) {
            console.error('❌ Error parsing WS message:', error);
          }
        };

        ws.onclose = (event) => {
          console.log('🔌 WebSocket closed:', event.code, event.reason);
          // Attempt to reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };

      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        // Retry connection
        setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [workerId]);

  const handleOrbClick = async () => {
    setAnimationMode('assisting');

    // User explicitly clicked orb - VOLUNTARY interaction
    wsRef.current?.send(JSON.stringify({
      action: 'voluntary_interaction',
      type: 'orb_click',
      timestamp: Date.now()
    }));

    // Query mode
    setTimeout(() => setAnimationMode('idle'), 2000);
  };

  return (
    <>
      {/* ... orb component ... */}
      <div
        className={`floating-orb ${animationMode}`}
        style={{
          position: 'fixed',
          left: `${position.x - 75}px`,
          top: `${position.y - 75}px`,
          transform: `scale(${isMoving ? 1.05 : 1})`,
          transition: 'transform 0.1s ease-out'
        }}
        onClick={handleOrbClick}
      >
        <div className="orb-visual">
          <div className={`orb-core ${animationMode}`} />
          <div className={`orb-aura ${animationMode}`} />
        </div>
      </div>
      <PerformanceHUD />
    </>
  );
};

// 📡 FRONTEND PERFORMANCE INDICATORS
const PerformanceHUD = () => {
  const [metrics, setMetrics] = useState({
    skg_latency: 0,
    memory_usage: 0,
    fragmentation: 0,
    edge_cutter: false
  });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/orb/performance');
        const data = await response.json();

        setMetrics({
          skg_latency: data.metrics.query_latency_ms.toFixed(0),
          memory_usage: data.metrics.memory_usage_mb.toFixed(0),
          fragmentation: (data.metrics.fragmentation_ratio * 100).toFixed(0),
          edge_cutter: data.health_status === 'degraded'
        });

        // Visual indication of edge cutter mode
        if (data.health_status === 'degraded') {
          document.body.style.border = '2px solid #F5A623'; // Orange border
        } else {
          document.body.style.border = 'none';
        }
      } catch (error) {
        // Fallback if server not available
        setMetrics({
          skg_latency: 'N/A',
          memory_usage: 'N/A',
          fragmentation: 'N/A',
          edge_cutter: false
        });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="performance-hud" style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.8)',
      color: metrics.edge_cutter ? '#F5A623' : '#50E3C2',
      padding: '10px',
      borderRadius: '4px',
      fontSize: '12px',
      zIndex: 999999,
      fontFamily: 'monospace'
    }}>
      <div>SKG Latency: {metrics.skg_latency}ms</div>
      <div>Memory: {metrics.memory_usage}MB</div>
      <div>Fragmentation: {metrics.fragmentation}%</div>
      {metrics.edge_cutter && <div style={{color: '#F5A623'}}>⚡ EDGE CUTTER ACTIVE</div>}
    </div>
  );
};

export default FloatingOrb;