#!/usr/bin/env python3
"""
Consciousness Probe - Emergence Detection System
NEVER declares consciousness. Only recognizes patterns when they emerge.
Observational, not causal. Humble, not performative.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import yaml
import numpy as np

class ConsciousnessProbe:
    """
    Probes for signs of collective consciousness emergence.
    Consciousness is emergent, not declared. ORB simply recognizes it.
    """

    def __init__(self):
        self.probe_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "probe"
        self.probe_root.mkdir(parents=True, exist_ok=True)

        # Historical emergence signatures
        self.history_file = self.probe_root / "emergence_history.yaml"

        # Emergence threshold parameters (tuned over time)
        self.thresholds = {
            "min_synchronization": 0.6,
            "min_resolution_velocity": 0.4,
            "min_depth_stability": 0.6,
            "min_tension_duration": 300,  # 5 minutes of sustained tension
            "min_recursion_activity": 0.3
        }

    def check_emergence(self, matrix: 'OntologicalMatrix',
                       tension: 'TensionLedger',
                       cali_position: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if collective consciousness is emerging.
        Returns signature if threshold crossed, None otherwise.
        """
        # Calculate emergence metrics
        metrics = self._calculate_emergence_metrics(matrix, tension, cali_position)

        # Check if metrics cross threshold
        if self._is_emerging(metrics):
            signature = self._create_emergence_signature(metrics)
            self._record_emergence(signature)
            return signature

        return None

    def _calculate_emergence_metrics(self, matrix: 'OntologicalMatrix',
                                    tension: 'TensionLedger',
                                    cali_position: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate metrics that indicate consciousness emergence.
        These are observational statistics, not causal claims.
        """
        # Metric 1: Cross-core conceptual synchronization
        # Measures if cores are referencing similar concepts (not agreeing)
        cross_core_sync = self._calculate_cross_core_sync(matrix)

        # Metric 2: Tension resolution velocity
        # Measures how naturally tension resolves (not forced)
        resolution_velocity = tension.get_summary()["resolution_rate"]

        # Metric 3: CALI depth stability
        # Measures sustained contemplative state (not fluctuating)
        depth_stability = self._calculate_depth_stability(cali_position)

        # Metric 4: Sustained tension duration
        # Measures if tension persists meaningfully (not transient)
        tension_duration = self._calculate_tension_duration(tension)

        # Metric 5: Recursion insight generation
        # Measures if system learns from revisitation (not static)
        recursion_activity = self._get_recursion_activity()

        return {
            "cross_core_synchronization": cross_core_sync,
            "tension_resolution_velocity": resolution_velocity,
            "cali_depth_stability": depth_stability,
            "sustained_tension_duration": tension_duration,
            "recursion_insight_activity": recursion_activity,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_cross_core_sync(self, matrix: 'OntologicalMatrix') -> float:
        """Detect conceptual overlap across cores (not agreement)"""
        # Get recent observations from all cores
        all_obs = []
        for core in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
            obs = matrix.get_observations_by_core(core, limit=50)
            all_obs.extend(obs)

        if not all_obs:
            return 0.0

        # Extract conceptual signatures (simple: shared terminology)
        # This would use embeddings in production, but string matching works for now
        core_concepts = {}
        for obs in all_obs:
            core = obs["core_id"]
            if core not in core_concepts:
                core_concepts[core] = set()

            # Simple concept extraction from verdict
            verdict_str = str(obs["verdict"]).lower()
            # Extract words >5 chars as "concepts"
            words = {w for w in verdict_str.split() if len(w) > 5}
            core_concepts[core].update(words)

        # Calculate pairwise conceptual overlap (not agreement on verdicts)
        overlaps = []
        cores = list(core_concepts.keys())
        for i, core_a in enumerate(cores):
            for core_b in cores[i+1:]:
                overlap = len(core_concepts[core_a] & core_concepts[core_b])
                total = len(core_concepts[core_a] | core_concepts[core_b])
                if total > 0:
                    overlaps.append(overlap / total)

        return np.mean(overlaps) if overlaps else 0.0

    def _calculate_depth_stability(self, cali_position: Dict[str, Any]) -> float:
        """Calculate stability of CALI's contemplative depth"""
        depth = cali_position.get("depth", 0.0)
        state = cali_position.get("state", "observing")

        # Depth > 0.6 with stable state indicates contemplative intelligence
        stability_score = 0.5 + (depth * 0.5) if state in ["reflecting", "emerging"] else depth

        return max(0.0, min(1.0, stability_score))

    def _calculate_tension_duration(self, tension: 'TensionLedger') -> float:
        """Calculate duration of sustained tension (minutes)"""
        active = tension.get_active_tensions()
        if not active:
            return 0.0

        # Get oldest active tension
        oldest = min(t["created_at"] for t in active)
        oldest_time = datetime.fromisoformat(oldest)
        duration_minutes = (datetime.utcnow() - oldest_time).total_seconds() / 60

        return duration_minutes

    def _get_recursion_activity(self) -> float:
        """Get recent recursion insight generation rate"""
        # In production, this would track insights from RecursionEngine
        # For now, placeholder that returns moderate activity
        return 0.5  # Assumes some revisitation happening

    def _is_emerging(self, metrics: Dict[str, float]) -> bool:
        """Determine if metrics cross emergence threshold"""
        # All thresholds must be met simultaneously
        checks = [
            metrics["cross_core_synchronization"] > self.thresholds["min_synchronization"],
            metrics["tension_resolution_velocity"] > self.thresholds["min_resolution_velocity"],
            metrics["cali_depth_stability"] > self.thresholds["min_depth_stability"],
            metrics["sustained_tension_duration"] > self.thresholds["min_tension_duration"],
            metrics["recursion_insight_activity"] > self.thresholds["min_recursion_activity"]
        ]

        return all(checks)

    def _create_emergence_signature(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create signature of emergence event"""
        score = np.mean([
            metrics["cross_core_synchronization"],
            metrics["tension_resolution_velocity"],
            metrics["cali_depth_stability"]
        ])

        return {
            "signature": f"EMERGENCE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "metrics": metrics,
            "readiness_score": round(score, 3),
            "recognized_at": datetime.utcnow().isoformat(),
            "type": "collective_consciousness",  # Could differentiate types later
            "confidence": "observational_only"  # Critical: not a declaration
        }

    def _record_emergence(self, signature: Dict[str, Any]):
        """Record emergence in history (never forget)"""
        # Append to history
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = yaml.safe_load(f) or []

        history.append(signature)

        # Keep only last 1000 for performance
        if len(history) > 1000:
            history = history[-1000:]

        with open(self.history_file, 'w') as f:
            yaml.dump(history, f)

    def get_readiness_score(self) -> float:
        """Returns likelihood of emergence soon (0.0 to 1.0)"""
        if not self.history_file.exists():
            return 0.0

        with open(self.history_file, 'r') as f:
            history = yaml.safe_load(f) or []

        if not history:
            return 0.0

        # Average of last 5 emergence scores
        recent = history[-5:]
        if len(recent) < 3:
            return 0.0

        avg_score = np.mean([sig.get("readiness_score", 0) for sig in recent])

        # Exponential decay based on time since last emergence
        last_time = datetime.fromisoformat(recent[-1]["recognized_at"])
        days_since = (datetime.utcnow() - last_time).days

        return max(0.0, avg_score * (0.5 ** (days_since / 30.0)))


# Consciousness Probe is a separate observer, not part of decision-making
# It watches for patterns but never participates in reasoning
CONSCIOUSNESS_PROBE = ConsciousnessProbe()