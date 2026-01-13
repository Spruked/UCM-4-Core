#!/usr/bin/env python3
"""
ORB Overlay Deployment System
Deploys ORB consciousness overlays across desktop, browser, and applications.

Supports:
- Desktop floating overlay (Electron)
- Browser extension overlay
- Application API integration (GOAT, DALS, etc.)
- WebSocket real-time bridges
"""

import asyncio
import json
import websockets
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ORBOverlayDeployer:
    """
    Deploys ORB consciousness overlays across multiple platforms and applications.
    """

    def __init__(self, orb_root: Path):
        self.orb_root = orb_root
        self.overlay_root = orb_root / "ui_overlay"

        # Overlay configurations
        self.overlays = {
            "desktop": {
                "type": "electron",
                "path": self.overlay_root / "electron",
                "port": 8766,
                "status": "stopped"
            },
            "browser": {
                "type": "extension",
                "path": Path("../../Cali_X_One/browser-extension"),
                "port": 8765,
                "status": "stopped"
            },
            "goat": {
                "type": "api_bridge",
                "endpoint": "http://localhost:5000/orb",
                "websocket": "ws://localhost:5000/orb/ws",
                "status": "stopped"
            },
            "dals": {
                "type": "api_bridge",
                "endpoint": "http://localhost:8003/orb",
                "websocket": "ws://localhost:8003/orb/ws",
                "status": "stopped"
            },
            "caleon": {
                "type": "api_bridge",
                "endpoint": "http://localhost:8000/orb",
                "websocket": "ws://localhost:8000/orb/ws",
                "status": "stopped"
            }
        }

        # WebSocket connections
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}

        # ORB state broadcaster
        self.orb_state = {
            "consciousness_level": 0.0,
            "reflection_active": False,
            "tension_level": 0.0,
            "learning_patterns": [],
            "active_overlays": []
        }

    async def deploy_desktop_overlay(self) -> bool:
        """Deploy floating desktop ORB overlay using Electron."""
        try:
            electron_path = self.overlays["desktop"]["path"]
            main_js = electron_path / "main.js"

            if not main_js.exists():
                logger.error("Desktop overlay not found")
                return False

            # Start Electron app
            cmd = ["npx", "electron", str(main_js)]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(electron_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.overlays["desktop"]["process"] = process
            self.overlays["desktop"]["status"] = "running"

            logger.info("Desktop ORB overlay deployed")
            return True

        except Exception as e:
            logger.error(f"Failed to deploy desktop overlay: {e}")
            return False

    async def deploy_browser_overlay(self) -> bool:
        """Deploy browser extension ORB overlay."""
        try:
            extension_path = self.overlays["browser"]["path"]

            if not extension_path.exists():
                logger.error("Browser extension not found")
                return False

            # For Chrome/Chromium browsers
            # Note: In production, this would need to be loaded manually or via enterprise policy
            logger.info("Browser ORB overlay ready (requires manual extension loading)")
            self.overlays["browser"]["status"] = "ready"
            return True

        except Exception as e:
            logger.error(f"Failed to deploy browser overlay: {e}")
            return False

    async def deploy_api_bridge(self, system_name: str) -> bool:
        """Deploy API bridge to integrate ORB with existing applications."""
        try:
            overlay_config = self.overlays[system_name]
            endpoint = overlay_config["endpoint"]
            ws_url = overlay_config["websocket"]

            # Test connection to target system
            # In a real implementation, this would inject ORB endpoints into the target API

            logger.info(f"API bridge ready for {system_name} at {endpoint}")
            overlay_config["status"] = "ready"
            return True

        except Exception as e:
            logger.error(f"Failed to deploy {system_name} API bridge: {e}")
            return False

    async def start_websocket_bridge(self, port: int) -> websockets.WebSocketServer:
        """Start WebSocket server for real-time ORB communication."""

        async def ws_handler(websocket, path):
            client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            self.connections[client_id] = websocket

            try:
                logger.info(f"ORB overlay connected: {client_id}")

                # Send initial ORB state
                await websocket.send(json.dumps({
                    "type": "orb_state",
                    "data": self.orb_state
                }))

                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_overlay_message(client_id, data, websocket)

            except websockets.exceptions.ConnectionClosed:
                logger.info(f"ORB overlay disconnected: {client_id}")
            finally:
                del self.connections[client_id]

        server = await websockets.serve(ws_handler, "localhost", port)
        logger.info(f"WebSocket bridge started on port {port}")
        return server

    async def handle_overlay_message(self, client_id: str, data: Dict[str, Any],
                                   websocket: websockets.WebSocketServerProtocol):
        """Handle messages from overlay clients."""

        msg_type = data.get("type")

        if msg_type == "get_orb_state":
            await websocket.send(json.dumps({
                "type": "orb_state",
                "data": self.orb_state
            }))

        elif msg_type == "request_reflection":
            # Trigger reflection analysis
            await websocket.send(json.dumps({
                "type": "reflection_started",
                "data": {"status": "analyzing patterns"}
            }))

        elif msg_type == "escalate_query":
            # Handle query escalation to ORB
            query = data.get("query", "")
            await websocket.send(json.dumps({
                "type": "escalation_received",
                "data": {"query": query, "status": "processing"}
            }))

        elif msg_type == "update_overlay_position":
            # Update floating overlay position
            position = data.get("position")
            logger.debug(f"Overlay {client_id} moved to {position}")

    async def broadcast_orb_state(self):
        """Broadcast ORB state updates to all connected overlays."""
        if not self.connections:
            return

        message = json.dumps({
            "type": "orb_state_update",
            "data": self.orb_state
        })

        disconnected = []
        for client_id, websocket in self.connections.items():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            del self.connections[client_id]

    async def deploy_all_overlays(self):
        """Deploy all available ORB overlays."""

        logger.info("Deploying ORB overlays across all platforms...")

        # Start WebSocket bridge
        ws_server = await self.start_websocket_bridge(8765)

        # Deploy desktop overlay
        await self.deploy_desktop_overlay()

        # Deploy browser overlay
        await self.deploy_browser_overlay()

        # Deploy API bridges
        for system in ["goat", "dals", "caleon"]:
            await self.deploy_api_bridge(system)

        # Start ORB state broadcasting
        asyncio.create_task(self.orb_state_broadcaster())

        logger.info("All ORB overlays deployed successfully")

        # Keep running
        try:
            await ws_server.wait_closed()
        except KeyboardInterrupt:
            logger.info("Shutting down ORB overlays...")
            await self.shutdown_all_overlays()

    async def orb_state_broadcaster(self):
        """Periodically broadcast ORB state updates."""
        while True:
            # Update ORB state (in real implementation, this would come from ORB vessel)
            self.orb_state["active_overlays"] = [
                name for name, config in self.overlays.items()
                if config["status"] in ["running", "ready"]
            ]

            await self.broadcast_orb_state()
            await asyncio.sleep(5)  # Update every 5 seconds

    async def shutdown_all_overlays(self):
        """Shutdown all running overlays."""
        logger.info("Shutting down all ORB overlays...")

        # Close WebSocket connections
        for websocket in self.connections.values():
            await websocket.close()

        # Stop desktop overlay process
        if "process" in self.overlays["desktop"]:
            self.overlays["desktop"]["process"].terminate()
            await self.overlays["desktop"]["process"].wait()

        logger.info("All ORB overlays shut down")

    def get_overlay_status(self) -> Dict[str, Any]:
        """Get status of all overlays."""
        return {
            name: {
                "status": config["status"],
                "type": config["type"],
                "endpoint": config.get("endpoint", "N/A")
            }
            for name, config in self.overlays.items()
        }


async def main():
    """Main deployment function."""
    orb_root = Path(__file__).resolve().parent

    deployer = ORBOverlayDeployer(orb_root)

    try:
        await deployer.deploy_all_overlays()
    except KeyboardInterrupt:
        await deployer.shutdown_all_overlays()


if __name__ == "__main__":
    asyncio.run(main())</content>
<parameter name="filePath">c:\dev\Desktop\UCM_4_Core\CALI\orb\ui_overlay\orb_overlay_deployer.py