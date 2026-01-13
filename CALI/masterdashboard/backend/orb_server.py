# ucm_4_core/cali/orb_server.py
"""
Enhanced CALI Orb server with CORS and Pulse broadcasting
Production-ready for React MasterDashboard integration
PRIVACY-SAFE: Only voluntary interactions, no surveillance
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import time
from dataclasses import dataclass

# Mock implementations for development (replace with real UCM imports)
class ChaCha20Vault:
    def encrypt(self, data): return data
    def encrypt_workspace(self, worker_id): pass

# Import SKG Manager
try:
    from orb_skg_manager import SKGRebuildEngine
except ImportError:
    # Fallback for development
    class SKGRebuildEngine:
        async def get_performance_report(self):
            return {
                "health_status": "healthy",
                "metrics": {"query_latency_ms": 50, "memory_usage_mb": 200, "fragmentation_ratio": 0.1},
                "emergency_cache": []
            }

@dataclass
class OrbPosition:
    x: float
    y: float
    target_x: float
    target_y: float
    cursor_distance: int = 350

class FloatingAssistantOrb:
    """
    ORB Floating UI Component - Part of the Ontologically Recursive Bubble (CALI)
    CURSOR-TRACKING ONLY - respects user privacy
    Tracks cursor position but NEVER captures screen/keystrokes
    """
    
    def __init__(self, vault_path: str, worker_id: str):
        self.vault_path = vault_path
        self.worker_id = worker_id

        # ✅ SAFE: Only cursor coordinates, no screen content
        self.current_position: Optional[OrbPosition] = None

        # ✅ SAFE: Voluntary interaction learning only
        self.voluntary_skg = {
            "query_history": [],
            "preferred_topics": {},
            "interaction_times": []
        }

        # ✅ SAFE: Explicit user-triggered actions only
        self.is_active = False

        # SKG Performance Manager
        self.skg_manager = SKGRebuildEngine(vault_path, worker_id)
        
    async def initialize_orb(self, screen_width: int, screen_height: int) -> bool:
        """Initialize with screen dimensions (NO capture permission needed)"""
        self.current_position = OrbPosition(
            x=screen_width // 2,
            y=screen_height // 2,
            target_x=screen_width // 2,
            target_y=screen_height // 2,
            cursor_distance=350
        )
        
        # Load voluntary interaction history (mock for now)
        # self.voluntary_skg = await self.forge.recall_vault_memory(
        #     domain="voluntary_interactions",
        #     key="user_preferences"
        # ) or self.voluntary_skg
        
        self.is_active = True
        return True
    
    async def update_cursor_position(self, cursor_x: int, cursor_y: int, screen_width: int, screen_height: int):
        """
        ✅ SAFE: Called by frontend, not by screen scraping
        Electron sends cursor coords voluntarily, no OS-level monitoring
        """
        if not self.current_position:
            return
        
        # Calculate avoidance vector (simple geometry, no screen reading)
        dx = cursor_x - self.current_position.x
        dy = cursor_y - self.current_position.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance < self.current_position.cursor_distance:
            # Move away from cursor (mathematical, not visual)
            angle = np.arctan2(dy, dx)
            target_distance = self.current_position.cursor_distance * 1.2
            
            self.current_position.target_x = int(
                cursor_x + np.cos(angle) * target_distance
            )
            self.current_position.target_y = int(
                cursor_y + np.sin(angle) * target_distance
            )
            
            # Clamp to screen bounds
            self._clamp_position(screen_width, screen_height)
    
    def _clamp_position(self, screen_width: int, screen_height: int):
        """Keep orb on screen"""
        margin = 50
        self.current_position.target_x = max(
            margin, 
            min(screen_width - margin, self.current_position.target_x)
        )
        self.current_position.target_y = max(
            margin, 
            min(screen_height - margin, self.current_position.target_y)
        )
    
    async def handle_voluntary_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        ✅ SAFE: User explicitly types/asks for help
        This is the ONLY way orb learns - voluntary interaction
        """
        # Mock ECM convergence for query understanding
        cognitive_response = {
            "answer": f"I understand you asked: '{query}'. This is a voluntary interaction that helps me learn your preferences.",
            "confidence": 0.95,
            "topic": self._extract_topic(query)
        }
        
        # Update SKG with VOLUNTARY interaction
        self.voluntary_skg["query_history"].append({
            "query": query,
            "context": context,
            "timestamp": time.time(),
            "response": cognitive_response
        })
        
        # Learn topic preferences (explicit user interest)
        topic = self._extract_topic(query)
        self.voluntary_skg["preferred_topics"][topic] = \
            self.voluntary_skg["preferred_topics"].get(topic, 0) + 1
        
        # Mock persist to vault
        # await self.forge.forge_skg_brain(
        #     pattern=self.voluntary_skg,
        #     context={"domain": "voluntary_interactions", "source": "user_queries"}
        # )
        
        return cognitive_response
    
    def _extract_topic(self, query: str) -> str:
        """Simple topic extraction from query"""
        topics = ["code", "search", "help", "explain", "debug"]
        query_lower = query.lower()
        for topic in topics:
            if topic in query_lower:
                return topic
        return "general"

