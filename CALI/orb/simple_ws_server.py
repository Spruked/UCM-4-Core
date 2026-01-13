#!/usr/bin/env python3
"""
Simple WebSocket server for ORB UI on port 8766 with cursor tracking
"""

import asyncio
import websockets
import json
from datetime import datetime
import pyautogui
import pygetwindow as gw

# Global list of connected clients
connected_clients = set()

async def handle_connection(websocket, path):
    """Handle WebSocket connections from Electron app"""
    print(f"[WS SERVER] Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)

    try:
        # Send initial connection confirmation
        await websocket.send(json.dumps({
            "type": "connection_established",
            "message": "ORB WebSocket server ready",
            "timestamp": datetime.utcnow().isoformat()
        }))

        # Send show command to make the floating window visible
        await websocket.send(json.dumps({
            "command": "show",
            "timestamp": datetime.utcnow().isoformat()
        }))

        print("[WS SERVER] Sent show command to floating window")

        # Keep connection alive and echo messages
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"[WS SERVER] Received: {data}")

                # Echo back with acknowledgment
                response = {
                    "type": "acknowledged",
                    "original_message": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(response))

            except json.JSONDecodeError:
                # Handle non-JSON messages
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON received",
                    "timestamp": datetime.utcnow().isoformat()
                }))

    except websockets.exceptions.ConnectionClosed:
        print(f"[WS SERVER] Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def cursor_tracking_loop():
    """Track cursor position and send updates to all connected clients"""
    last_position = None
    last_app = None

    while True:
        try:
            # Get current cursor position
            cursor_pos = pyautogui.position()

            # Get active window info
            active_window = gw.getActiveWindow()
            current_app = None
            if active_window:
                current_app = {
                    "title": active_window.title,
                    "pid": getattr(active_window, 'pid', None)
                }

            # Only send updates if position or app changed
            if cursor_pos != last_position or current_app != last_app:
                # Calculate bubble position (offset from cursor)
                offset_x, offset_y = 20, 20  # 20px offset from cursor
                target_x = cursor_pos[0] + offset_x
                target_y = cursor_pos[1] + offset_y

                # Keep within screen bounds (handle multiple monitors)
                screen_width, screen_height = pyautogui.size()
                target_x = max(0, min(target_x, screen_width - 120))  # 120px bubble width
                target_y = max(0, min(target_y, screen_height - 120))  # 120px bubble height

                # Send position update to all connected clients
                position_update = {
                    "command": "update_position",
                    "x": target_x,
                    "y": target_y,
                    "cursor_x": cursor_pos[0],
                    "cursor_y": cursor_pos[1],
                    "application": current_app,
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Send to all connected clients
                disconnected_clients = set()
                for client in connected_clients:
                    try:
                        await client.send(json.dumps(position_update))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.add(client)

                # Remove disconnected clients
                connected_clients.difference_update(disconnected_clients)

                last_position = cursor_pos
                last_app = current_app

            # Small delay to prevent excessive updates
            await asyncio.sleep(0.05)  # 20 FPS tracking

        except Exception as e:
            print(f"[WS SERVER] Cursor tracking error: {e}")
            await asyncio.sleep(1.0)

async def main():
    """Start the WebSocket server and cursor tracking"""
    print("[WS SERVER] Starting ORB WebSocket server on port 8766...")

    server = await websockets.serve(
        handle_connection,
        "localhost",
        8766,
        ping_interval=None  # Disable ping-pong to keep connection simple
    )

    print("[WS SERVER] Server started. Starting cursor tracking...")

    # Run both server and cursor tracking concurrently
    await asyncio.gather(
        server.wait_closed(),
        cursor_tracking_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())