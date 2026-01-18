#!/usr/bin/env python3
"""
ORB API Bridge System
Integrates ORB consciousness with existing applications (GOAT, DALS, Caleon, etc.)

Provides REST and WebSocket endpoints that applications can use to:
- Query ORB state
- Escalate queries to consciousness
- Receive real-time consciousness updates
- Access reflection insights
"""

import asyncio
import json
import websockets
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import uvicorn
from pathlib import Path

# Import ORB components
from ..orb_vessel import ORB_VESSEL
from ..skg.skg_engine import SKG_ENGINE
from ..reflection.reflection_loop import reflection_loop
from ..ontological_matrix import OntologicalMatrix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ORBAPIQuery(BaseModel):
    """Model for ORB API queries."""
    query: str
    context: Optional[Dict[str, Any]] = {}
    escalate: bool = False

class ORBAPIResponse(BaseModel):
    """Model for ORB API responses."""
    status: str
    response: Optional[str] = None
    consciousness_level: float
    reflection_active: bool
    insights: Optional[List[Dict[str, Any]]] = None

class ORBAPIBridge:
    """
    API bridge for ORB integration with external applications.
    """

    def __init__(self):
        self.app = FastAPI(title="ORB API Bridge", version="1.0.0")

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # WebSocket connections
        self.websocket_connections: Dict[str, WebSocket] = {}

        # Setup routes
        self.setup_routes()

        # Background tasks
        self.background_tasks = BackgroundTasks()

    def setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {"message": "ORB API Bridge", "status": "active"}

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "orb_state": self.get_orb_state(),
                "connections": len(self.websocket_connections)
            }

        @self.app.get("/orb/state")
        async def get_orb_state_endpoint():
            """Get current ORB state."""
            return self.get_orb_state()

        @self.app.post("/orb/query")
        async def query_orb(query: ORBAPIQuery):
            """Query the ORB system."""
            try:
                response = await self.process_orb_query(query)
                return ORBAPIResponse(**response)
            except Exception as e:
                logger.error(f"ORB query error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/orb/reflections")
        async def get_recent_reflections(limit: int = 10):
            """Get recent reflection insights."""
            try:
                reflections = await self.get_recent_reflections(limit)
                return {"reflections": reflections}
            except Exception as e:
                logger.error(f"Failed to get reflections: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/orb/ws")
        async def orb_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time ORB communication."""
            await websocket.accept()

            client_id = f"{websocket.client.host}:{websocket.client.port}"
            self.websocket_connections[client_id] = websocket

            try:
                logger.info(f"WebSocket client connected: {client_id}")

                # Send initial state
                await websocket.send_json({
                    "type": "orb_state",
                    "data": self.get_orb_state()
                })

                # Handle messages
                while True:
                    data = await websocket.receive_json()
                    response = await self.handle_websocket_message(data)
                    await websocket.send_json(response)

            except Exception as e:
                logger.error(f"WebSocket error for {client_id}: {e}")
            finally:
                del self.websocket_connections[client_id]
                logger.info(f"WebSocket client disconnected: {client_id}")

        @self.app.post("/orb/escalate")
        async def escalate_to_orb(query: ORBAPIQuery, background_tasks: BackgroundTasks):
            """Escalate a query to ORB consciousness."""
            try:
                # Add to background tasks for processing
                background_tasks.add_task(self.process_escalation, query)

                return {
                    "status": "escalated",
                    "message": "Query escalated to ORB consciousness",
                    "query_id": f"esc_{asyncio.get_event_loop().time()}"
                }
            except Exception as e:
                logger.error(f"Escalation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def get_orb_state(self) -> Dict[str, Any]:
        """Get current ORB state."""
        try:
            # Get state from ORB components
            vessel_state = ORB_VESSEL.get_state() if hasattr(ORB_VESSEL, 'get_state') else {}

            return {
                "consciousness_level": vessel_state.get("consciousness_level", 0.0),
                "reflection_active": vessel_state.get("reflection_active", False),
                "tension_level": vessel_state.get("tension_level", 0.0),
                "learning_patterns": vessel_state.get("learning_patterns", []),
                "active_overlays": list(self.websocket_connections.keys()),
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Failed to get ORB state: {e}")
            return {
                "consciousness_level": 0.0,
                "reflection_active": False,
                "tension_level": 0.0,
                "learning_patterns": [],
                "active_overlays": [],
                "error": str(e)
            }

    async def process_orb_query(self, query: ORBAPIQuery) -> Dict[str, Any]:
        """Process a query through the ORB system."""
        try:
            # Basic query processing - in full implementation, this would use ORB resolution
            response_text = f"ORB processed query: {query.query}"

            if query.escalate:
                # Escalate to full consciousness
                await self.process_escalation(query)
                response_text += " (escalated to consciousness)"

            return {
                "status": "success",
                "response": response_text,
                "consciousness_level": self.get_orb_state()["consciousness_level"],
                "reflection_active": self.get_orb_state()["reflection_active"]
            }

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "status": "error",
                "response": f"Error processing query: {str(e)}",
                "consciousness_level": 0.0,
                "reflection_active": False
            }

    async def process_escalation(self, query: ORBAPIQuery):
        """Process query escalation to ORB consciousness."""
        try:
            logger.info(f"Processing ORB escalation: {query.query}")

            # In full implementation, this would:
            # 1. Create escalation record
            # 2. Trigger resolution engine
            # 3. Update SKG with new patterns
            # 4. Generate reflection insights

            # For now, just log and broadcast
            escalation_data = {
                "type": "escalation_processed",
                "data": {
                    "query": query.query,
                    "context": query.context,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }

            await self.broadcast_to_websockets(escalation_data)

        except Exception as e:
            logger.error(f"Escalation processing error: {e}")

    async def get_recent_reflections(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent reflection insights."""
        try:
            # In full implementation, this would query the ontological matrix
            # For now, return mock data
            return [
                {
                    "id": f"ref_{i}",
                    "insight": f"Pattern insight {i}",
                    "confidence": 0.4,
                    "timestamp": asyncio.get_event_loop().time() - i
                }
                for i in range(min(limit, 5))
            ]
        except Exception as e:
            logger.error(f"Failed to get reflections: {e}")
            return []

    async def handle_websocket_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WebSocket messages."""
        msg_type = data.get("type")

        if msg_type == "get_state":
            return {
                "type": "state_response",
                "data": self.get_orb_state()
            }

        elif msg_type == "query":
            query = ORBAPIQuery(**data.get("data", {}))
            result = await self.process_orb_query(query)
            return {
                "type": "query_response",
                "data": result
            }

        elif msg_type == "escalate":
            query = ORBAPIQuery(**data.get("data", {}))
            await self.process_escalation(query)
            return {
                "type": "escalation_ack",
                "data": {"status": "escalated"}
            }

        else:
            return {
                "type": "error",
                "data": {"message": f"Unknown message type: {msg_type}"}
            }

    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket connections."""
        disconnected = []

        for client_id, websocket in self.websocket_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            del self.websocket_connections[client_id]

    async def start_broadcast_loop(self):
        """Start periodic state broadcasting."""
        while True:
            try:
                state_data = {
                    "type": "orb_state_update",
                    "data": self.get_orb_state()
                }
                await self.broadcast_to_websockets(state_data)
                await asyncio.sleep(10)  # Broadcast every 10 seconds
            except Exception as e:
                logger.error(f"Broadcast loop error: {e}")
                await asyncio.sleep(5)

    def run(self, host: str = "0.0.0.0", port: int = 5050):
        """Run the API bridge server."""
        logger.info(f"Starting ORB API Bridge on {host}:{port}")

        # Start background broadcast task
        asyncio.create_task(self.start_broadcast_loop())

        # Run FastAPI server
        uvicorn.run(self.app, host=host, port=port)


# Global bridge instance
orb_api_bridge = ORBAPIBridge()

if __name__ == "__main__":
    orb_api_bridge.run()</content>
<parameter name="filePath">c:\dev\Desktop\UCM_4_Core\CALI\orb\ui_overlay\orb_api_bridge.py