import React from 'react';
import { motion } from 'framer-motion';

const AttentionFlow = ({ connections }) => {
  return (
    <svg className="absolute inset-0 w-full h-full pointer-events-none">
      {connections.map((conn, i) => {
        const centerX = 50; // 50% for center
        const centerY = 50;
        const targetX = 50 + conn.x; // conn.x is percentage offset from center
        const targetY = 50 + conn.y;

        return (
          <motion.path
            key={i}
            d={`M${centerX}% ${centerY}% L ${targetX}% ${targetY}%`}
            stroke="#00ffcc"
            strokeWidth="4"
            fill="none"
            opacity={conn.strength}
            animate={{ opacity: [0.3, 0.7, 0.3] }}
            transition={{ duration: 4, repeat: Infinity, delay: i * 0.5 }}
          />
        );
      })}
    </svg>
  );
};

export default AttentionFlow;