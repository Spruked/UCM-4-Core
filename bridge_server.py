#!/usr/bin/env python3
"""
CALI WebSocket Bridge Server
Connects headless CALI cores and the HLSF orb to Electron/Browser orb surfaces.
"""

import asyncio
import contextlib
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, Set

import websockets
from websockets.server import WebSocketServerProtocol

PROJECT_ROOT = Path(__file__).parent.resolve()
# Ensure CALI modules are importable when running from repo root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "CALI") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "CALI"))

from CALI.cali_state_hub import _get_state_hub  # type: ignore
from CALI.orb import OntologicallyRecursiveBubble  # Unified ORB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BRIDGE] %(message)s")
logger = logging.getLogger(__name__)


class CALIBridgeServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.state_hub = _get_state_hub()
        self.orb = OntologicallyRecursiveBubble(repo_root=str(PROJECT_ROOT))
        # Activate ORB for bridge operations
        self.orb.activate()

        self.connections: Set[WebSocketServerProtocol] = set()
        self.is_running = False

    async def register_connection(self, websocket: WebSocketServerProtocol):
        self.connections.add(websocket)
        logger.info(f"Orb surface connected (total: {len(self.connections)})")
        await self.send_ready(websocket)
        await self.broadcast_status()

    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        self.connections.discard(websocket)
        logger.info(f"Orb surface disconnected (total: {len(self.connections)})")

    async def send_ready(self, websocket: WebSocketServerProtocol):
        ready = {
            "type": "bridge_ready",
            "status": "headless_orb_active",
            "health": self.orb.health_score,
            "timestamp": time.time(),
        }
        await websocket.send(json.dumps(ready))

    async def broadcast_status(self):
        if not self.connections:
            return
        snapshot = self.state_hub.snapshot()
        status = {
            "type": "cali_status",
            "data": {
                "cores": snapshot.get("cores", {}),
                "systems": snapshot.get("systems", {}),
                "controls": snapshot.get("controls", {}),
                "health": self.orb.health_score,
                "orb_status": self.orb.get_status(),
                "timestamp": time.time(),
            },
        }
        await asyncio.gather(
            *[conn.send(json.dumps(status)) for conn in list(self.connections)],
            return_exceptions=True,
        )

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        try:
            msg = json.loads(message)
            msg_type = msg.get("type")

            if msg_type == "orb_query":
                text = msg.get("text", "")
                session = msg.get("session_id")
                # Run orb processing off the event loop
                result = await asyncio.to_thread(self.orb.process_query, text, session)
                payload = {
                    "type": "query_result",
                    "data": result,
                    "core": msg.get("core", "kaygee"),
                    "timestamp": time.time(),
                }
                await websocket.send(json.dumps(payload))

            elif msg_type == "orb_status_request":
                await websocket.send(
                    json.dumps({"type": "status_response", "data": self.orb.get_status()})
                )

            elif msg_type == "orb_config":
                config = msg.get("config", {})
                self.orb.config.update(config)
                self.orb._recompute_state()
                await websocket.send(
                    json.dumps({"type": "config_ack", "data": self.orb.config, "timestamp": time.time()})
                )

            elif msg_type == "orb_audio":
                await websocket.send(
                    json.dumps({"type": "error", "error": "audio_not_implemented"})
                )

            else:
                await websocket.send(
                    json.dumps({"type": "error", "error": f"unknown_type:{msg_type}"})
                )

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Message handling error: {e}", exc_info=True)
            await websocket.send(json.dumps({"type": "error", "error": str(e)}))

    async def handler(self, websocket: WebSocketServerProtocol, _path: str):
        await self.register_connection(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            await self.unregister_connection(websocket)

    async def health_broadcast_loop(self):
        while self.is_running:
            try:
                await self.broadcast_status()
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"Broadcast error: {e}")

    async def start(self):
        logger.info(f"Starting CALI Bridge Server on {self.host}:{self.port}")
        self.is_running = True
        broadcast_task = asyncio.create_task(self.health_broadcast_loop())
        async with websockets.serve(self.handler, self.host, self.port):
            try:
                await asyncio.Future()  # run forever
            except asyncio.CancelledError:
                pass
            finally:
                self.is_running = False
                broadcast_task.cancel()
                with contextlib.suppress(Exception):
                    await broadcast_task
                logger.info("✓ Bridge server stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="CALI WebSocket Bridge Server")
    parser.add_argument("--host", default="localhost", help="Host to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind")
    args = parser.parse_args()

    server = CALIBridgeServer(host=args.host, port=args.port)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Shutting down bridge server...")


if __name__ == "__main__":
    main()
