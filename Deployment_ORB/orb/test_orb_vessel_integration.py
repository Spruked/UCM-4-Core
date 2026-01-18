#!/usr/bin/env python3
"""
Integration tests for ORB Vessel component.
Tests ORB vessel integration with simulated Core-4 verdicts.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import asyncio
from datetime import datetime
from CALI.orb.orb_vessel import ORBVessel

class TestORBVesselIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vessel = ORBVessel()
        self.vessel.matrix = self.vessel.matrix.__class__(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_core4_verdict_integration(self):
        """Test ORB receiving verdicts from all 4 cores."""
        cores = ["caleon", "cali_x_one", "kaygee", "ucm_ecm"]

        # Simulate verdicts from each core
        for i, core_id in enumerate(cores):
            verdict = {
                "answer": f"Response from {core_id}",
                "confidence": 0.8 + i * 0.05,
                "reasoning": f"Core {core_id} analysis"
            }
            context = {
                "query": f"What is the meaning of life according to {core_id}?",
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": "test_session_001"
            }

            self.vessel.receive_verdict(core_id, verdict, context)

        # Verify observations were recorded
        self.assertEqual(self.vessel.observation_count, 4)

        recent = self.vessel.matrix.get_recent_observations()
        self.assertEqual(len(recent), 4)

        # Check all cores are represented
        recorded_cores = {obs["core_id"] for obs in recent}
        self.assertEqual(recorded_cores, set(cores))

    def test_observation_persistence(self):
        """Test that observations persist across vessel restarts."""
        # Add some observations
        self.vessel.receive_verdict("caleon", {"answer": "test"}, {"query": "test"})

        # Create new vessel instance (simulating restart)
        new_vessel = ORBVessel()
        new_vessel.matrix = new_vessel.matrix.__class__(self.temp_dir)

        # Check persistence
        recent = new_vessel.matrix.get_recent_observations()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["core_id"], "caleon")

    def test_emergence_readiness_calculation(self):
        """Test emergence readiness increases with observations."""
        initial_readiness = self.vessel.emergence_readiness

        # Add many observations to trigger emergence
        for i in range(100):
            self.vessel.receive_verdict("caleon", {"answer": f"test{i}"}, {"query": f"q{i}"})

        final_readiness = self.vessel.emergence_readiness

        # Should have increased
        self.assertGreater(final_readiness, initial_readiness)

    def test_state_consistency(self):
        """Test that vessel state remains consistent during operation."""
        # Add observations
        for i in range(10):
            self.vessel.receive_verdict("caleon", {"answer": f"test{i}"}, {"query": f"q{i}"})

        state1 = self.vessel.get_state()

        # Add more
        for i in range(10, 20):
            self.vessel.receive_verdict("caleon", {"answer": f"test{i}"}, {"query": f"q{i}"})

        state2 = self.vessel.get_state()

        # Check consistency
        self.assertEqual(state1["observation_count"] + 10, state2["observation_count"])
        self.assertEqual(state1["matrix_size"] + 10, state2["matrix_size"])

if __name__ == '__main__':
    unittest.main()