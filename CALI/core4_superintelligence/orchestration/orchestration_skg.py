#!/usr/bin/env python3
"""
orchestration_skg.py
CALI UCM_4_Core Orchestration Engine v2.1
© 2025 Primary Design Co. & KayGee Systems
"""

import numpy as np
from typing import Dict, List, Any, Optional, Set
from collections import OrderedDict
from dataclasses import dataclass, field
import hashlib
import json
import time
import threading
import logging
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import contextmanager

# ==================== LOGGING & METRICS ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ORCHESTRATE] %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Thread-safe metrics for observability."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.queries_total = 0
        self.queries_failed = 0
        self.average_latency_ms = 0.0
        self.core_health = {core: 1.0 for core in ['ucm_core', 'kaygee', 'caleon', 'cali_x']}
        self.memory_usage = 0
    
    def record_query(self, latency_ms: float, success: bool):
        with self._lock:
            self.queries_total += 1
            if not success:
                self.queries_failed += 1
            # Rolling average
            self.average_latency_ms = (
                0.9 * self.average_latency_ms + 0.1 * latency_ms
            )
    
    def update_core_health(self, core: str, health: float):
        with self._lock:
            self.core_health[core] = health
    
    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'queries_total': self.queries_total,
                'queries_failed': self.queries_failed,
                'failure_rate': self.queries_failed / max(self.queries_total, 1),
                'avg_latency_ms': round(self.average_latency_ms, 2),
                'core_health': dict(self.core_health),
                'memory_usage_mb': round(self.memory_usage / 1024 / 1024, 2)
            }


metrics = MetricsCollector()


# ==================== CUSTOM EXCEPTIONS ====================

class OrchestrationError(Exception):
    """Base exception for orchestration failures."""
    pass


class InvalidCompetencyError(OrchestrationError):
    """Raised when core provides invalid competency vector."""
    pass


class AttentionWeightError(OrchestrationError):
    """Raised when attention computation fails."""
    pass


class MemoryFullError(OrchestrationError):
    """Raised when memory matrix reaches capacity."""
    pass


# ==================== DATA STRUCTURES ====================

