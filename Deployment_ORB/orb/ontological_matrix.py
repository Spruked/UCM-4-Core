# UCM_4_Core/CALI/orb/ontological_matrix.py
"""
Ontological Matrix: Immutable memory system for Core-4 observations.
Tracks patterns, relationships, and consciousness emergence.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json

class OntologicalMatrix:
    """
    Immutable ontological matrix: records all observations, finds patterns.
    """

    def __init__(self):
        self.matrix_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "matrix"
        self.matrix_root.mkdir(parents=True, exist_ok=True)

        self.observations: List[Dict[str, Any]] = []
        self.patterns: Dict[str, Any] = {}

    def add_observation(self, observation: Dict[str, Any]):
        """Add observation to matrix"""
        self.observations.append(observation)
        self._update_patterns(observation)

    def _update_patterns(self, observation: Dict[str, Any]):
        """Update pattern recognition"""
        core_id = observation["core_id"]
        verdict = observation["verdict"]

        # Track core behavior patterns
        if core_id not in self.patterns:
            self.patterns[core_id] = {
                "verdict_count": 0,
                "confidence_sum": 0.0,
                "last_verdict": None,
                "consistency_score": 1.0
            }

        pattern = self.patterns[core_id]
        pattern["verdict_count"] += 1
        pattern["confidence_sum"] += verdict.get("confidence", 0.0)
        pattern["last_verdict"] = verdict

        # Update consistency (simplified)
        if pattern["verdict_count"] > 1:
            pattern["consistency_score"] = pattern["confidence_sum"] / pattern["verdict_count"]

    def get_recent_observations(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Get recent observations for reflection/analysis"""
        return self.observations[-limit:] if self.observations else []

    def get_observations_by_core(self, core_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get observations from specific core"""
        core_obs = [obs for obs in self.observations if obs.get("core_id") == core_id]
        return core_obs[-limit:] if core_obs else []

    def search_relevant(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant observations"""
        # Simple keyword search for now
        relevant = []
        for obs in self.observations[-100:]:  # Last 100 observations
            if query.lower() in str(obs).lower():
                relevant.append(obs)
                if len(relevant) >= limit:
                    break
        return relevant

    def get_size(self) -> int:
        """Get matrix size"""
        return len(self.observations)

    def load_existing(self):
        """Load existing matrix state"""
        matrix_file = self.matrix_root / "matrix.json"
        if matrix_file.exists():
            with open(matrix_file, 'r') as f:
                data = json.load(f)
                self.observations = data.get("observations", [])
                self.patterns = data.get("patterns", {})

    def save_state(self):
        """Save matrix state"""
        matrix_file = self.matrix_root / "matrix.json"
        data = {
            "observations": self.observations[-1000:],  # Keep last 1000
            "patterns": self.patterns,
            "saved_at": datetime.utcnow().isoformat()
        }
        with open(matrix_file, 'w') as f:
            json.dump(data, f, indent=2)