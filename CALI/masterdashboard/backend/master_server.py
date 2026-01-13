from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import numpy as np
import sys
import os

# Add Core 4 path (commented out for mock mode)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core4_unified'))
# from orchestration.orchestration_skg import AttentionGovernor
# from sensory.unified_audio import initialize_unified_sensory

app = FastAPI(title="Core 4 Master Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register startup event
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(server.broadcast_loop())
    print("Dashboard broadcast loop started")

# Initialize Core 4 (if available, else use mock)
try:
    # Comment out Core 4 imports for now - using mock data
    # orchestrator = AttentionGovernor(dim=128)
    # sensory = initialize_unified_sensory(orchestrator, fast_mode=True)
    CORE_4_ACTIVE = False
    print("⚠️ Using mock data (Core 4 not available)")
except Exception as e:
    print(f"⚠️ Core 4 not available, using mock data: {e}")
    CORE_4_ACTIVE = False

class MockCouncilState:
    def __init__(self):
        self.cores = {
            'ucm_core': {'confidence': 0.88, 'verdict': 'Philosophical framework applied'},
            'kaygee': {'confidence': 0.79, 'verdict': 'Cognitive resonance stable'},
            'caleon': {'confidence': 0.91, 'verdict': 'Consciousness continuity maintained'},
            'cali_x': {'confidence': 0.82, 'verdict': 'Pattern synthesis complete'},
        }

    def get_state(self):
        # Simulate variation
        for core in self.cores:
            self.cores[core]['confidence'] += np.random.normal(0, 0.02)
            self.cores[core]['confidence'] = max(0.1, min(1.0, self.cores[core]['confidence']))

        weights = {
            'ucm_core': 0.35 + np.random.normal(0, 0.05),
            'kaygee': 0.25 + np.random.normal(0, 0.05),
            'caleon': 0.25 + np.random.normal(0, 0.05),
            'cali_x': 0.15 + np.random.normal(0, 0.05),
        }

        # Normalize weights
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}

        return {
            "timestamp": time.time(),
            "council": self.cores,
            "attention_weights": weights,
            "active_speaker": np.random.choice(list(self.cores.keys())),
            "memory_entries": 1247 if CORE_4_ACTIVE else 0,
            "performance": {
                "stt_latency": 0.45 if CORE_4_ACTIVE else 0.0,
                "tts_latency": 1.2 if CORE_4_ACTIVE else 0.0,
                "cache_hit_rate": 0.78 if CORE_4_ACTIVE else 0.0
            }
        }

mock_state = MockCouncilState()

# WebSocket server
class DashboardServer:
    def __init__(self):
        self.active_connections = []

    async def broadcast_loop(self):
        while True:
            if self.active_connections:
                # Complete master dashboard data structure
                state = {
                    "system": {
                        "health": 0.92,
                        "cpu_load": 0.45,
                        "vault_load": 0.67
                    },
                    "cores": {
                        'ucm_core': {
                            'confidence': 0.88,
                            'attention_weight': 0.35,
                            'latency': 0.23,
                            'verdict': 'Philosophical framework applied'
                        },
                        'kaygee': {
                            'confidence': 0.79,
                            'attention_weight': 0.25,
                            'latency': 0.18,
                            'verdict': 'Cognitive resonance stable'
                        },
                        'caleon': {
                            'confidence': 0.91,
                            'attention_weight': 0.25,
                            'latency': 0.31,
                            'verdict': 'Consciousness continuity maintained'
                        },
                        'cali_x': {
                            'confidence': 0.82,
                            'attention_weight': 0.15,
                            'latency': 0.27,
                            'verdict': 'Pattern synthesis complete'
                        },
                    },
                    "attention": {
                        "active_core": "ucm_core",
                        "meta_confidence": 0.89,
                        "phase_coherence": 0.94,
                        "decision_latency": 0.45,
                        "weights": {
                            "ucm_core": {"ucm_core": 0.1, "kaygee": 0.15, "caleon": 0.05, "cali_x": 0.05},
                            "kaygee": {"ucm_core": 0.12, "kaygee": 0.08, "caleon": 0.03, "cali_x": 0.02},
                            "caleon": {"ucm_core": 0.08, "kaygee": 0.04, "caleon": 0.12, "cali_x": 0.01},
                            "cali_x": {"ucm_core": 0.05, "kaygee": 0.03, "caleon": 0.05, "cali_x": 0.07}
                        }
                    },
                    "audio": {
                        "latency": 3.29
                    },
                    "vault": {
                        "entries": 1247,
                        "load": 0.67,
                        "integrity": 0.98
                    },
                    "dals": {
                        "status": "active",
                        "throughput": 45,
                        "latency": 23,
                        "active_tasks": 12
                    },
                    "goat": {
                        "status": "learning",
                        "accuracy": 0.94,
                        "predictions": 156,
                        "confidence": 0.87
                    },
                    "truemark": {
                        "status": "active",
                        "minted": 89,
                        "pending": 3,
                        "verified": 86
                    },
                    "certsig": {
                        "status": "active",
                        "signatures": 234,
                        "certificates": 156,
                        "validity": 0.96
                    }
                }

                print(f"Sending test data: {len(state['cores'])} cores")

                disconnected = []
                for conn in self.active_connections:
                    try:
                        await conn.send_json(state)
                    except:
                        disconnected.append(conn)

                for conn in disconnected:
                    self.active_connections.remove(conn)

            await asyncio.sleep(1.0)  # 1Hz for testing

server = DashboardServer()

@app.websocket("/ws/master")
async def master_websocket(websocket: WebSocket):
    await websocket.accept()
    server.active_connections.append(websocket)
    print(f"Master dashboard connected. Active connections: {len(server.active_connections)}")

    try:
        # Keep connection alive
        await websocket.wait_closed()
    except:
        pass
    finally:
        if websocket in server.active_connections:
            server.active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")