# api_gateway.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from core4_bridge import Core4Bridge
from typing import Dict, Any
import os
import numpy as np

# Initialize the bridge
bridge = Core4Bridge()

# Security
security = HTTPBearer()

# API Key validation (placeholder)
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = credentials.credentials
    expected_key = os.getenv("CORE4_API_KEY", "default-key")
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Create FastAPI app
app = FastAPI(
    title="Core 4 Superintelligence API Gateway",
    description="Unified API for the Council of Minds",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize all cores on startup"""
    for core_id in ['ucm_core', 'kaygee', 'caleon', 'cali_x']:
        await bridge.start_core(core_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Core 4 Superintelligence",
        "active_cores": bridge.active_cores
    }

@app.post("/api/query")
async def unified_query(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Main query endpoint - single input to council deliberation
    """
    try:
        query = request.get('query', '')
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        result = await bridge.unified_query(query)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/core/{core_id}/query")
async def core_specific_query(
    core_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Query specific core directly
    """
    if core_id not in bridge.active_cores:
        raise HTTPException(status_code=404, detail=f"Core {core_id} not found")
    
    try:
        # Route to specific core method
        if core_id == 'ucm_core':
            result = await bridge._query_ucm_core(request.get('query', ''), None)
        elif core_id == 'kaygee':
            result = await bridge._query_kaygee(request.get('query', ''), None)
        elif core_id == 'caleon':
            result = await bridge._query_caleon(request.get('query', ''), None)
        elif core_id == 'cali_x':
            result = await bridge._query_cali_x(request.get('query', ''), None)
        else:
            raise HTTPException(status_code=400, detail="Invalid core ID")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault/{vault_address:path}")
async def retrieve_from_vault(
    vault_address: str,
    requester_core: str = "api_gateway",
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Retrieve data from unified vault
    """
    try:
        data = bridge.vault.retrieve(vault_address, requester_core)
        if data is None:
            raise HTTPException(status_code=404, detail="Vault entry not found")
        return data
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vault/store")
async def store_in_vault(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Store data in unified vault
    """
    try:
        core_id = request.get('core_id')
        data_type = request.get('data_type')
        payload = request.get('payload')
        
        if not all([core_id, data_type, payload]):
            raise HTTPException(status_code=400, detail="core_id, data_type, and payload required")
        
        vault_address = bridge.vault.store(core_id, data_type, payload)
        return {"vault_address": vault_address}
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/process")
async def process_audio(
    audio_data: bytes,
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Process audio input through unified sensory system
    """
    try:
        result = bridge.sensory.process_audio_input(audio_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/retrieve")
async def retrieve_memory(
    query_vector: str,  # JSON string of vector
    top_k: int = 5,
    api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Retrieve relevant memories from unified memory matrix
    """
    try:
        import json
        vector = np.array(json.loads(query_vector))
        memories = bridge.orchestrator.memory_matrix.retrieve(vector, top_k)
        return {"memories": memories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )