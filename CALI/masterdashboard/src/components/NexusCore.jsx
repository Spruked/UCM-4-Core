import React from 'react';
import { motion } from 'framer-motion';

const NexusCore = ({ telemetry, className = "", executionMode = false, currentAction = null }) => {
  if (!telemetry) {
    return (
      <div className={`w-full h-full flex items-center justify-center ${className}`}>
        <div className="text-center">
          <div className="text-4xl mb-4">🔄</div>
          <div className="text-slate-400">Waiting for telemetry data...</div>
          <div className="text-xs text-slate-500 mt-2">Backend connection required</div>
        </div>
      </div>
    );
  }

  const cores = telemetry.cores || {};
  const attention = telemetry.attention || {};
  const system = telemetry.system || {};

  // Calculate positions for cores around the circle
  const corePositions = [
    { name: 'ucm_core', angle: 315, color: '#06b6d4' }, // Cyan - Top-left
    { name: 'kaygee', angle: 45, color: '#a855f7' },   // Purple - Top-right
    { name: 'caleon', angle: 135, color: '#10b981' },  // Green - Bottom-right
    { name: 'cali_x', angle: 225, color: '#f59e0b' }   // Amber - Bottom-left
  ];

  const getCorePosition = (angle, radius = 120) => {
    const radian = (angle * Math.PI) / 180;
    return {
      x: Math.cos(radian) * radius,
      y: Math.sin(radian) * radius
    };
  };

  const TraceLine = ({ core, isActive, latency, color, isExecuting }) => {
    const startPos = getCorePosition(core.angle);
    const endPos = { x: 0, y: 0 }; // Center (CALI Nexus)

    // Create SVG path from core to center
    const pathData = `M ${startPos.x + 160} ${startPos.y + 160} L ${endPos.x + 160} ${endPos.y + 160}`;

    // Pulse speed based on latency (lower latency = faster pulse)
    const pulseDuration = Math.max(1, Math.min(4, latency * 5));

    return (
      <g>
        {/* Static trace line */}
        <motion.path
          d={pathData}
          stroke={isActive || isExecuting ? color : '#374151'}
          strokeWidth={isActive || isExecuting ? "4" : "2"}
          fill="transparent"
          initial={{ pathLength: 0 }}
          animate={{
            pathLength: 1,
            stroke: isExecuting ? '#f59e0b' : color // Gold color for execution
          }}
          transition={{
            duration: 2,
            ease: "easeInOut",
            stroke: { duration: 0.3 }
          }}
          opacity={isActive || isExecuting ? 0.9 : 0.3}
        />

        {/* Animated pulse dot */}
        {isActive && (
          <motion.circle
            r="4"
            fill={color}
            animate={{
              offsetDistance: ["0%", "100%"],
              opacity: [0, 1, 0]
            }}
            transition={{
              offsetDistance: { duration: pulseDuration, repeat: Infinity, ease: "linear" },
              opacity: { duration: pulseDuration, repeat: Infinity }
            }}
            style={{
              offsetPath: `path('${pathData}')`
            }}
          />
        )}

        {/* Data flow particles */}
        {isActive && (
          <>
            <motion.circle
              r="2"
              fill={color}
              animate={{
                offsetDistance: ["0%", "100%"],
                opacity: [0, 0.8, 0]
              }}
              transition={{
                offsetDistance: { duration: pulseDuration * 0.7, repeat: Infinity, delay: 0.2 },
                opacity: { duration: pulseDuration * 0.7, repeat: Infinity, delay: 0.2 }
              }}
              style={{
                offsetPath: `path('${pathData}')`
              }}
            />
            <motion.circle
              r="1.5"
              fill={color}
              animate={{
                offsetDistance: ["0%", "100%"],
                opacity: [0, 0.6, 0]
              }}
              transition={{
                offsetDistance: { duration: pulseDuration * 0.5, repeat: Infinity, delay: 0.4 },
                opacity: { duration: pulseDuration * 0.5, repeat: Infinity, delay: 0.4 }
              }}
              style={{
                offsetPath: `path('${pathData}')`
              }}
            />
          </>
        )}
      </g>
    );
  };

  return (
    <div className={`relative bg-slate-900/50 rounded-xl p-6 border border-slate-700 ${className}`}>
      <h2 className="text-xl font-bold text-cyan-400 mb-6 text-center tracking-wider">
        CALI NEXUS // COGNITIVE CONVERGENCE
      </h2>

      {/* Circuit Board Container */}
      <div className="relative w-80 h-80 mx-auto">
        <svg
          viewBox="0 0 320 320"
          className="absolute inset-0 w-full h-full"
        >
          {/* Background circuit pattern */}
          <defs>
            <pattern id="circuit" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="10" cy="10" r="1" fill="#374151" opacity="0.3"/>
              <line x1="10" y1="10" x2="20" y2="10" stroke="#374151" strokeWidth="0.5" opacity="0.2"/>
              <line x1="10" y1="10" x2="10" y2="20" stroke="#374151" strokeWidth="0.5" opacity="0.2"/>
            </pattern>
          </defs>
          <rect width="320" height="320" fill="url(#circuit)" />

          {/* Trace lines from cores to center */}
          {corePositions.map((core) => {
            const coreData = cores[core.name];
            const isActive = attention.active_core === core.name;
            const isExecuting = executionMode && (core.name === 'cali_x' || core.name === 'kaygee');
            const latency = coreData?.latency || 0.5;

            return (
              <TraceLine
                key={core.name}
                core={core}
                isActive={isActive}
                isExecuting={isExecuting}
                latency={latency}
                color={core.color}
              />
            );
          })}
        </svg>

        {/* Core Modules (Peripheral) */}
        {corePositions.map((core) => {
          const coreData = cores[core.name];
          const position = getCorePosition(core.angle);
          const isActive = attention.active_core === core.name;

          return (
            <motion.div
              key={core.name}
              className="absolute w-16 h-16 rounded-lg border-2 flex flex-col items-center justify-center text-xs font-bold"
              style={{
                left: `${160 + position.x - 32}px`,
                top: `${160 + position.y - 32}px`,
                borderColor: core.color,
                backgroundColor: isActive ? `${core.color}20` : '#1e293b80',
                boxShadow: isActive ? `0 0 20px ${core.color}60` : 'none'
              }}
              animate={isActive ? {
                scale: [1, 1.1, 1],
                boxShadow: [`0 0 20px ${core.color}60`, `0 0 30px ${core.color}80`, `0 0 20px ${core.color}60`]
              } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="text-center">
                <div style={{ color: core.color }}>
                  {(coreData?.confidence * 100 || 0).toFixed(0)}%
                </div>
                <div className="text-slate-400 text-[10px] mt-1">
                  {core.name.replace('_', ' ').toUpperCase()}
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Central CALI Nexus */}
        <motion.div
          className="absolute w-20 h-20 rounded-full border-4 flex items-center justify-center overflow-hidden bg-cyan-500/20"
          style={{
            left: '120px',
            top: '120px',
            borderColor: '#06b6d4',
            background: 'radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(6,182,212,0.1) 70%, rgba(6,182,212,0.05) 100%)'
          }}
          animate={{
            boxShadow: [
              '0 0 30px rgba(6,182,212,0.6)',
              '0 0 50px rgba(6,182,212,0.9)',
              '0 0 30px rgba(6,182,212,0.6)'
            ],
            scale: attention.phase_coherence ? [1, 1 + attention.phase_coherence * 0.1, 1] : 1
          }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <img
            src="/CALILOGO128.png"
            alt="CALI Nexus"
            className="w-12 h-12 object-contain"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div className="w-12 h-12 flex items-center justify-center text-cyan-400 font-bold text-lg" style={{ display: 'none' }}>
            CALI
          </div>

          {/* Coherence indicator */}
          <motion.div
            className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-cyan-400 rounded-full"
            animate={{
              scaleX: attention.phase_coherence || 0,
              opacity: attention.phase_coherence || 0
            }}
            style={{ transformOrigin: 'left' }}
          />
        </motion.div>
      </div>

      {/* Convergence Metrics */}
      <div className="mt-6 grid grid-cols-2 gap-4 text-center">
        <div className="bg-slate-800/50 p-3 rounded-lg">
          <div className="text-xs text-slate-400">PHASE COHERENCE</div>
          <div className="text-lg font-bold text-cyan-400">
            {(attention.phase_coherence * 100 || 0).toFixed(1)}%
          </div>
        </div>
        <div className="bg-slate-800/50 p-3 rounded-lg">
          <div className="text-xs text-slate-400">META CONFIDENCE</div>
          <div className="text-lg font-bold text-purple-400">
            {(attention.meta_confidence * 100 || 0).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Current Activity */}
      <div className="mt-4 p-3 bg-slate-800/30 rounded-lg">
        <div className="text-xs text-slate-400 mb-1">CURRENT ACTIVITY</div>
        <div className="text-sm text-cyan-300 font-mono">
          {attention.active_core ?
            `${attention.active_core.replace('_', ' ').toUpperCase()} leading convergence...` :
            'System initializing...'
          }
        </div>
      </div>
    </div>
  );
};

export default NexusCore;