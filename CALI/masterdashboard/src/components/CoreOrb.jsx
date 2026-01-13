import React from 'react';
import { motion } from 'framer-motion';

const config = {
  ucm_core: { name: "UCM_Core_ECM", color: "from-blue-500 to-indigo-900", glow: "#00aaff" },
  kaygee: { name: "KayGee 1.0", color: "from-purple-500 to-pink-900", glow: "#aa00ff" },
  caleon: { name: "Caleon Genesis", color: "from-cyan-400 to-teal-800", glow: "#00ffcc" },
  cali_x: { name: "Cali_X_One", color: "from-amber-400 to-orange-800", glow: "#ffaa00" },
};

const CoreOrb = ({ coreId, data = { confidence: 0.8 } }) => {
  const c = config[coreId];
  const confidence = data.confidence || 0.8;

  return (
    <motion.div
      className="relative w-40 h-40"
      animate={{ rotate: 360 }}
      transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
    >
      {/* Main orb */}
      <motion.div
        className={`w-full h-full rounded-full bg-gradient-to-br ${c.color} shadow-2xl flex flex-col items-center justify-center text-white border-6 border-white border-opacity-40`}
        whileHover={{ scale: 1.15, boxShadow: `0 0 80px ${c.glow}` }}
        animate={{
          boxShadow: [
            `0 0 30px ${c.glow}`,
            `0 0 60px ${c.glow}`,
            `0 0 30px ${c.glow}`
          ]
        }}
        transition={{ duration: 3 + confidence * 2, repeat: Infinity }}
      >
        <div className="text-xs uppercase tracking-widest opacity-80">{c.name}</div>
        <div className="text-3xl font-bold mt-2">{Math.round(confidence * 100)}%</div>
        <div className="text-xs mt-1 animate-pulse">ACTIVE</div>
      </motion.div>
    </motion.div>
  );
};

export default CoreOrb;