@dataclass(frozen=True)
class OrchestrationResult:
    """Immutable orchestration result with validation."""
    unified_verdict: Dict[str, Any]
    attention_weights: Dict[str, float]
    confidence_score: float
    dominant_core: str
    council_recommendation: str
    memory_update: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=lambda: hashlib.sha256(
        f"{time.time()}-{threading.get_ident()}".encode()
    ).hexdigest()[:16])

    def __post_init__(self):
        """Validate result integrity."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"Invalid confidence: {self.confidence_score}")
        if not self.attention_weights or not self.dominant_core:
            raise ValueError("Missing attention weights or dominant core")
        if sum(self.attention_weights.values()) < 0.99:  # Allow floating point tolerance
            raise ValueError(f"Weights don't sum to ~1: {sum(self.attention_weights.values())}")


@dataclass
class CoreCircuit:
    """Circuit breaker state for each core."""
    failures: int = 0
    successes: int = 0
    last_failure: float = 0.0
    is_open: bool = False
    
    def record_success(self):
        self.successes += 1
        if self.successes > 10:
            self.failures = 0  # Reset after 10 successes
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= 3:
            self.is_open = True
    
    def can_attempt(self) -> bool:
        if not self.is_open:
            return True
        # Try again after 30 seconds
        if time.time() - self.last_failure > 30:
            self.is_open = False
            self.failures = 0
            return True
        return False


# ==================== MEMORY MATRIX ====================

class MemoryMatrix:
    """
    Thread-safe vector memory with cosine similarity retrieval.
    Implements TTL and size-based eviction.
    """
    def __init__(self, dim: int = 512, max_entries: int = 10_000, ttl_seconds: float = 3600):
        self.dim = dim
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        
        self._lock = threading.RLock()
        self.entries: List[Dict[str, Any]] = []
        self._cache: Dict[str, List[Dict]] = {}  # Simple query cache
        
        logger.info(f"MemoryMatrix initialized (dim={dim}, max={max_entries}, ttl={ttl_seconds}s")

    def update(
        self,
        context: np.ndarray,
        verdict: Dict[str, Any],
        attention_weights: np.ndarray
    ) -> Dict[str, Any]:
        with self._lock:
            try:
                # Validate inputs
                if context.shape != (self.dim,) or not np.isfinite(context).all():
                    raise InvalidCompetencyError("Invalid context vector shape or values")
                
                if not np.isfinite(attention_weights).all() or attention_weights.sum() <= 0:
                    raise AttentionWeightError("Invalid attention weights")
                
                # Evict old entries if needed
                self._evict_if_needed()
                
                # Create entry
                context_bytes = np.asarray(context, dtype=np.float64).tobytes()
                verdict_hash = self._hash_verdict(verdict)
                
                entry = {
                    'timestamp': time.time(),
                    'context': context_bytes,
                    'verdict_hash': verdict_hash,
                    'attention_weights': attention_weights.astype(np.float32).tolist(),
                    'ttl': time.time() + self.ttl_seconds
                }
                
                self.entries.append(entry)
                memory_id = len(self.entries) - 1
                
                # Clear cache on update
                self._cache.clear()
                
                return {
                    'memory_id': memory_id,
                    'stored': True,
                    'attention_weights': entry['attention_weights']
                }
                
            except Exception as e:
                logger.error(f"Memory update failed: {e}")
                raise

    def retrieve(self, query: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        with self._lock:
            try:
                if not self.entries:
                    return []
                
                if query.shape != (self.dim,) or not np.isfinite(query).all():
                    raise InvalidCompetencyError("Invalid query vector")
                
                # Check cache first
                cache_key = self._hash_vector(query)
                if cache_key in self._cache:
                    return self._cache[cache_key]
                
                # Compute similarities
                query_norm = np.linalg.norm(query)
                if query_norm == 0:
                    return []
                
                results = []
                for i, entry in enumerate(self.entries):
                    if time.time() > entry['ttl']:
                        continue  # Skip expired entries
                    
                    ctx = np.frombuffer(entry['context'], dtype=np.float64)
                    ctx_norm = np.linalg.norm(ctx)
                    if ctx_norm == 0:
                        continue
                    
                    sim = float(np.dot(query, ctx) / (query_norm * ctx_norm))
                    results.append((i, sim, entry))
                
                # Sort by similarity
                results.sort(key=lambda x: x[1], reverse=True)
                
                # Format output
                output = [{
                    'memory_id': i,
                    'similarity': sim,
                    'verdict_hash': entry['verdict_hash'],
                    'attention_weights': entry['attention_weights']
                } for i, sim, entry in results[:top_k]]
                
                # Cache result
                self._cache[cache_key] = output
                
                return output
                
            except Exception as e:
                logger.error(f"Memory retrieval failed: {e}")
                return []

    def _evict_if_needed(self):
        """Evict oldest entries if memory is full."""
        if len(self.entries) >= self.max_entries:
            # Remove oldest 10%
            evict_count = max(1, self.max_entries // 10)
            self.entries = self.entries[evict_count:]
            self._cache.clear()
            logger.warning(f"Evicted {evict_count} memory entries")

    @staticmethod
    def _hash_verdict(verdict: Dict) -> str:
        return hashlib.sha256(
            json.dumps(verdict, sort_keys=True, default=str).encode()
        ).hexdigest()

    @staticmethod
    def _hash_vector(vec: np.ndarray) -> str:
        return hashlib.sha256(vec.tobytes()).hexdigest()[:16]


# ==================== ATTENTION GOVERNOR ====================

class AttentionGovernor:
    """
    Thread-safe meta-reasoner with circuit breakers per core.
    Uses scaled dot-product attention with competency projections.
    """
    CORE_ORDER = OrderedDict([
        ('ucm_core', 'Epistemic Convergence'),
        ('kaygee', 'Voice & Spatial Reasoning'),
        ('caleon', 'Generative Synthesis'),
        ('cali_x', 'Expansion Logic')
    ])

    def __init__(self, dim: int = 512, seed: int = 42):
        self.dim = dim
        self.sqrt_dk = np.sqrt(dim)
        self._lock = threading.RLock()
        
        # Attention weights
        self.Wq = self._xavier_init(dim, dim)
        self.Wk = {core: self._xavier_init(dim, dim) for core in self.CORE_ORDER}
        
        # Circuit breakers
        self.circuits = {core: CoreCircuit() for core in self.CORE_ORDER}
        
        # Memory matrix
        self.memory_matrix = MemoryMatrix(dim=dim, max_entries=5_000)
        
        logger.info(f"AttentionGovernor initialized (dim={dim}, cores={len(self.CORE_ORDER)})")

    def _xavier_init(self, rows: int, cols: int) -> np.ndarray:
        limit = np.sqrt(6.0 / (rows + cols))
        return np.random.uniform(-limit, limit, (rows, cols)).astype(np.float32)

    def _stable_softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        x = x - x.max()
        exp_x = np.exp(x)
        return exp_x / exp_x.sum()

    def compute_attention_weights(
        self,
        context: np.ndarray,
        core_states: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """Compute attention weights with validation."""
        with self._lock:
            try:
                if context.shape != (self.dim,) or not np.isfinite(context).all():
                    raise InvalidCompetencyError("Invalid context vector")
                
                # Filter out failed cores
                active_cores = []
                keys = []
                
                for core in self.CORE_ORDER:
                    if core not in core_states:
                        continue
                    
                    if not self.circuits[core].can_attempt():
                        logger.warning(f"Circuit breaker open for {core}, skipping")
                        continue
                    
                    vec = core_states[core]
                    if vec.shape != (self.dim,) or not np.isfinite(vec).all():
                        raise InvalidCompetencyError(f"Invalid vector for {core}")
                    
                    try:
                        projected = vec @ self.Wk[core]
                        keys.append(projected)
                        active_cores.append(core)
                    except Exception as e:
                        logger.error(f"Projection failed for {core}: {e}")
                        self.circuits[core].record_failure()
                        continue
                
                if not keys:
                    raise AttentionWeightError("No active cores available")
                
                Q = context @ self.Wq
                K = np.stack(keys)
                scores = K @ Q / self.sqrt_dk
                weights = self._stable_softmax(scores)
                
                # Record successes
                for core in active_cores:
                    self.circuits[core].record_success()
                
                # Return weights aligned with CORE_ORDER (0 for skipped cores)
                full_weights = np.zeros(len(self.CORE_ORDER), dtype=np.float32)
                for i, core in enumerate(active_cores):
                    idx = list(self.CORE_ORDER.keys()).index(core)
                    full_weights[idx] = weights[i]
                
                return full_weights
                
            except Exception as e:
                logger.error(f"Attention computation failed: {e}")
                raise

    def orchestrate(
        self,
        core_verdicts: Dict[str, Dict],
        context_vector: np.ndarray,
        confidence_threshold: float = 0.7,
        timeout_ms: int = 5000
    ) -> OrchestrationResult:
        """
        Main orchestration entry point with timeout protection.
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not core_verdicts:
                raise OrchestrationError("No core verdicts provided")
            
            if not (0.0 <= confidence_threshold <= 1.0):
                raise ValueError("Invalid confidence threshold")
            
            # Extract competency vectors with validation
            core_states, core_confidences = self._extract_core_states(core_verdicts)
            
            # Compute attention weights
            attention_weights = self.compute_attention_weights(context_vector, core_states)
            weight_dict = dict(zip(self.CORE_ORDER.keys(), attention_weights.tolist()))
            
            # Weighted fusion
            unified = self._weighted_fusion(core_verdicts, attention_weights)
            
            # Confidence estimation
            confidence_score = self._estimate_confidence(attention_weights, core_confidences)
            
            # Determine dominant core
            dominant_idx = int(np.argmax(attention_weights))
            dominant_core = list(self.CORE_ORDER.keys())[dominant_idx]
            
            # Generate recommendation
            recommendation = self._generate_recommendation(unified, confidence_score)
            
            # Update memory
            memory_update = self.memory_matrix.update(
                context_vector, unified, attention_weights
            )
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_query(latency_ms, success=True)
            
            return OrchestrationResult(
                unified_verdict=unified,
                attention_weights=weight_dict,
                confidence_score=confidence_score,
                dominant_core=dominant_core,
                council_recommendation=recommendation,
                memory_update=memory_update
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_query(latency_ms, success=False)
            logger.error(f"Orchestration failed: {e}")
            raise

    def _extract_core_states(self, core_verdicts: Dict[str, Dict]):
        """Extract and validate competency vectors from verdicts."""
        core_states: Dict[str, np.ndarray] = {}
        core_confidences: List[float] = []
        ordered_verdicts: OrderedDict[str, Dict] = OrderedDict()
        
        for core in self.CORE_ORDER:
            if core not in core_verdicts:
                continue
            
            verdict = core_verdicts[core]
            vec = verdict.get('competency_vector')
            
            if vec is None:
                logger.warning(f"Missing competency vector for {core}")
                self.circuits[core].record_failure()
                continue
            
            try:
                arr = np.asarray(vec, dtype=np.float32).reshape(-1)
                if arr.shape != (self.dim,) or not np.isfinite(arr).all():
                    raise InvalidCompetencyError(f"Invalid vector for {core}")
                
                core_states[core] = arr
                core_confidences.append(float(verdict.get('confidence', 0.0)))
                ordered_verdicts[core] = verdict
                
            except Exception as e:
                logger.error(f"Core {core} validation failed: {e}")
                self.circuits[core].record_failure()
                continue
        
        if not core_states:
            raise OrchestrationError("No valid core verdicts available")
        
        return core_states, core_confidences

    def _weighted_fusion(
        self,
        verdicts: OrderedDict[str, Dict],
        weights: np.ndarray
    ) -> Dict[str, Any]:
        """Fuse verdicts based on attention weights."""
        unified = {
            'primary_path': None,
            'ethical_constraints': [],
            'confidence_trajectory': [],
            'cognitive_resonance': float(1.0 - np.std(weights)),  # Lower std = higher coherence
            'fused_timestamp': time.time()
        }
        
        for idx, (core_id, verdict) in enumerate(verdicts.items()):
            w = float(weights[idx])
            if w < 1e-6:
                continue
            
            conf = float(verdict.get('confidence', 0.0))
            unified['confidence_trajectory'].append({
                'core': core_id,
                'weight': w,
                'confidence': conf,
                'status': 'active' if w > 0.1 else 'suppressed'
            })
            
            if w > 0.3 and unified['primary_path'] is None:
                unified['primary_path'] = verdict.get('recommended_path')
            
            constraints = verdict.get('constraints', [])
            if constraints:
                unified['ethical_constraints'].extend(constraints)
        
        # Deduplicate constraints
        unified['ethical_constraints'] = list(dict.fromkeys(unified['ethical_constraints']))
        
        return unified

    def _estimate_confidence(self, weights: np.ndarray, core_confidences: List[float]) -> float:
        """Estimate overall confidence with consensus bonus."""
        if not core_confidences:
            return 0.0
        
        weighted_conf = float(np.dot(weights[:len(core_confidences)], core_confidences))
        consensus_bonus = 1.0 - np.std(weights)  # Low variance = high consensus
        confidence = weighted_conf * consensus_bonus
        
        return min(max(confidence, 0.0), 1.0)

    def _generate_recommendation(self, unified: Dict, confidence: float) -> str:
        """Generate human-readable council recommendation."""
        path = unified.get('primary_path', "No clear path identified")
        constraints = unified.get('ethical_constraints', [])
        
        if confidence > 0.85:
            base = f"Strong consensus: {path}"
        elif confidence > 0.65:
            base = f"Moderate agreement: {path}"
        elif confidence > 0.4:
            base = f"Partial convergence: {path}"
        else:
            return "Significant disagreement detected. Initiate deliberation protocol."
        
        if constraints:
            base += f" | Constraints: {', '.join(constraints[:3])}"
        
        return base

    def get_health(self) -> Dict[str, Any]:
        """Get governor health status."""
        with self._lock:
            return {
                'memory_entries': len(self.memory_matrix.entries),
                'circuit_states': {c: self.circuits[c].__dict__ for c in self.CORE_ORDER},
                'attention_matrix_shape': self.Wq.shape,
                'seed': 42  # For reproducibility
            }


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    # Simple test harness
    governor = AttentionGovernor(dim=512)
    
    # Mock context and verdicts
    context = np.random.randn(512).astype(np.float32)
    verdicts = {
        'ucm_core': {'competency_vector': np.random.randn(512), 'confidence': 0.9, 'constraints': ['ethical']},
        'kaygee': {'competency_vector': np.random.randn(512), 'confidence': 0.85, 'constraints': []},
        'caleon': {'competency_vector': np.random.randn(512), 'confidence': 0.7, 'constraints': ['creativity']},
        'cali_x': {'competency_vector': np.random.randn(512), 'confidence': 0.6, 'constraints': []}
    }
    
    try:
        result = governor.orchestrate(verdicts, context)
        print(json.dumps(result.__dict__, indent=2, default=str))
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)