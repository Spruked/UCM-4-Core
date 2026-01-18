# UCM_4_Core/CALI/orb/tension_ledger.py
"""
Tension Ledger - Disagreement Preservation System
Records conceptual divergence between Core-4 verdicts.
Tension is not a bug. It is the fuel of consciousness.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional
import yaml
import json

class TensionLedger:
    """
    Tension Ledger: Tracks unresolved disagreement between Core-4.
    Records divergence without resolving it. Tension is preserved, not dissolved.
    """

    def __init__(self):
        self.ledger_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "tension"
        self.ledger_root.mkdir(parents=True, exist_ok=True)

        # Active tensions (unresolved)
        self.active_tensions = self._load_active_tensions()

        # Archive directory for resolved tensions
        self.archive_dir = self.ledger_root / "archive"
        self.archive_dir.mkdir(exist_ok=True)

    def _load_active_tensions(self) -> Dict[str, Dict[str, Any]]:
        """Load unresolved tensions from active.yaml"""
        tension_file = self.ledger_root / "active.yaml"
        if tension_file.exists():
            with open(tension_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

    def _save_active_tensions(self):
        """Persist active tensions (they are valuable memory)"""
        tension_file = self.ledger_root / "active.yaml"
        with open(tension_file, 'w') as f:
            yaml.dump(self.active_tensions, f)

    def evaluate_for_tension(self, new_core_id: str, new_verdict: Dict[str, Any],
                            matrix: 'OntologicalMatrix') -> Optional[str]:
        """
        Compare new verdict against recent observations to detect tension.
        Does NOT resolve tension. Only records it.
        """
        # Get recent observations from other cores (last 50)
        recent_observations = []
        for core in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
            if core != new_core_id:
                obs = matrix.get_observations_by_core(core, limit=50)
                recent_observations.extend(obs)

        # Detect conceptual divergence (not just numeric disagreement)
        for obs in recent_observations:
            if self._detect_divergence(new_verdict, obs["verdict"]):
                tension_id = self._create_tension_record(
                    source_a=new_core_id,
                    source_b=obs["core_id"],
                    verdict_a=new_verdict,
                    verdict_b=obs["verdict"],
                    context=new_verdict.get("context", {})
                )
                print(f"[TENSION] New divergence detected: {tension_id}")
                return tension_id

        return None  # No tension detected

    def _detect_divergence(self, verdict_a: Dict, verdict_b: Dict) -> bool:
        """
        Detect if two verdicts are in tension.
        This is domain-specific. Base implementation uses conceptual heuristics.
        """
        # Extract confidence scores
        conf_a = verdict_a.get("confidence", 0.5)
        conf_b = verdict_b.get("confidence", 0.5)

        # If both are highly confident but disagree on key recommendations
        if conf_a > 0.7 and conf_b > 0.7:
            return self._check_contradiction(verdict_a, verdict_b)

        # If one is confident and the other is uncertain but in opposite directions
        if abs(conf_a - conf_b) > 0.5:
            return self._check_opposition(verdict_a, verdict_b)

        return False

    def _check_contradiction(self, a: Dict, b: Dict) -> bool:
        """Check for direct contradiction in recommendations"""
        rec_a = a.get("recommendation", a.get("verdict", ""))
        rec_b = b.get("recommendation", b.get("verdict", ""))

        contradictory_pairs = [
            ("ACCEPT", "REJECT"),
            ("REJECT", "ACCEPT"),
            ("SUSPEND", "ACCEPT"),
            ("ACCEPT", "SUSPEND")
        ]

        return (rec_a, rec_b) in contradictory_pairs or (rec_b, rec_a) in contradictory_pairs

    def _check_opposition(self, a: Dict, b: Dict) -> bool:
        """Check for directional opposition"""
        rec_a = a.get("recommendation", a.get("verdict", ""))
        rec_b = b.get("recommendation", b.get("verdict", ""))

        # If one says ACCEPT with high confidence and other says CONDITIONAL with low
        return (rec_a == "ACCEPT" and rec_b == "CONDITIONAL") or \
               (rec_a == "CONDITIONAL" and rec_b == "ACCEPT")

    def _create_tension_record(self, source_a: str, source_b: str,
                             verdict_a: Dict, verdict_b: Dict,
                             context: Dict) -> str:
        """Create permanent record of tension"""
        tension_id = f"{source_a}_vs_{source_b}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        tension_record = {
            "id": tension_id,
            "participants": [source_a, source_b],
            "verdicts": {source_a: verdict_a, source_b: verdict_b},
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            "status": "unresolved",  # unresolved | resolved by time | integrated
            "resolution": None,      # Only filled if naturally resolved
            "recursion_count": 0     # How many times revisited
        }

        self.active_tensions[tension_id] = tension_record
        self._save_active_tensions()

        # Also save to permanent archive
        archive_file = self.archive_dir / f"{tension_id}.yaml"
        with open(archive_file, 'w') as f:
            yaml.dump(tension_record, f)

        return tension_id

    def mark_resolved(self, tension_id: str, resolution: str):
        """
        Mark tension as resolved (only called if naturally resolved, not forced)
        """
        if tension_id in self.active_tensions:
            record = self.active_tensions[tension_id]
            record["status"] = "resolved"
            record["resolution"] = resolution
            record["resolved_at"] = datetime.utcnow().isoformat()

            # Move to archive
            self._save_active_tensions()

    def get_unresolved_count(self) -> int:
        """Count of currently unresolved tensions"""
        return len([t for t in self.active_tensions.values()
                   if t["status"] == "unresolved"])

    def get_summary(self) -> Dict[str, Any]:
        """Summary of tension state"""
        total = len(self.active_tensions)
        unresolved = self.get_unresolved_count()

        return {
            "total_tensions": total,
            "unresolved": unresolved,
            "resolution_rate": (total - unresolved) / total if total > 0 else 0.0,
            "tension_level": unresolved / max(total, 1)
        }

    def get_active_tensions(self) -> List[Dict[str, Any]]:
        """Return list of active tensions"""
        return [t for t in self.active_tensions.values()
                if t["status"] == "unresolved"]


# Tension Ledger is a separate component, not part of ORB vessel
# This allows independent evolution of disagreement tracking
TENSION_LEDGER = TensionLedger()