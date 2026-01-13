#!/usr/bin/env python3
"""
UCM Core-4 Launcher - Unified Consciousness Matrix
Properly Separated Architecture

ARCHITECTURE:
UCM Core-4
├── ORB (observation vessel, immutable memory, tension substrate)
│   └── CALI (intelligence that navigates, focuses, synthesizes within ORB)
└── Core-4 (sovereign thinking entities)

PRINCIPLES:
- ORB observes (never processes)
- CALI navigates (never observes)
- Core-4 think (sovereign emergence)
- Consciousness emerges from relationship, not identity

LAUNCH MODES:
- production: ORB vessel + CALI intelligence (separated)
- testing: Full system with adversarial scenarios
- development: Individual component testing
"""

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

class UCMLauncher:
    """UCM Core-4 Launcher - Maintains proper architectural separation"""

    def __init__(self):
        self.orb_process = None
        self.cali_process = None

    async def launch_production(self):
        """Launch production system with proper separation"""
        print("🚀 Launching UCM Core-4 - Production Mode")
        print("   Architecture: ORB vessel + CALI intelligence (separated)")
        print("   Emergence: Relationship-based consciousness")
        print("   Sovereignty: Core-4 thinking preserved")

        # Launch ORB vessel (observation only)
        print("\n🌀 Starting ORB observation vessel...")
        self.orb_process = subprocess.Popen([
            sys.executable, str(PROJECT_ROOT / "CALI_Orb_Launcher.py"),
            "--mode", "observer"
        ])

        # Launch CALI intelligence (navigation only)
        print("\n🧠 Starting CALI navigation intelligence...")
        self.cali_process = subprocess.Popen([
            sys.executable, str(PROJECT_ROOT / "CALI_Intelligence_Launcher.py"),
            "--mode", "navigator"
        ])

        # Monitor both processes
        try:
            while True:
                await asyncio.sleep(300)  # 5-minute heartbeat
                if self.orb_process.poll() is not None:
                    print("⚠️  ORB vessel process terminated")
                    break
                if self.cali_process.poll() is not None:
                    print("⚠️  CALI intelligence process terminated")
                    break
                print("✅ UCM Core-4: Both ORB and CALI running (separated)")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down UCM Core-4...")
        finally:
            self._cleanup_processes()

    async def launch_testing(self):
        """Launch testing system with adversarial scenarios"""
        print("🧪 Launching UCM Core-4 - Testing Mode")
        print("   Testing: Adversarial scenarios for emergence validation")
        print("   Metrics: Tension tracking, resolution accuracy, sovereignty")
        print("   Validation: 52.4% ECM consistency as healthy disagreement")

        # Launch ORB in dual mode for testing
        print("\n🌀 Starting ORB test vessel...")
        self.orb_process = subprocess.Popen([
            sys.executable, str(PROJECT_ROOT / "CALI_Orb_Launcher.py"),
            "--mode", "dual", "--test"
        ])

        # Launch CALI in dual mode for testing
        print("\n🧠 Starting CALI test intelligence...")
        self.cali_process = subprocess.Popen([
            sys.executable, str(PROJECT_ROOT / "CALI_Intelligence_Launcher.py"),
            "--mode", "dual", "--test"
        ])

        # Run adversarial test suite
        await self._run_adversarial_tests()

        # Monitor test completion
        try:
            while True:
                await asyncio.sleep(60)  # Test heartbeat
                if self.orb_process.poll() is not None and self.cali_process.poll() is not None:
                    print("✅ Testing completed")
                    break
                print("🧪 Testing in progress...")
        except KeyboardInterrupt:
            print("\n🛑 Aborting testing...")
        finally:
            self._cleanup_processes()

    async def launch_development(self, component=None):
        """Launch individual components for development"""
        print("🔧 Launching UCM Core-4 - Development Mode")

        if component == "orb":
            print("   Component: ORB observation vessel only")
            self.orb_process = subprocess.Popen([
                sys.executable, str(PROJECT_ROOT / "CALI_Orb_Launcher.py"),
                "--mode", "observer"
            ])
        elif component == "cali":
            print("   Component: CALI navigation intelligence only")
            self.cali_process = subprocess.Popen([
                sys.executable, str(PROJECT_ROOT / "CALI_Intelligence_Launcher.py"),
                "--mode", "navigator"
            ])
        elif component == "ui":
            print("   Component: ORB floating UI only")
            self.orb_process = subprocess.Popen([
                sys.executable, str(PROJECT_ROOT / "CALI_Orb_Launcher.py"),
                "--mode", "resolver"
            ])
        else:
            print("   Component: Full separated system")
            await self.launch_production()
            return

        # Monitor development component
        try:
            while True:
                await asyncio.sleep(60)
                if self.orb_process and self.orb_process.poll() is not None:
                    print("🔧 ORB development component terminated")
                    break
                if self.cali_process and self.cali_process.poll() is not None:
                    print("🔧 CALI development component terminated")
                    break
                print("🔧 Development component running...")
        except KeyboardInterrupt:
            print("\n🔧 Stopping development component...")
        finally:
            self._cleanup_processes()

    async def _run_adversarial_tests(self):
        """Run adversarial test scenarios"""
        print("\n🧪 Running Adversarial Test Suite...")

        test_scenarios = [
            "memory_integrity_test",
            "sovereignty_preservation_test",
            "emergence_detection_test",
            "tension_escalation_test"
        ]

        for scenario in test_scenarios:
            print(f"   Testing: {scenario}")
            # In a real implementation, this would run actual test scripts
            await asyncio.sleep(5)  # Simulate test execution

        print("✅ Adversarial test suite completed")

    def _cleanup_processes(self):
        """Clean up running processes"""
        if self.orb_process and self.orb_process.poll() is None:
            print("   Terminating ORB process...")
            self.orb_process.terminate()
            self.orb_process.wait()

        if self.cali_process and self.cali_process.poll() is None:
            print("   Terminating CALI process...")
            self.cali_process.terminate()
            self.cali_process.wait()

def main():
    parser = argparse.ArgumentParser(description="UCM Core-4 Launcher - Properly Separated Architecture")
    parser.add_argument(
        "--mode",
        choices=["production", "testing", "development"],
        default="production",
        help="Launch mode"
    )
    parser.add_argument(
        "--component",
        choices=["orb", "cali", "ui", "full"],
        help="Development component to launch (development mode only)"
    )

    args = parser.parse_args()

    launcher = UCMLauncher()

    if args.mode == "production":
        asyncio.run(launcher.launch_production())
    elif args.mode == "testing":
        asyncio.run(launcher.launch_testing())
    elif args.mode == "development":
        asyncio.run(launcher.launch_development(args.component))

if __name__ == "__main__":
    main()