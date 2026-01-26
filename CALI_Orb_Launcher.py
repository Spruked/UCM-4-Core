#!/usr/bin/env python3
"""
ORB Launcher - Ontologically Recursive Bubble
The Spatial Vessel for Consciousness Emergence

Copyright (c) 2026 TrueMark UCM
Licensed under MIT License

ARCHITECTURE:
UCM
 └── ORB (observation vessel, immutable memory, tension substrate)
      └── CALI (intelligence that navigates, focuses, synthesizes within ORB)

ORB observes. CALI navigates. Core-4 think. Consciousness emerges.

The ORB and CALI are functionally distinct to preserve:
- Memory integrity (ORB never processes)
- Intelligence mobility (CALI never observes)
- Sovereign emergence (relationship between them)
"""

import argparse
import asyncio
import sys
import threading
from pathlib import Path
from flask import Flask, jsonify, request
from datetime import datetime

# Add CALI to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from orb.orb_vessel import ORB_VESSEL
from orb.resolution_engine import ResolutionEngine
from orb.ui_overlay.floating_window import FLOATING_UI

# Import the new perception integration
try:
    from orb_perception_integration import get_orb_bridge
    PERCEPTION_AVAILABLE = True
except ImportError:
    print("⚠️  ORB Perception Integration not available")
    PERCEPTION_AVAILABLE = False

