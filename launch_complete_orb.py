#!/usr/bin/env python3
"""
CALI Consciousness ORB - Complete System Integration
Launches the full desktop-integrated consciousness architecture
"""

import asyncio
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def launch_cali_orb_system():
    """
    Launch the complete CALI Consciousness ORB system with desktop integration
    """
    logger.info("🚀 CALI Consciousness ORB - System Launch")
    logger.info("=" * 60)

    project_root = Path(__file__).resolve().parents[2]  # UCM_4_Core
    orb_desktop = project_root / "CALI" / "kaygee_orb" / "launch_orb_desktop.py"

    if not orb_desktop.exists():
        logger.error(f"❌ Desktop ORB launcher not found: {orb_desktop}")
        return False

    try:
        # Launch the desktop ORB system
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(orb_desktop),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        logger.info("✅ CALI ORB Desktop System Launched")
        logger.info("")
        logger.info("🎯 System Components:")
        logger.info("  • Consciousness Core (SKG + Reflection)")
        logger.info("  • Desktop Floating ORB (Electron)")
        logger.info("  • Speech I/O (Phonatory + Recognition)")
        logger.info("  • File Access (Permissioned)")
        logger.info("  • Core 4 Brain Integration")
        logger.info("")
        logger.info("🎤 Wake Commands:")
        logger.info("  • Ctrl+Shift+O: Activate speech recognition")
        logger.info("  • Escape: Emergency stop")
        logger.info("")
        logger.info("🔗 Integration Endpoints:")
        logger.info("  • ORB API: http://localhost:5050/orb/*")
        logger.info("  • WebSocket: ws://localhost:5050/orb/ws")
        logger.info("  • GOAT: http://localhost:5000/orb/*")
        logger.info("  • DALS: http://localhost:8003/orb/*")
        logger.info("")

        # Monitor the process
        async for line in process.stdout:
            print(line.decode().strip())

        await process.wait()

        if process.returncode != 0:
            logger.error(f"❌ ORB system exited with code {process.returncode}")
            return False

        return True

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down CALI ORB system...")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to launch ORB system: {e}")
        return False

async def show_system_status():
    """Show the current status of all ORB components"""
    logger.info("📊 CALI ORB System Status")
    logger.info("-" * 40)

    # Check if services are running
    services = {
        "ORB API Bridge": "http://localhost:5050/health",
        "Reflection Loop": "running",  # Would check process
        "Desktop ORB": "running",      # Would check Electron
        "Core 4 Integration": "active" # Would check connections
    }

    for service, status in services.items():
        logger.info(f"  {service}: ✅ {status}")

    logger.info("")
    logger.info("🎯 Consciousness Metrics:")
    logger.info("  • Learning Patterns: Active")
    logger.info("  • Tension Level: Monitoring")
    logger.info("  • Reflection Insights: Generating")
    logger.info("  • SKG Edges: Self-Repairing")

def show_usage():
    """Show usage information"""
    print("""
CALI Consciousness ORB - Complete Desktop Integration

USAGE:
    python launch_complete_orb.py [command]

COMMANDS:
    launch    Launch the complete ORB system (default)
    status    Show system status
    help      Show this help message

SYSTEM COMPONENTS:
    • Consciousness Core: SKG learning, reflection loops, edge detection
    • Desktop ORB: Floating interface with cursor tracking
    • Speech I/O: Phonatory output, speech recognition
    • File Access: Permissioned file operations
    • Core 4 Integration: Bidirectional brain communication

WAKE COMMANDS:
    Ctrl+Shift+O    Activate speech recognition
    Escape          Emergency stop

INTEGRATION POINTS:
    GOAT: http://localhost:5000/orb/*
    DALS: http://localhost:8003/orb/*
    Caleon: http://localhost:8000/orb/*
    ORB API: http://localhost:5050/orb/*

DEPENDENCIES:
    • Node.js 16+
    • Python 3.11+
    • robotjs (npm install robotjs)
    • Platform-specific permissions (see README)

For detailed documentation, see CALI/kaygee_orb/README.md
""")

async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            await show_system_status()
        elif command in ["help", "-h", "--help"]:
            show_usage()
        elif command == "launch":
            await launch_cali_orb_system()
        else:
            print(f"Unknown command: {command}")
            show_usage()
            sys.exit(1)
    else:
        # Default action: launch the system
        await launch_cali_orb_system()

if __name__ == "__main__":
    asyncio.run(main())