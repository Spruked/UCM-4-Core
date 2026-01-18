#!/usr/bin/env python3
"""
ORB Overlay Deployment Launcher
Launches ORB consciousness overlays across all platforms and applications.
"""

import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ORBOverlayLauncher:
    """Launches ORB overlays across different platforms."""

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[3]  # UCM_4_Core
        self.cali_root = self.project_root / "CALI"
        self.orb_root = self.cali_root / "orb"
        self.overlay_root = self.orb_root / "ui_overlay"

        # Overlay configurations
        self.overlays = {
            "desktop": {
                "script": self.overlay_root / "electron" / "main.js",
                "type": "electron",
                "description": "Desktop floating ORB overlay"
            },
            "browser": {
                "script": self.overlay_root / "browser_orb_overlay.js",
                "type": "extension",
                "description": "Browser extension ORB overlay"
            },
            "api_bridge": {
                "script": self.overlay_root / "orb_api_bridge.py",
                "type": "api",
                "description": "API bridge for GOAT/DALS/Caleon integration"
            },
            "deployer": {
                "script": self.overlay_root / "orb_overlay_deployer.py",
                "type": "deployer",
                "description": "Master overlay deployer"
            }
        }

    def show_available_overlays(self):
        """Show information about available overlays."""
        logger.info("🎯 Available ORB Overlay Platforms:")
        for name, config in self.overlays.items():
            logger.info(f"  {name}: {config['description']}")
            logger.info(f"    Type: {config['type']}")
            logger.info(f"    Script: {config['script']}")
            logger.info("")

def main():
    """Main launcher function."""
    import argparse

    parser = argparse.ArgumentParser(description="ORB Overlay Launcher")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available overlay platforms"
    )

    args = parser.parse_args()

    launcher = ORBOverlayLauncher()

    if args.list:
        launcher.show_available_overlays()
        return

    logger.info("ORB Overlay Launcher ready. Use --list to see available overlays.")

if __name__ == "__main__":
    main()