app = FastAPI(
    title="CALI Floating Orb Server",
    description="UCM_4_Core Cognitive Voice Interface with Pulse Broadcasting",
    version="2.1.0"
)

# ===== CORS CONFIGURATION FOR REACT DASHBOARD =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://your-production-domain.com"  # Add your production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Pulse-Event"]  # Allow frontend to read Pulse headers
)

class PulseEvent:
    """Pulse event for UI synchronization"""
    def __init__(self, event_type: str, worker_id: str, timestamp: float, intensity: float = 1.0):
        self.event_type = event_type  # 'speech_start', 'speech_chunk', 'speech_end', 'listening_start'
        self.worker_id = worker_id
        self.timestamp = timestamp
        self.intensity = intensity  # 0.0 to 1.0 for UI animation

    def to_dict(self) -> Dict:
        return {
            "type": "PULSE",
            "event": self.event_type,
            "workerId": self.worker_id,
            "timestamp": self.timestamp,
            "intensity": self.intensity
        }

class OrbManager:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.active_orbs: Dict[str, FloatingAssistantOrb] = {}
        self.encryption = ChaCha20Vault()

        # WebSocket connection tracking for Pulse broadcasting
        self.connections: Dict[str, List[WebSocket]] = {}

    async def get_or_create_orb(self, worker_id: str) -> FloatingAssistantOrb:
        """Get existing orb or create new one with worker isolation"""
        if worker_id not in self.active_orbs:
            print(f"🎯 Initializing new Floating Orb for worker: {worker_id}")
            orb = FloatingAssistantOrb(
                vault_path=self.vault_path,
                worker_id=worker_id
            )
            await orb.initialize_orb(screen_width=1920, screen_height=1080)  # Default screen size
            self.active_orbs[worker_id] = orb

            # Initialize connection list for Pulse broadcasting
            self.connections[worker_id] = []

            # Encrypt worker workspace
            await self.encryption.encrypt_workspace(worker_id)

        return self.active_orbs[worker_id]

    async def register_connection(self, worker_id: str, websocket: WebSocket):
        """Register WebSocket connection for Pulse events"""
        if worker_id not in self.connections:
            self.connections[worker_id] = []
        self.connections[worker_id].append(websocket)
        print(f"🔗 Registered connection for worker {worker_id}. Total connections: {len(self.connections[worker_id])}")

    async def unregister_connection(self, worker_id: str, websocket: WebSocket):
        """Remove WebSocket connection"""
        if worker_id in self.connections:
            self.connections[worker_id].remove(websocket)
            print(f"🔌 Unregistered connection for worker {worker_id}")

    async def broadcast_pulse(self, worker_id: str, pulse: PulseEvent):
        """Broadcast Pulse event to all connected clients for a worker"""
        if worker_id in self.connections:
            dead_connections = []

            for connection in self.connections[worker_id]:
                try:
                    await connection.send_json(pulse.to_dict())
                except WebSocketDisconnect:
                    dead_connections.append(connection)
                except Exception as e:
                    print(f"⚠️ Pulse broadcast error: {e}")
                    dead_connections.append(connection)

            # Clean up dead connections
            for dead in dead_connections:
                await self.unregister_connection(worker_id, dead)

# Initialize global orb manager
orb_manager = OrbManager(vault_path="/opt/ucm_4_core/vault")

# ===== VOLUNTARY QUERY API (PRIVACY-SAFE) =====
class VoluntaryQuery(BaseModel):
    query: str
    context: dict  # URL, selected text (user-consented)
    voluntary: bool = True

@app.post("/api/orb/query")
async def handle_voluntary_query(data: VoluntaryQuery):
    """Handle voluntary user queries (privacy-safe)"""
    if not data.voluntary:
        raise HTTPException(status_code=403, detail="Only voluntary queries permitted")
    
    # Get or create orb
    orb = await orb_manager.get_or_create_orb("CALI_UNIT_01")
    result = await orb.handle_voluntary_query(data.query, json.dumps(data.context))
    return {"answer": result["answer"], "topic": result["topic"]}

