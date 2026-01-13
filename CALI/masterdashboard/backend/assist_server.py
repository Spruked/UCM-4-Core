from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time

app = FastAPI(title="Core 4 Assistance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/assist")
async def assist_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Assistant connection established")

    try:
        while True:
            data = await websocket.receive_json()

            if data["action"] == "help_requested":
                print(f"🆘 USER REQUESTS ASSISTANCE: {data['timestamp']}")
                # Notify all cores
                await notify_council_of_help_request()

            elif data["action"] == "begin_monitoring":
                print(f"📹 Screen monitoring started: {data['stream_id']}")

            elif data["action"] == "help_cancelled":
                print(f"✅ Help session cancelled: {data['timestamp']}")

    except Exception as e:
        print(f"Assistant connection error: {e}")

async def notify_council_of_help_request():
    """Broadcast to all 4 cores that user needs help"""
    # This would integrate with your existing orchestrator
    print("Notifying council: User requires immediate assistance")
    print("KayGee: Beginning screen analysis...")
    print("Caleon: Activating voice recognition...")
    print("UCM Core: Preparing philosophical framework...")
    print("Cali X: Initializing pattern synthesis...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)