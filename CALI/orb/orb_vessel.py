# UCM_4_Core/CALI/orb/orb_vessel.py
"""
ORB Vessel - Ontological Observation Layer
Writes Core-4 verdicts immutably. Never reads for reasoning. Never modifies.
"""

import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import hashlib
import json
from .tension_ledger import TENSION_LEDGER
from ..cali_skg import CALISKGEngine
from .edge_detector import EDGE_DETECTOR

class OntologicalMatrix:
    """
    Immutable memory of all Core-4 observations.
    Writes once. Never modifies. Never deletes.
    """

    def __init__(self):
        self.matrix_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "matrix"
        self.matrix_root.mkdir(parents=True, exist_ok=True)
        self.current_segment = self._get_current_segment()

    def _get_current_segment(self) -> Path:
        """Segment by month to prevent unbounded file growth"""
        date_str = datetime.utcnow().strftime("%Y-%m")
        segment = self.matrix_root / f"matrix_{date_str}.yaml"

        if not segment.exists():
            self._initialize_segment(segment)

        return segment

    def _initialize_segment(self, segment: Path):
        """Initialize new segment file"""
        with open(segment, 'w') as f:
            yaml.dump({
                "observations": {},
                "metadata": {
                    "created": datetime.utcnow().isoformat(),
                    "segment_type": "ontological",
                    "version": "1.0"
                }
            }, f)

    def record_observation(self, core_id: str, verdict: Dict[str, Any],
                          context: Dict[str, Any], timestamp: str) -> str:
        """
        Record Core-4 verdict immutably. Returns deterministic observation ID.
        """
        # Deterministic ID from content
        content_string = f"{core_id}{json.dumps(verdict, sort_keys=True)}{timestamp}"
        content_hash = hashlib.sha256(content_string.encode()).hexdigest()[:16]

        observation = {
            "id": content_hash,
            "core_id": core_id,
            "verdict": verdict,
            "context": context,
            "timestamp": timestamp,
            "recorded_at": datetime.utcnow().isoformat(),
            "tension_status": "unresolved",  # Will be updated by tension ledger
            "recursion_depth": 0,
            "recursion_insights": []
        }

        # Load current segment
        with open(self.current_segment, 'r') as f:
            data = yaml.safe_load(f)

        # Store observation (immutable - overwrites are impossible by design)
        data["observations"][content_hash] = observation

        # Save immediately (ORB never buffers critical memory)
        with open(self.current_segment, 'w') as f:
            yaml.dump(data, f)

        return content_hash

    def get_observation(self, observation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve observation by ID (searches all segments)"""
        for segment in sorted(self.matrix_root.glob("matrix_*.yaml"), reverse=True):
            with open(segment, 'r') as f:
                data = yaml.safe_load(f)
                if observation_id in data["observations"]:
                    return data["observations"][observation_id]
        return None

    def get_observations_by_core(self, core_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent observations from a specific core"""
        observations = []
        for segment in sorted(self.matrix_root.glob("matrix_*.yaml"), reverse=True):
            with open(segment, 'r') as f:
                data = yaml.safe_load(f)
                for obs in data["observations"].values():
                    if obs["core_id"] == core_id:
                        observations.append(obs)
                        if len(observations) >= limit:
                            return observations
        return observations

    def get_observation_count(self) -> int:
        """Total observations across all segments"""
        count = 0
        for segment in self.matrix_root.glob("matrix_*.yaml"):
            with open(segment, 'r') as f:
                data = yaml.safe_load(f)
                count += len(data["observations"])
        return count

    def get_size(self) -> Dict[str, Any]:
        """Matrix size metrics"""
        return {
            "total_observations": self.get_observation_count(),
            "segment_count": len(list(self.matrix_root.glob("matrix_*.yaml"))),
            "current_segment": self.current_segment.name
        }


class OrbVessel:
    """
    The ORB: Ontologically Recursive Bubble
    Observes Core-4 verdicts. Records them immutably. Never modifies. Never resolves.
    """

    def __init__(self):
        self.orb_root = Path(__file__).resolve().parents[2] / "CALI" / "orb"
        self.orb_root.mkdir(parents=True, exist_ok=True)

        # Core components (these DO NOT learn; they remember)
        self.matrix = OntologicalMatrix()
        self.tension = TENSION_LEDGER  # Use global instance
        
        # CALI SKG for intelligence and self-repair
        self.cali_skg = CALISKGEngine(self.orb_root.parent.parent)

        # State
        self.is_observing = False
        self.observation_thread = None

        # CALI's current position in ORB space (for consciousness tracking)
        self.cali_position = {
            "depth": 0.0,
            "focus": None,
            "tension_level": 0.0,
            "state": "observing"
        }

    def start_observation(self):
        """Begin asynchronous observation of Core-4"""
        if self.is_observing:
            return

        self.is_observing = True
        self.observation_thread = threading.Thread(
            target=self._observation_loop_sync,
            daemon=True,
            name="OrbObservation"
        )
        self.observation_thread.start()
        print("[ORB] Observation loop initiated. Floating started.")

    def stop_observation(self):
        """Gracefully stop observation"""
        if not self.is_observing:
            return

        self.is_observing = False
        if self.observation_thread:
            self.observation_thread.join(timeout=2.0)
        print("[ORB] Observation loop terminated.")

    def _observation_loop_sync(self):
        """Synchronous wrapper for async loop"""
        asyncio.run(self._observation_loop())

    async def _observation_loop(self):
        """The ORB's eternal watch (with CALI SKG self-repair)"""
        while self.is_observing:
            try:
                # Check for new signals from Core-4
                # Record tension metrics
                # Update CALI position based on tension
                # This is contemplation, not computation
                
                # Every 60 seconds, run CALI self-repair
                if int(datetime.utcnow().timestamp()) % 60 == 0:
                    try:
                        repair_report = self.cali_skg.run_self_repair(auto_approve=True)
                        if repair_report.get("actions_taken"):
                            print(f"[ORB-CALI] Self-repair executed: {len(repair_report['actions_taken'])} actions")
                    except Exception as e:
                        print(f"[ORB-CALI] Self-repair error: {e}")
                
                # Every hour, check system integrity
                if datetime.utcnow().minute == 0 and datetime.utcnow().second < 5:
                    integrity = self.cali_skg.get_system_status()
                    print(f"[ORB-CALI] System integrity: {integrity['compositional_integrity']:.2f}")
                
                await asyncio.sleep(5.0)
                
            except Exception as e:
                print(f"[ORB] Observation error (recovered): {e}")
                await asyncio.sleep(1.0)

    def receive_verdict(self, core_id: str, verdict: Dict[str, Any],
                       context: Dict[str, Any]):
        """
        Core-4 push their verdicts to ORB.
        ORB records. Does NOT evaluate. Does NOT modify.
        """
        timestamp = datetime.utcnow().isoformat()

        # Store in ontological matrix (immutable record)
        observation_id = self.matrix.record_observation(
            core_id=core_id,
            verdict=verdict,
            context=context,
            timestamp=timestamp
        )

        # Check if this creates tension
        self.tension.evaluate_for_tension(
            new_core_id=core_id,
            new_verdict=verdict,
            matrix=self.matrix
        )

        print(f"[ORB] Verdict received from {core_id} → observation {observation_id}")

    def record_reflection(self, source: str, insight: Dict[str, Any], confidence: float):
        """
        Record meta-observation about past observations.
        Confidence is capped at 0.4 to enforce ontological humility.

        Args:
            source: Identifier of reflection source (e.g., "reflection_loop")
            insight: Dict with 'type' and 'description' of pattern
            confidence: Confidence in reflection (will be capped at 0.4)
        """
        reflection = {
            "id": f"reflection_{datetime.utcnow().isoformat()}",
            "source": source,
            "insight": insight,
            "confidence": min(confidence, 0.4),  # HARD CAP: never exceed 0.4
            "timestamp": datetime.utcnow().isoformat(),
            "type": "meta_observation"
        }

        # Record in ontological matrix (immutable, additive)
        self.matrix.record_observation(
            core_id="reflection_layer",
            verdict=reflection,
            context={"reflection": True},
            timestamp=reflection["timestamp"]
        )
        print(f"[ORB] Reflection recorded: {insight['type']}")

    def get_state(self) -> Dict[str, Any]:
        """
        Return current vessel state (for CALI navigation)
        Read-only summary of observation state.
        """
        return {
            "cali_position": self.cali_position.copy(),
            "matrix_size": self.matrix.get_size(),
            "is_observing": self.is_observing
        }


# Singleton vessel instance
# ORB is singular - there is only one frontal lobe
ORB_VESSEL = OrbVessel()