# ===== PULSE STATUS ENDPOINT =====
@app.get("/pulse/{worker_id}")
async def get_pulse_status(worker_id: str):
    """Get current pulse status for a worker (REST fallback)"""
    orb = await orb_manager.get_or_create_orb(worker_id)

    return {
        "workerId": worker_id,
        "isActive": orb.is_active,
        "hasProfile": orb.current_profile is not None,
        "connectionCount": len(orb_manager.connections.get(worker_id, [])),
        "timestamp": time.time()
    }

# ===== PERFORMANCE MONITORING ENDPOINT =====
@app.get("/api/orb/performance")
async def get_performance_report():
    """Get SKG performance metrics for frontend HUD"""
    orb = await orb_manager.get_or_create_orb("CALI_UNIT_01")

    # Get performance report from SKG manager
    if hasattr(orb, 'skg_manager'):
        report = await orb.skg_manager.get_performance_report()
        return report
    else:
        # Fallback if SKG manager not available
        return {
            "health_status": "unknown",
            "metrics": {
                "query_latency_ms": 0,
                "memory_usage_mb": 0,
                "fragmentation_ratio": 0,
                "write_queue_depth": 0,
                "last_rebuild_timestamp": 0,
                "rebuild_count": 0
            },
            "thresholds": {},
            "rebuild_recommended": False,
            "next_rebuild_allowed": 0,
            "emergency_cache_size": 0
        }

# ===== MAIN WEBSOCKET ENDPOINT =====
@app.websocket("/ws/orb/{worker_id}")
async def websocket_orb_endpoint(websocket: WebSocket, worker_id: str):
    """Main WebSocket endpoint for bidirectional CALI communication"""
    await websocket.accept()

    # Get or create orb for this worker
    orb = await orb_manager.get_or_create_orb(worker_id)

    # Register connection for Pulse broadcasting
    await orb_manager.register_connection(worker_id, websocket)

    print(f"🌟 Orb connection established for worker: {worker_id}")

    try:
        while True:
            # Receive command from React dashboard
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "update_cursor":
                # ✅ SAFE: Update cursor position from frontend
                cursor_x = data.get("cursorX", 0)
                cursor_y = data.get("cursorY", 0)
                screen_width = data.get("screenWidth", 1920)
                screen_height = data.get("screenHeight", 1080)
                
                await orb.update_cursor_position(cursor_x, cursor_y, screen_width, screen_height)
                
                # Send updated position back
                if orb.current_position:
                    await websocket.send_json({
                        "type": "position_update",
                        "position": {
                            "x": orb.current_position.target_x,
                            "y": orb.current_position.target_y
                        },
                        "timestamp": time.time()
                    })

            elif action == "voluntary_query":
                # ✅ SAFE: Handle voluntary user query
                query = data.get("query", "")
                context = data.get("context", {})
                
                if not query:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No query provided",
                        "timestamp": time.time()
                    })
                    continue
                
                print(f"🤔 Voluntary query from {worker_id}: '{query[:50]}...'")
                
                # Process query
                result = await orb.handle_voluntary_query(query, json.dumps(context))
                
                # Send response
                await websocket.send_json({
                    "type": "query_response",
                    "answer": result["answer"],
                    "topic": result["topic"],
                    "timestamp": time.time()
                })

            elif action == "ping":
                # Keepalive
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": time.time()
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": time.time()
                })

    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected for worker {worker_id}")

    except Exception as e:
        error_msg = f"Orb error: {str(e)}"
        print(f"⚠️ {error_msg}")
        await websocket.send_json({
            "type": "error",
            "message": error_msg,
            "timestamp": time.time()
        })

    finally:
        # Unregister connection
        await orb_manager.unregister_connection(worker_id, websocket)

# ===== SHUTDOWN CLEANUP =====
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up orbs on shutdown"""
    print("🛑 Shutting down Floating Orb Server...")
    for worker_id, orb in orb_manager.active_orbs.items():
        orb.is_active = False
        print(f"  Deactivated orb for worker {worker_id}")

# ===== MAIN LAUNCHER (for direct execution) =====
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CALI Floating Orb Server on port 8000...")
    print("📡 CORS enabled for React development at http://localhost:5173-5174")
    print("🔮 Pulse broadcasting active for UI synchronization")

    uvicorn.run(
        "orb_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development mode
        log_level="info"
    )