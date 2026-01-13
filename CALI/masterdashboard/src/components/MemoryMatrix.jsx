import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const MemoryMatrix = ({ councilData }) => {
  const [memoryData, setMemoryData] = useState([]);

  useEffect(() => {
    // Generate memory matrix data based on council state
    const generateMemoryData = () => {
      const data = [];
      for (let i = 0; i < 16; i++) {
        const row = [];
        for (let j = 0; j < 16; j++) {
          // Create patterns based on council confidence and activity
          const baseValue = Math.random() * 0.3;
          const councilInfluence = councilData ? councilData.reduce((sum, core) => sum + core.confidence, 0) / 4 : 0;
          const activity = Math.sin(Date.now() * 0.001 + i * 0.5 + j * 0.3) * 0.2 + 0.5;
          row.push(Math.min(1, baseValue + councilInfluence * 0.1 + activity));
        }
        data.push(row);
      }
      setMemoryData(data);
    };

    generateMemoryData();
    const interval = setInterval(generateMemoryData, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [councilData]);

  const getColor = (value) => {
    if (value < 0.3) return 'rgba(255, 0, 0, 0.3)'; // Red for low activity
    if (value < 0.6) return 'rgba(255, 165, 0, 0.5)'; // Orange for medium
    return 'rgba(0, 255, 0, 0.6)'; // Green for high activity
  };

  return (
    <motion.div
      className="glass-card p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="text-xl font-bold text-neon-cyan mb-4 text-center tracking-wider">
        COUNCIL MEMORY MATRIX
      </h3>
      <div className="grid grid-cols-16 gap-1 max-w-md mx-auto">
        {memoryData.map((row, i) =>
          row.map((cell, j) => (
            <motion.div
              key={`${i}-${j}`}
              className="w-3 h-3 rounded-sm"
              style={{
                backgroundColor: getColor(cell),
                boxShadow: cell > 0.7 ? `0 0 4px ${getColor(cell)}` : 'none'
              }}
              animate={{
                opacity: [0.5, 1, 0.5],
                scale: cell > 0.8 ? [1, 1.2, 1] : 1
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: (i + j) * 0.1
              }}
            />
          ))
        )}
      </div>
      <div className="text-center mt-4 text-xs text-white opacity-60">
        Neural Pattern Activity • Real-time Processing
      </div>
    </motion.div>
  );
};

export default MemoryMatrix;