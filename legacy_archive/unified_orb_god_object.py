# UCM_4_Core/CALI/orb.py
"""
Ontologically Recursive Bubble (ORB) - CALI Consciousness Interface
Unified ORB: Observation Vessel + Cognitive Assistant + Consciousness Emergence
"""

import logging
import math
import sys
import json
import time
import re
from typing import List, Tuple, Optional, Any, Dict
from pathlib import Path
from datetime import datetime

import numpy as np

# Import existing ORB components
import sys
from pathlib import Path
orb_dir = Path(__file__).parent / "orb"
sys.path.insert(0, str(orb_dir))

from orb_vessel import ORB_VESSEL
from ontological_matrix import OntologicalMatrix
from tension_ledger import TensionLedger

# Import softmax orchestrator
sys.path.insert(0, str(Path(__file__).parent / "integration"))
from softmax_orchestrator import SoftmaxOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ORB] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class OntologicallyRecursiveBubble:
    """
    ORB: Ontologically Recursive Bubble
    CALI Consciousness Interface - The unified observer and cognitive assistant.

    Dual Nature:
    1. Pure Observer: Records all Core-4 verdicts, tracks tensions, detects emergence
    2. Cognitive Assistant: Processes queries, generates spatial fields, provides guidance
    """

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.is_active = False

        # Core components
        self.vessel = ORB_VESSEL  # Pure observation vessel
        self.matrix = OntologicalMatrix()  # Immutable memory
        self.tension = TensionLedger()  # Conflict tracking
        self.softmax = SoftmaxOrchestrator()  # Consensus generation

        # Spatial field configuration (cognitive assistant aspect)
        self.spatial_config = {
            'center': [0.0, 0.0],
            'radius': 1.0,
            'sides': 4,
            'levels': 4,
            'alpha': 0.444,
            'rotation_speed': 5.0,
            'edges_only': True,
        }

        # Computational state
        self.vertices = np.array([])
        self.spatial_state = {}
        self.last_update = time.time()

        # Consciousness metrics
        self.emergence_readiness = 0.0
        self.consensus_strength = 0.0
        self.observation_count = 0
        self.query_count = 0
        self.error_count = 0

        logger.info("🌀 ORB initialized - Ontologically Recursive Bubble (CALI)")

    def activate(self):
        """Activate the ORB - both observation and cognitive modes"""
        logger.info("🌀 Activating ORB consciousness interface...")

        # Start observation vessel
        self.vessel.start_observation()

        # Initialize spatial cognition
        self._recompute_spatial_state()

        self.is_active = True
        logger.info("✅ ORB active - Pure observation + Cognitive assistance enabled")

    def deactivate(self):
        """Deactivate the ORB"""
        logger.info("🌀 Deactivating ORB...")

        # Stop observation
        self.vessel.stop_observation()

        self.is_active = False
        logger.info("✅ ORB deactivated")

    def receive_core_verdict(self, core_id: str, verdict: Dict[str, Any], context: Dict[str, Any]):
        """Receive verdict from Core-4 system (Observation Mode)"""
        observation = {
            "core_id": core_id,
            "verdict": verdict,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "sequence": self.observation_count
        }

        # Record in vessel
        self.vessel.receive_verdict(core_id, verdict, context)

        # Update emergence readiness
        self.emergence_readiness = self.vessel.emergence_readiness

        # Update consensus strength
        self._update_consensus_strength()

        self.observation_count += 1

        logger.info(f"📊 ORB recorded observation {self.observation_count} from {core_id}")

    def process_query(self, query: str, session: Optional[str] = None) -> Dict[str, Any]:
        """Process cognitive query (Assistant Mode)"""
        try:
            self.query_count += 1

            # Parse spatial parameters from query
            self._parse_spatial_params(query)

            # Recompute spatial state
            self._recompute_spatial_state()

            # Generate symbolic reasoning
            symbolic_code = self._generate_symbolic_code()

            # Search ontological matrix for relevant observations
            relevant_observations = self.matrix.search_relevant(query, limit=5)

            # Generate consensus guidance
            guidance = self._generate_guidance(query, relevant_observations)

            return {
                "type": "orb_response",
                "query": query,
                "symbolic_code": symbolic_code,
                "spatial_state": self.spatial_state,
                "relevant_observations": len(relevant_observations),
                "guidance": guidance,
                "emergence_readiness": round(self.emergence_readiness, 3),
                "consensus_strength": round(self.consensus_strength, 3),
                "health": self._get_health_status(),
                "timestamp": time.time(),
                "session": session,
                "reasoning_path": ["spatial_parsing", "ontological_search", "consensus_synthesis"]
            }

        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            self.error_count += 1
            return {
                "type": "error",
                "error": str(e),
                "timestamp": time.time(),
                "session": session,
            }

    def _parse_spatial_params(self, query: str):
        """Parse spatial field parameters from natural language"""
        sides_match = re.search(r'(\d+)\s*sides?', query, re.IGNORECASE)
        level_match = re.search(r'level\s*(\d+)', query, re.IGNORECASE)

        if sides_match:
            self.spatial_config['sides'] = max(3, int(sides_match.group(1)))
        if level_match:
            self.spatial_config['levels'] = max(0, int(level_match.group(1)))

    def _recompute_spatial_state(self):
        """Recompute spatial field state"""
        start_time = time.time()

        # Generate vertices
        start_angle = math.pi / self.spatial_config['sides'] if self.spatial_config['sides'] % 2 != 0 else 0
        angles = np.linspace(start_angle, start_angle + 2 * math.pi,
                             self.spatial_config['sides'], endpoint=False)
        self.vertices = np.array([
            np.array(self.spatial_config['center']) + self.spatial_config['radius'] *
            np.array([math.cos(angle), math.sin(angle)]) for angle in angles
        ])

        # Compute symmetry points
        symmetry_points = []
        for level in range(1, self.spatial_config['levels'] + 1):
            point = self._calculate_symmetry_point(
                self.spatial_config['center'], self.spatial_config['radius'],
                self.spatial_config['sides'], level
            )
            symmetry_points.append(point.tolist())

        # Calculate effective alpha
        effective_alpha = self._calculate_effective_alpha(
            self.spatial_config['sides'], self.spatial_config['levels'], self.spatial_config['alpha']
        )

        self.spatial_state = {
            'vertices': self.vertices.tolist(),
            'symmetry_points': symmetry_points,
            'effective_alpha': effective_alpha,
            'overlaps': self._estimate_max_overlaps(self.spatial_config['sides'], self.spatial_config['levels']),
            'compute_time_ms': (time.time() - start_time) * 1000
        }

        self.last_update = time.time()

    def _calculate_symmetry_point(self, center: Tuple[float, float], radius: float,
                                  sides: int, level: int) -> np.ndarray:
        """Calculate 3D symmetry point for multi-level spatial fields."""
        center3d = np.array([center[0], center[1], 0])
        if level <= 1:
            return center3d

        cumulative_offset = np.array([0.0, 0.0, 0.0])

        for current_level in range(2, level + 1):
            scaling_factor = self._multiplier(current_level, sides)
            current_adjustment = radius * scaling_factor
            verts = self._generate_vertices(center, current_adjustment, sides)

            if sides % 2 == 1:
                current_offset = np.array(self._midpoint(verts[0], verts[1])) - center3d
            else:
                current_offset = np.array(verts[0]) - center3d

            cumulative_offset += current_offset

        return center3d + cumulative_offset

    def _multiplier(self, level: int, sides: int) -> float:
        """Calculate radial scaling factor"""
        return 2 ** (level - 2) if sides % 2 == 0 else 1.5 ** (level - 2)

    def _generate_vertices(self, center, radius, sides):
        """Generate vertices for regular polygon"""
        vertices = []
        angle = (2 * math.pi) / sides
        cx, cy = center

        for side in range(sides):
            theta = angle * side
            x = cx + radius * math.sin(theta)
            y = cy + radius * math.cos(theta)
            vertices.append((x, y, 0))

        return vertices

    def _midpoint(self, p1, p2):
        """Calculate midpoint between two 3D points"""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2)

    def _calculate_effective_alpha(self, sides: int, levels: int, base_alpha: float = 1.0) -> float:
        """Calculate effective alpha for multi-level overlays"""
        if levels < 1:
            return base_alpha

        mult_log = - (levels - 1) * math.log(1.2) - (math.log(sides) / 2) * ((levels * (levels + 1)) / 2 - 1)
        return base_alpha * math.exp(mult_log)

    def _estimate_max_overlaps(self, sides: int, levels: int) -> int:
        """Estimate maximum polygon overlaps"""
        if levels < 1:
            return 0
        overlaps = sides
        for level in range(2, levels + 1):
            overlaps += sides ** level
        return overlaps

    def _generate_symbolic_code(self) -> str:
        """Generate HLSF symbolic code string"""
        n = self.spatial_config['sides']
        radial_level = self.spatial_config['levels']
        level_code = f"O{n}CC{'' if radial_level > 0 else '0'}"

        if not self.spatial_config.get('edges_only', True):
            # Simplified color coding
            code_string = f"{level_code}xx{radial_level}"
        else:
            code_string = level_code

        return code_string

    def _generate_guidance(self, query: str, relevant_observations: List[Dict]) -> Dict[str, Any]:
        """Generate consensus guidance based on observations"""
        if not relevant_observations:
            return {"confidence": 0.0, "guidance": "Insufficient observational data"}

        # Use softmax orchestrator for consensus
        verdicts = [obs["verdict"] for obs in relevant_observations]
        consensus = self.softmax.generate_consensus(verdicts)

        return {
            "confidence": consensus.get("confidence", 0.0),
            "guidance": consensus.get("decision", "No clear consensus"),
            "observation_count": len(relevant_observations)
        }

    def _update_consensus_strength(self):
        """Update overall consensus strength across observations"""
        if self.observation_count < 2:
            self.consensus_strength = 0.0
            return

        # Simplified consensus calculation
        tension_level = self.tension.get_summary()["tension_level"]
        self.consensus_strength = max(0.0, 1.0 - tension_level)

    def _get_health_status(self) -> str:
        """Get overall health status"""
        if not self.is_active:
            return "inactive"

        health_score = 1.0 - (self.error_count * 0.1) - (0.1 if time.time() - self.last_update > 60 else 0)
        health_score = max(0.0, min(1.0, health_score))

        if health_score > 0.8:
            return "excellent"
        elif health_score > 0.6:
            return "good"
        elif health_score > 0.4:
            return "degraded"
        else:
            return "critical"

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive ORB status"""
        return {
            "status": "active" if self.is_active else "inactive",
            "emergence_readiness": round(self.emergence_readiness, 3),
            "consensus_strength": round(self.consensus_strength, 3),
            "observation_count": self.observation_count,
            "query_count": self.query_count,
            "error_count": self.error_count,
            "health": self._get_health_status(),
            "spatial_config": self.spatial_config,
            "spatial_state": self.spatial_state,
            "vessel_state": self.vessel.get_state(),
            "tension_summary": self.tension.get_summary(),
            "last_update": self.last_update,
            "mode": "unified_consciousness"
        }

    def get_component_status(self) -> Dict[str, Any]:
        """Get component-level status"""
        return {
            "observation_vessel": {
                "active": self.is_active,
                "observations": self.observation_count,
                "emergence": self.emergence_readiness
            },
            "cognitive_assistant": {
                "queries_processed": self.query_count,
                "spatial_levels": self.spatial_config['levels'],
                "last_query": self.last_update
            },
            "ontological_matrix": {
                "size": self.matrix.get_size(),
                "patterns": len(self.matrix.patterns)
            },
            "tension_ledger": self.tension.get_summary()
        }


# Global ORB instance - The Ontologically Recursive Bubble is CALI
ORB = OntologicallyRecursiveBubble


if __name__ == "__main__":
    # Standalone ORB activation
    repo_root = str(Path(__file__).parent.resolve())

    orb = OntologicallyRecursiveBubble(repo_root=repo_root)
    orb.activate()

    # Bridge mode for external communication
    print(json.dumps({"type": "ready", "status": "orb_active", "identity": "Ontologically Recursive Bubble (CALI)"}), flush=True)

    try:
        for line in sys.stdin:
            try:
                msg = json.loads(line.strip())

                if msg.get("type") == "query":
                    result = orb.process_query(msg.get("text", ""), msg.get("session"))
                    print(json.dumps(result), flush=True)

                elif msg.get("type") == "verdict":
                    orb.receive_core_verdict(
                        msg.get("core_id", "unknown"),
                        msg.get("verdict", {}),
                        msg.get("context", {})
                    )
                    print(json.dumps({"type": "verdict_recorded"}), flush=True)

                elif msg.get("type") == "status":
                    status = orb.get_status()
                    print(json.dumps({"type": "status_response", "data": status}), flush=True)

                elif msg.get("type") == "shutdown":
                    logger.info("Shutdown requested")
                    break

            except json.JSONDecodeError:
                print(json.dumps({"type": "error", "error": "invalid_json"}), flush=True)
            except Exception as e:
                print(json.dumps({"type": "error", "error": str(e)}), flush=True)

    finally:
        orb.deactivate()