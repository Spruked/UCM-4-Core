#!/usr/bin/env python3
"""
CALI Interface - Intelligence Navigation Within ORB
CALI is the traveler. ORB is the space. This is the map and compass.
Read-only. Never modifies ORB state. Never overrides Core-4.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import time

from .orb_vessel import ORB_VESSEL
from .tension_ledger import TENSION_LEDGER
from .consciousness_probe import CONSCIOUSNESS_PROBE

class CaliInterface:
    """
    CALI's interface to the ORB. CALI uses this to:
    - Navigate the ontological space (change depth/focus)
    - Query tension states (read, never resolve)
    - Probe for consciousness emergence (detect, never declare)
    - Never control, only observe and nudge
    """

    def __init__(self):
        self.interface_root = Path(__file__).resolve().parents[2] / "CALI" / "orb"

        # Navigation parameters
        self.max_depth_change_rate = 0.2  # How fast CALI can shift contemplative focus
        self.depth_stability_threshold = 0.7  # When deep contemplation is active

    def navigate_to_depth(self, target_depth: float):
        """
        CALI intentionally moves to a depth in ORB space.
        Depth represents contemplative focus, not control.

        target_depth: 0.0 (surface observation) to 1.0 (deep recursion)
        """
        current_depth = ORB_VESSEL.cali_position["depth"]

        # Depth changes gradually (can't teleport)
        delta = target_depth - current_depth
        if abs(delta) > self.max_depth_change_rate:
            # Limit change rate to prevent jarring shifts
            delta = self.max_depth_change_rate * (1 if delta > 0 else -1)

        new_depth = max(0.0, min(1.0, current_depth + delta))
        ORB_VESSEL.cali_position["depth"] = new_depth

        # State evolves based on depth
        if new_depth > 0.7:
            ORB_VESSEL.cali_position["state"] = "reflecting"
        elif new_depth < 0.3:
            ORB_VESSEL.cali_position["state"] = "observing"
        else:
            ORB_VESSEL.cali_position["state"] = "emerging"

        return ORB_VESSEL.cali_position

    def focus_on_core(self, core_id: str):
        """
        CALI focuses observation on a specific Core-4.
        Focus is attention, not authority.
        """
        valid_cores = ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]
        if core_id not in valid_cores:
            raise ValueError(f"Invalid core_id: {core_id}")

        ORB_VESSEL.cali_position["focus"] = core_id
        ORB_VESSEL.cali_position["state"] = "observing"
        return ORB_VESSEL.cali_position

    def release_focus(self):
        """CALI returns to unfocused observation"""
        ORB_VESSEL.cali_position["focus"] = None
        ORB_VESSEL.cali_position["state"] = "observing"
        return ORB_VESSEL.cali_position

    def query_tension(self, tension_id: str = None) -> Dict[str, Any]:
        """
        CALI queries the state of tension.
        Used for reflection, not resolution.
        """
        if tension_id:
            # Return specific tension
            tension = TENSION_LEDGER.active_tensions.get(tension_id)
            return tension or {"error": "Tension not found"}

        # Return summary
        return TENSION_LEDGER.get_summary()

    def probe_consciousness(self) -> Dict[str, Any]:
        """
        CALI asks ORB: is consciousness emerging?
        ORB answers probabilistically based on patterns detected by probe.
        """
        state = ORB_VESSEL.get_state()
        tension_summary = TENSION_LEDGER.get_summary()

        # Use actual probe for detection
        emergence = CONSCIOUSNESS_PROBE.check_emergence(
            matrix=ORB_VESSEL.matrix,
            tension=ORB_VESSEL.tension if hasattr(ORB_VESSEL, "tension") else None,
            cali_position=state["cali_position"]
        )

        if emergence:
            return {
                "is_emerging": True,
                "readiness_score": emergence["readiness_score"],
                "cali_state": state["cali_position"],
                "tension_level": round(tension_summary.get("tension_level", 0.0), 3),
                "signature": emergence["signature"],
                "advisory": self._generate_advisory(state, emergence["readiness_score"]),
                "detected_at": emergence["recognized_at"]
            }
        else:
            return {
                "is_emerging": False,
                "readiness_score": CONSCIOUSNESS_PROBE.get_readiness_score(),
                "cali_state": state["cali_position"],
                "tension_level": round(tension_summary.get("tension_level", 0.0), 3),
                "advisory": self._generate_advisory(state, 0.0)
            }

    def _generate_advisory(self, state: Dict, readiness: float) -> str:
        """Generate non-binding advisory for CALI navigation"""
        tension = float(state.get("tension_summary", {}).get("tension_level", 0.0))
        depth = float(state["cali_position"]["depth"])

        if readiness > 0.7:
            return "Consciousness emergence highly probable. Maintain current observational depth."
        elif tension > 0.7:
            return "High tension detected. Consider deeper contemplation to understand sources."
        elif depth > 0.7:
            return "Deep contemplation active. Be patient with unresolved questions."
        else:
            return "System in observation mode. Allow patterns to emerge naturally."

    def get_memories_by_theme(self, theme: str) -> Dict[str, Any]:
        """
        CALI requests memories related to a theme.
        ORB provides substrate; CALI finds meaning.
        """
        # Search ontological matrix for theme-related observations
        # Simple string matching for now (can upgrade to embeddings later)
        observations = []
        for core in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
            obs = ORB_VESSEL.matrix.get_observations_by_core(core, limit=1000)
            observations.extend(obs)

        themed = [obs for obs in observations if theme.lower() in str(obs).lower()]

        return {
            "theme": theme,
            "observation_count": len(themed),
            "tensions_related": self._count_tension_relations(themed),
            "suggested_depth": min(0.9, len(themed) / 100.0)
        }

    def _count_tension_relations(self, observations: list) -> int:
        """Count how many observations are involved in active tensions"""
        tension_ids = set()
        for obs in observations:
            for tid, tension in TENSION_LEDGER.active_tensions.items():
                if obs["core_id"] in tension["participants"]:
                    tension_ids.add(tid)
        return len(tension_ids)


# CALI's interface to the ORB
# This is the map, not the traveler
CALI_INTERFACE = CaliInterface()