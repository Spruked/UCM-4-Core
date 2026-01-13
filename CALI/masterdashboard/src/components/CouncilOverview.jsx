import React from 'react';
import CoreOrb from './CoreOrb';

// Hard-coded mock data
const mockCores = {
  ucm_core: { confidence: 0.92 },
  kaygee: { confidence: 0.85 },
  caleon: { confidence: 0.89 },
  cali_x: { confidence: 0.93 },
};

const CouncilOverview = () => {
  return (
    <div className="glass-card relative h-screen w-full">
      <h1 className="text-4xl font-bold text-neon-cyan text-center pt-8 tracking-widest">
        DIAGNOSTIC: FORCE ORB RENDER
      </h1>

      {/* Force 4 orbs in fixed positions */}
      <div className="absolute top-1/4 left-1/4">
        <CoreOrb coreId="ucm_core" data={mockCores.ucm_core} />
      </div>
      <div className="absolute top-3/4 left-3/4">
        <CoreOrb coreId="kaygee" data={mockCores.kaygee} />
      </div>
      <div className="absolute top-3/4 left-1/4">
        <CoreOrb coreId="caleon" data={mockCores.caleon} />
      </div>
      <div className="absolute top-1/4 left-3/4">
        <CoreOrb coreId="cali_x" data={mockCores.cali_x} />
      </div>

      <div className="absolute bottom-8 left-0 right-0 text-center text-neon-cyan">
        If you see 4 glowing orbs → CoreOrb works.<br/>
        If not → CoreOrb has error.
      </div>
    </div>
  );
};

export default CouncilOverview;