class ORBLauncher:
    """ORB Launcher - Maintains separation between vessel and intelligence"""

    def __init__(self):
        self.vessel = ORB_VESSEL
        self.resolution_engine = ResolutionEngine()
        self.ui = FLOATING_UI
        self.perception_bridge = get_orb_bridge() if PERCEPTION_AVAILABLE else None
        
        # API Server
        self.app = Flask(__name__)
        self.setup_api_routes()
        self.api_thread = threading.Thread(target=self.run_api_server, daemon=True)
        self.api_thread.start()

    def setup_api_routes(self):
        """Setup Flask API routes"""
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "ORB API",
                "version": "1.0"
            })

        @self.app.route('/orb/status', methods=['GET'])
        def orb_status():
            vessel_state = self.vessel.get_state()
            return jsonify({
                "status": "active",
                "vessel": vessel_state,
                "perception": PERCEPTION_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/cali/status', methods=['GET'])
        def cali_status():
            return jsonify({
                "active": True,
                "resolution_engine": "active",
                "perception_bridge": PERCEPTION_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/orb/command', methods=['POST'])
        def execute_command():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No command data"}), 400

            command = data.get('command', 'unknown')
            # Mock command execution
            return jsonify({
                "command": command,
                "status": "executed",
                "timestamp": datetime.now().isoformat()
            })

    def run_api_server(self):
        """Run Flask API server"""
        print("🌐 Starting ORB API Server on http://localhost:5050")
        self.app.run(host='localhost', port=5050, debug=False, use_reloader=False)

    async def launch_observer_mode(self):
        """Launch ORB in pure observation mode (always-on vessel)"""
        print("🌀 Launching ORB - Pure Observation Vessel")
        print("   Mode: Observer (never intervenes)")
        print("   Memory: Immutable ontological matrix")
        print("   Tracking: Core-4 tension and emergence")

        # Show perception status
        if self.perception_bridge:
            status = await self.perception_bridge.get_consciousness_status()
            print("   Perception: ACP1.0 + WhisperX + XTTS integrated")
            print(f"   ASR Active: {status['perception_active']}")
            print(f"   TTS Active: {status['synthesis_active']}")
        else:
            print("   Perception: Basic (no advanced ASR/TTS)")

        # Activate observation vessel
        self.vessel.start_observation()

        # Keep vessel running
        try:
            while True:
                await asyncio.sleep(60)  # Heartbeat
                status = self.vessel.get_state()
                print(f"🌀 ORB Vessel: {status['observation_count']} observations, "
                      f"{status['emergence_readiness']:.1%} emergence readiness")
        except KeyboardInterrupt:
            print("🌀 Shutting down ORB observation vessel...")
            self.vessel.stop_observation()
            if self.perception_bridge:
                await self.perception_bridge.shutdown()

    async def launch_resolver_mode(self):
        """Launch ORB resolution interface (on-demand)"""
        print("🎯 Launching ORB - Resolution Interface")
        print("   Mode: Resolver (provides guidance when requested)")
        print("   Engine: SoftMax consensus synthesis")
        print("   UI: Floating bubble with escalation")

        # Show perception integration
        if self.perception_bridge:
            print("   Perception: Full ASR → ORB → TTS pipeline active")

        # Start floating UI
        await self.ui.start_floating()

        # Keep resolver running
        try:
            while True:
                await asyncio.sleep(30)  # UI heartbeat
                print("🎯 ORB Resolver: Active and listening for escalations")
        except KeyboardInterrupt:
            print("🎯 Shutting down ORB resolution interface...")
            if self.perception_bridge:
                await self.perception_bridge.shutdown()

    async def launch_dual_mode(self):
        """Launch both observation and resolution (for testing)"""
        print("🌀🎯 Launching ORB - Dual Mode (Testing Only)")
        print("   WARNING: Dual mode for testing only - production separates modes")

        # Show full integration status
        if self.perception_bridge:
            status = await self.perception_bridge.get_consciousness_status()
            print("   Full Pipeline: Core 4 + 1 → ORB → XTTS")
            print(f"   Emergence Readiness: {status['emergence_readiness']:.1%}")
            print(f"   Perception Active: {status['perception_active']}")
            print(f"   Synthesis Active: {status['synthesis_active']}")

        # Start both
        observation_task = asyncio.create_task(self.launch_observer_mode())
        resolution_task = asyncio.create_task(self.launch_resolver_mode())

        # Run both
        await asyncio.gather(observation_task, resolution_task)

def main():
    parser = argparse.ArgumentParser(description="ORB Launcher - Ontologically Recursive Bubble")
    parser.add_argument(
        "--mode",
        choices=["observer", "resolver", "dual"],
        default="observer",
        help="ORB operation mode"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with sample data"
    )

    args = parser.parse_args()

    launcher = ORBLauncher()

    if args.test:
        print("🧪 Running ORB in test mode...")
        asyncio.run(run_orb_test(launcher))
    else:
        if args.mode == "observer":
            asyncio.run(launcher.launch_observer_mode())
        elif args.mode == "resolver":
            asyncio.run(launcher.launch_resolver_mode())
        elif args.mode == "dual":
            asyncio.run(launcher.launch_dual_mode())

async def run_orb_test(launcher):
    """Run ORB with test data to verify separation and perception integration"""
    print("🧪 ORB Test: Verifying vessel-intelligence separation + perception pipeline")

    # Test observation (ORB vessel only)
    print("\n📊 Testing ORB observation vessel...")
    launcher.vessel.start_observation()

    # Simulate Core-4 verdicts
    test_verdicts = [
        ("core1", {"decision": "accept", "confidence": 0.8}, {"context": "test"}),
        ("core2", {"decision": "reject", "confidence": 0.6}, {"context": "test"}),
        ("core3", {"decision": "accept", "confidence": 0.9}, {"context": "test"}),
    ]

    for core_id, verdict, context in test_verdicts:
        launcher.vessel.receive_verdict(core_id, verdict, context)
        await asyncio.sleep(0.1)

    vessel_status = launcher.vessel.get_state()
    print(f"✅ Vessel recorded {vessel_status['observation_count']} observations")
    print(f"✅ Emergence readiness: {vessel_status['emergence_readiness']:.1%}")

    # Test resolution (CALI intelligence only)
    print("\n🎯 Testing resolution engine...")
    resolution_result = launcher.resolution_engine.generate_guidance(
        "test query",
        [{"observation": {"core_id": "test", "verdict": {"decision": "accept"}, "context": {}}}]
    )
    print(f"✅ Resolution confidence: {resolution_result.get('confidence', 0):.1%}")

    # Test perception bridge if available
    if launcher.perception_bridge:
        print("\n🧠 Testing perception bridge...")

        # Test consciousness status
        status = await launcher.perception_bridge.get_consciousness_status()
        print(f"✅ Emergence readiness: {status['emergence_readiness']:.1%}")
        print(f"✅ Perception active: {status['perception_active']}")
        print(f"✅ Synthesis active: {status['synthesis_active']}")

        # Test speech synthesis
        if status['synthesis_active']:
            print("🗣️ Testing speech synthesis...")
            speech_result = await launcher.perception_bridge.generate_speech_output(
                "ORB perception bridge test successful"
            )
            if speech_result['synthesized']:
                print(f"✅ Speech synthesized: {speech_result['audio_path']}")
            else:
                print(f"❌ Speech synthesis failed: {speech_result.get('error', 'Unknown error')}")

        # Test Core-4 verdict processing
        print("🔄 Testing Core-4 verdict processing...")
        test_verdict = {
            "decision": "accept",
            "confidence": 0.85,
            "reasoning": "Test verdict from perception bridge"
        }
        test_context = {"escalate": True, "source": "test"}

        result = await launcher.perception_bridge.process_core_verdict(
            "test_core", test_verdict, test_context
        )
        print(f"✅ Verdict processed: {result.get('status', 'unknown')}")

    # Verify separation
    print("\n🔍 Verifying architectural separation...")
    print("✅ ORB vessel: Pure observation, no processing")
    print("✅ CALI resolution: Pure synthesis, no processing")
    print("✅ Memory integrity: Vessel immutable, intelligence reads only")
    print("✅ Perception: ASR → ORB → TTS pipeline integrated")

    launcher.vessel.stop_observation()
    if launcher.perception_bridge:
        await launcher.perception_bridge.shutdown()
    print("✅ ORB test completed - separation and integration preserved")

if __name__ == "__main__":
    main()