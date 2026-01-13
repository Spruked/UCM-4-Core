# core4_bridge.py
import asyncio
import json
import os
import logging
import importlib.util
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib import request, error as urlerror

import numpy as np
from fastapi import FastAPI, WebSocket, HTTPException

from ..orchestration.orchestration_skg import AttentionGovernor
from ..orchestration.unified_vault import UnifiedVault, UnifiedSensoryIO, VaultBindingError
from ...softmax_advisory_skor.consensus_advisor import process_core4_consensus
from ...core4_emission_adapter import collect_and_emit, CoreEmissionError


def _load_pom_classes():
    pom_path = os.path.join(os.path.dirname(__file__), "..", "..", "POM_2.0", "uvula_control.py")
    spec = importlib.util.spec_from_file_location("pom_uvula_control", pom_path)
    if not spec or not spec.loader:
        raise ImportError("Cannot load pom_uvula_control module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.UvulaController, module.POMRequest, module.POMBindingError


UvulaController, POMRequest, POMBindingError = _load_pom_classes()


logger = logging.getLogger(__name__)


@dataclass
class CoreEndpoint:
    core_id: str
    url: str
    method: str = "POST"
    payload_key: str = "query"
    headers: Dict[str, str] = field(default_factory=dict)


def _read_json_file(path: str) -> Optional[List[Dict]]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _parse_endpoint_list(data: List[Dict]) -> Dict[str, CoreEndpoint]:
    endpoints: Dict[str, CoreEndpoint] = {}
    for item in data or []:
        try:
            core_id = item["core_id"]
            url = item["url"]
            method = item.get("method", "POST").upper()
            payload_key = item.get("payload_key", "query")
            headers = item.get("headers", {}) or {}
            endpoints[core_id] = CoreEndpoint(core_id=core_id, url=url, method=method, payload_key=payload_key, headers=headers)
        except Exception:
            continue
    return endpoints


def _load_core_endpoints() -> Dict[str, CoreEndpoint]:
    raw_env = os.getenv("CORE4_BRIDGE_ENDPOINTS")
    if raw_env:
        try:
            parsed = json.loads(raw_env)
            endpoints = _parse_endpoint_list(parsed)
            if endpoints:
                return endpoints
        except Exception:
            pass

    file_env = os.getenv("CORE4_BRIDGE_ENDPOINTS_FILE")
    if file_env and os.path.exists(file_env):
        data = _read_json_file(file_env)
        endpoints = _parse_endpoint_list(data or [])
        if endpoints:
            return endpoints

    default_path = os.path.join(os.getcwd(), "core4_bridge_endpoints.json")
    if os.path.exists(default_path):
        data = _read_json_file(default_path)
        endpoints = _parse_endpoint_list(data or [])
        if endpoints:
            return endpoints

    raise RuntimeError("CORE4_BRIDGE_ENDPOINTS not configured; no core endpoints available")


def _assert_vector(vec: Any, dim: int, field_name: str) -> np.ndarray:
    arr = np.asarray(vec, dtype=np.float64).reshape(-1)
    if arr.shape != (dim,) or not np.isfinite(arr).all():
        raise ValueError(f"{field_name} must be length {dim} with finite values")
    if np.allclose(arr, 0.0):
        raise ValueError(f"{field_name} cannot be all zeros")
    return arr

class Core4Bridge:
    """
    Integration bridge connecting all four systems
    Runs as independent processes communicating via shared vault and memory
    """
    
    def __init__(self, asr_provider, embedder_provider, embed_dim: int):
        self.app = FastAPI(title="Core 4 Superintelligence Bridge")
        if asr_provider is None or embedder_provider is None:
            raise VaultBindingError("ASR and embedding providers are required for bridge")
        self.embed_dim = embed_dim
        
        # State tracking
        self.active_cores = {
            'ucm_core': False,
            'kaygee': False,
            'caleon': False,
            'cali_x': False
        }

        # Core endpoints must be explicitly configured (no fabricated data)
        self.core_endpoints = _load_core_endpoints()
        missing = [cid for cid in self.active_cores if cid not in self.core_endpoints]
        if missing:
            raise RuntimeError(
                f"Missing endpoint configuration for cores: {missing}. "
                "Define CORE4_BRIDGE_ENDPOINTS (or file) with urls for all cores."
            )
        
        # Shared orchestration
        self.orchestrator = AttentionGovernor()
        self.vault = UnifiedVault(asr_provider, embedder_provider, dim=embed_dim)
        self.sensory = UnifiedSensoryIO(self.orchestrator, self.vault)
        self.uvula_controller: Optional[UvulaController] = None

    def _validate_core_verdict(self, core_id: str, verdict: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(verdict, dict):
            raise ValueError(f"{core_id}: verdict must be a dict")

        required_fields = ["core", "verdict", "confidence", "competency_vector", "recommended_path"]
        for field_name in required_fields:
            if field_name not in verdict:
                raise ValueError(f"{core_id}: missing required field '{field_name}'")

        if verdict.get("core") != core_id:
            raise ValueError(f"{core_id}: core field mismatch (got {verdict.get('core')})")

        verdict_text = verdict.get("verdict")
        if not isinstance(verdict_text, str) or not verdict_text.strip():
            raise ValueError(f"{core_id}: verdict must be non-empty string")

        confidence = float(verdict.get("confidence"))
        if not (0.0 <= confidence <= 1.0) or not np.isfinite(confidence):
            raise ValueError(f"{core_id}: confidence must be finite in [0,1]")

        comp_vec = _assert_vector(verdict.get("competency_vector"), 512, f"{core_id}: competency_vector")

        recommended_path = verdict.get("recommended_path")
        if not isinstance(recommended_path, str) or not recommended_path.strip():
            raise ValueError(f"{core_id}: recommended_path must be non-empty string")

        constraints = verdict.get("constraints")
        if constraints is not None:
            if not isinstance(constraints, list) or not all(isinstance(c, str) for c in constraints):
                raise ValueError(f"{core_id}: constraints must be list of strings if provided")

        metadata = verdict.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValueError(f"{core_id}: metadata must be dict if provided")

        # Normalize and return validated copy (immutability for downstream)
        normalized = dict(verdict)
        normalized["confidence"] = float(confidence)
        normalized["competency_vector"] = comp_vec.tolist()
        normalized["constraints"] = constraints or []
        normalized["metadata"] = metadata

        return normalized

    async def _fetch_core_verdict(self, core_id: str, query: str, context_vector: Optional[np.ndarray]) -> Dict[str, Any]:
        endpoint = self.core_endpoints[core_id]

        payload: Dict[str, Any] = {
            endpoint.payload_key: query
        }
        if context_vector is not None:
            payload["context_vector"] = context_vector.tolist()

        data = json.dumps(payload).encode("utf-8")

        def _do_request():
            req = request.Request(endpoint.url, data=data, method=endpoint.method)
            req.add_header("Content-Type", "application/json")
            for k, v in endpoint.headers.items():
                req.add_header(k, v)
            with request.urlopen(req, timeout=10) as resp:
                body = resp.read()
                return json.loads(body)

        try:
            loop = asyncio.get_running_loop()
            raw_verdict = await loop.run_in_executor(None, _do_request)
        except Exception as exc:  # urlerror.URLError et al
            logger.error(f"{core_id}: fetch failed: {exc}")
            raise RuntimeError(f"{core_id} verdict fetch failed") from exc

        validated = self._validate_core_verdict(core_id, raw_verdict)
        self.vault.store(core_id, 'verdicts', validated)
        return validated
        
    async def start_core(self, core_id: str):
        """Initialize a core system"""
        if core_id == 'ucm_core':
            await self._start_ucm_core()
        elif core_id == 'kaygee':
            await self._start_kaygee()
        elif core_id == 'caleon':
            await self._start_caleon()
        elif core_id == 'cali_x':
            await self._start_cali_x()
        
        self.active_cores[core_id] = True
    
    async def _start_ucm_core(self):
        """Start UCM_Core_ECM philosophical engine (no placeholders)."""

        @self.app.post("/api/ucm/adjudicate")
        async def ucm_adjudicate(request_body: Dict):
            query = request_body.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="query is required")

            verdict = await self._fetch_core_verdict("ucm_core", query=query, context_vector=None)
            self.vault.store(core_id='ucm_core', data_type='contracts', payload=verdict)
            return verdict
    
    async def _start_kaygee(self):
        """Start KayGee visualization and monitoring (no fabricated metrics)."""

        @self.app.websocket("/ws/kaygee/monitor")
        async def kaygee_monitor(websocket: WebSocket):
            await websocket.accept()

            while True:
                states = {}
                for core_id in self.active_cores.keys():
                    state = self.vault.retrieve(
                        vault_address=f"vault://{core_id}/consciousness/last",
                        requester_core='kaygee'
                    )
                    states[core_id] = state

                if not any(states.values()):
                    await websocket.send_json({
                        'error': 'no_state_available',
                        'states': states,
                        'timestamp': datetime.now().isoformat()
                    })
                    await asyncio.sleep(0.5)
                    continue

                await websocket.send_json({
                    'states': states,
                    'timestamp': datetime.now().isoformat()
                })

                await asyncio.sleep(0.1)
    
    async def _start_caleon(self):
        """Start Caleon voice/consciousness loop"""
        # from caleon_genesis.audio import CochlearProcessor, PhonatoryOutput
        
        # self.cochlear = CochlearProcessor()
        # self.pom = PhonatoryOutput()  # Placeholders
        
        # Continuous audio loop
        @self.app.post("/api/caleon/process_audio")
        async def process_audio(request_body: Dict[str, Any]):
            audio_file = request_body.get("audio")
            sample_rate = request_body.get("sample_rate")
            if audio_file is None or sample_rate is None:
                raise HTTPException(status_code=400, detail="audio and sample_rate are required")

            # Single audio input → all cores
            result = self.sensory.process_audio_input(audio_file, sample_rate)
            
            # Generate voice response
            audio_response = self.sensory.generate_voice_output(result)
            
            return {
                'text_response': result['council_recommendation'],
                'audio_response': audio_response,
                'attention_weights': result['attention_weights']
            }
    
    async def _start_cali_x(self):
        """Start Cali_X AGI knowledge synthesis"""
        # from cali_x.skg import SuperKnowledgeGraph
        
        # self.skg = SuperKnowledgeGraph()  # Placeholder
        
        # Pattern recognition on unified memory
        @self.app.post("/api/cali/analyze")
        async def cali_analyze(pattern_request: Dict):
            # Retrieve relevant memories
            memories = self.orchestrator.memory_matrix.retrieve(
                query=np.array(pattern_request['query_vector']),
                top_k=10
            )
            
            # Find patterns across cores
            # patterns = self.skg.recursive_pattern_match(memories)
            patterns = ["pattern1", "pattern2"]  # Placeholder
            
            # Store knowledge
            self.vault.store(
                core_id='cali_x',
                data_type='patterns',
                payload={
                    'patterns': patterns,
                    'source_memories': memories
                }
            )
            
            return {
                'patterns': patterns,
                'knowledge_gain': len(patterns)
            }
    
    async def unified_query(self, query: str) -> Dict:
        """
        Main entry point: single query → council deliberation → unified response
        Full contract enforcement: all four cores, real vectors, no partials.
        """
        # Create context vector (must be real, finite, 512-dim)
        context_vector = self.sensory._embed_transcription(query)

        # Parallel core processing (must all succeed)
        core_verdicts = await asyncio.gather(
            self._query_ucm_core(query, context_vector),
            self._query_kaygee(query, context_vector),
            self._query_caleon(query, context_vector),
            self._query_cali_x(query, context_vector)
        )

        # Enforce contract and deterministic ordering
        core4_payload = collect_and_emit(core_verdicts)
        verdicts_dict = {v["core"]: v for v in core4_payload}

        # Orchestrate with attention
        orchestration_result = self.orchestrator.orchestrate(
            core_verdicts=verdicts_dict,
            context_vector=context_vector
        )

        # Outer advisory consensus (expression governance)
        advisory_signal = process_core4_consensus([
            {
                "core": v["core"],
                "verdict": v["verdict"],
                "confidence": v["confidence"],
                "reasoning": v.get("reasoning"),
                "metadata": v.get("metadata", {})
            }
            for v in core4_payload
        ])

        # Bind to POM if configured
        pom_out = None
        if self.uvula_controller:
            pom_req = POMRequest(
                text=advisory_signal.get("dominant_verdict", ""),
                prosody={"rate": 1.0, "pitch": 0.0, "energy": 1.0},
                voice_id="caleon_primary",
                sample_rate=22050,
            )
            pom_out = self.uvula_controller.speak(pom_req)

        return {
            'core4_verdicts': core4_payload,
            'orchestration': asdict(orchestration_result),
            'advisory_signal': advisory_signal,
            'response_text': advisory_signal.get('dominant_verdict'),
            'pom_output': pom_out
        }
    
    async def _query_ucm_core(self, query: str, context: np.ndarray) -> Dict:
        """Get philosophical adjudication from UCM (real core)."""
        return await self._fetch_core_verdict("ucm_core", query, context)
    
    async def _query_kaygee(self, query: str, context: np.ndarray) -> Dict:
        """Get cognitive resonance analysis from KayGee (real core)."""
        return await self._fetch_core_verdict("kaygee", query, context)
    
    async def _query_caleon(self, query: str, context: np.ndarray) -> Dict:
        """Get consciousness integration from Caleon (real core)."""
        return await self._fetch_core_verdict("caleon", query, context)
    
    async def _query_cali_x(self, query: str, context: np.ndarray) -> Dict:
        """Get knowledge synthesis from Cali_X (real core)."""
        return await self._fetch_core_verdict("cali_x", query, context)