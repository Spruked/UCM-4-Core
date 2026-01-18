#!/usr/bin/env python3
# CALI/cooperative_advisory.py - Tier 2: Cooperative Arbitration

import json
import time
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from peer_awareness.orchestration import PeerAwarenessWorker

class CooperativeAdvisoryWorker:
    """
    CALI-mediated cooperative advisory system.
    Generates confidence-weighted recommendations for Core 4 coordination.
    No self-modification. No learning. Pure deterministic synthesis.
    """

    VERSION = "1.0.0"
    CONFIDENCE_CAP_TENSION = 0.75  # Memory 12: Cap under tension

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent  # UCM_4_Core/
        self.peer_worker = PeerAwarenessWorker()
        self.advisory_log = self.base_path / "CALI" / "cali_synthesis" / "vault" / "cooperative_log.jsonl"
        self.queue_file = self.base_path / "CALI" / "cali_synthesis" / "queue" / "advisory_queue.jsonl"

        # Ensure directories exist
        self.advisory_log.parent.mkdir(parents=True, exist_ok=True)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

    def load_peer_status(self) -> List[Dict]:
        """Load latest peer health snapshots from Tier 1"""
        try:
            # Run Tier 1 scan to get fresh data
            scan_result = self.peer_worker.run({"action": "scan"})

            if scan_result["status"] != "success":
                return []

            return scan_result.get("report", [])

        except Exception as e:
            return []

    def detect_stressed_peers(self, peer_status: List[Dict]) -> List[str]:
        """Deterministic threshold detection"""
        stressed = []
        for peer in peer_status:
            # Stress threshold: CPU > 85% or status == "stressed"
            cpu_load = peer.get("system_load", 0)
            status = peer.get("status", "unknown")

            if cpu_load > 85 or status == "stressed":
                stressed.append(peer["name"])

        return stressed

    def compute_confidence_weighted_consensus(self, peer_status: List[Dict]) -> float:
        """
        SoftMax-style confidence weighting.
        Peers with higher confidence contribute more to consensus.
        """
        if not peer_status:
            return 0.0

        total_load = 0.0
        total_confidence = 0.0

        for peer in peer_status:
            cpu_load = peer.get("system_load", 0)
            confidence = peer.get("confidence", 0.5)

            # Weighted contribution
            total_load += cpu_load * confidence
            total_confidence += confidence

        if total_confidence == 0:
            return 0.0

        # Consensus load is confidence-weighted average
        consensus_load = total_load / total_confidence

        # Normalize to 0.0-1.0
        return min(1.0, consensus_load / 100.0)

    def generate_advisory(self, peer_status: List[Dict]) -> Dict:
        """Generate confidence-weighted advisory action"""
        stressed_peers = self.detect_stressed_peers(peer_status)
        consensus_load = self.compute_confidence_weighted_consensus(peer_status)

        advisory = {
            "action": "none",
            "priority": "low",
            "confidence": 0.0,
            "reason": "System healthy",
            "immutable": True,
            "timestamp": time.time(),
            "peer_count": len(peer_status),
            "stressed_peer_count": len(stressed_peers),
            "advisory_source": "CALI_cooperative_arbitration",
            "protocol_version": self.VERSION
        }

        # Determine action based on consensus and stress
        if len(stressed_peers) >= 3:
            # Critical: Multiple peers stressed
            advisory["action"] = "emergency_scaling"
            advisory["priority"] = "critical"
            advisory["reason"] = f"Multiple peers stressed: {stressed_peers}"
            advisory["confidence"] = min(self.CONFIDENCE_CAP_TENSION, consensus_load)

        elif len(stressed_peers) >= 1:
            # High: At least one peer stressed
            advisory["action"] = "redistribute_tasks"
            advisory["priority"] = "high"
            advisory["reason"] = f"Stressed peers: {stressed_peers}"
            advisory["confidence"] = min(self.CONFIDENCE_CAP_TENSION, consensus_load)

        elif consensus_load > 0.70:
            # Medium: High load but no individual stress
            advisory["action"] = "health_check"
            advisory["priority"] = "medium"
            advisory["reason"] = f"High load consensus: {consensus_load:.1%}"
            advisory["confidence"] = min(self.CONFIDENCE_CAP_TENSION, consensus_load)

        # Cap confidence per Memory 12
        advisory["confidence"] = min(self.CONFIDENCE_CAP_TENSION, advisory["confidence"])

        # Add unique ID
        advisory["id"] = f"{advisory['action']}_{int(advisory['timestamp'])}"

        return advisory

    def log_advisory(self, advisory: Dict):
        """Append advisory to immutable log"""
        # Log to cooperative_advisory vault
        with open(self.advisory_log, 'a') as f:
            f.write(json.dumps({
                "timestamp": advisory["timestamp"],
                "category": "cooperative_advisory",
                "data": advisory,
                "confidence": advisory["confidence"],
                "immutable": True
            }) + '\n')

        # Also write to queue for DALS visibility
        with open(self.queue_file, 'a') as f:
            f.write(json.dumps(advisory) + '\n')

    def run(self, job_data: dict) -> dict:
        """DALS job entry point"""
        action = job_data.get('action', 'generate_advisory')

        if action == 'generate_advisory':
            # Load fresh peer status
            peer_status = self.load_peer_status()

            if not peer_status:
                return {
                    "status": "error",
                    "message": "No peer data available",
                    "advisory": None
                }

            # Generate advisory
            advisory = self.generate_advisory(peer_status)

            # Log immutably
            self.log_advisory(advisory)

            return {
                "status": "success",
                "advisory": advisory,
                "stressed_peers": self.detect_stressed_peers(peer_status),
                "consensus_load": self.compute_confidence_weighted_consensus(peer_status)
            }

        elif action == 'list_recent_advisories':
            # Return last N advisories for DALS UI
            count = job_data.get('count', 10)
            advisories = []

            if self.advisory_log.exists():
                with open(self.advisory_log, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        obs = json.loads(line)
                        if obs.get("category") == "cooperative_advisory":
                            advisories.append(obs["data"])

            return {
                "status": "success",
                "advisories": advisories[-count:]
            }

        elif action == 'approve_suggestion':
            # Handle suggestion approval/rejection
            suggestion_id = job_data.get('suggestion_id')
            approved = job_data.get('approved', False)
            user = job_data.get('approved_by') or job_data.get('rejected_by')

            if not suggestion_id:
                return {"status": "error", "message": "suggestion_id required"}

            # Find and update the suggestion in queue
            updated = False
            if self.queue_file.exists():
                with open(self.queue_file, 'r') as f:
                    lines = f.readlines()

                with open(self.queue_file, 'w') as f:
                    for line in lines:
                        if not line.strip():
                            continue
                        suggestion = json.loads(line.strip())

                        # Check if this is the suggestion to update
                        if suggestion.get('id') == suggestion_id:
                            suggestion['status'] = 'approved' if approved else 'rejected'
                            suggestion['reviewed_by'] = user
                            suggestion['reviewed_at'] = time.time()
                            suggestion['rationale'] = job_data.get('rationale', '')
                            updated = True

                        f.write(json.dumps(suggestion) + '\n')

            if updated:
                # Log the decision immutably
                decision_log = {
                    "timestamp": time.time(),
                    "suggestion_id": suggestion_id,
                    "decision": "approved" if approved else "rejected",
                    "decided_by": user,
                    "rationale": job_data.get('rationale', ''),
                    "immutable": True
                }

                with open(self.advisory_log, 'a') as f:
                    f.write(json.dumps({
                        "timestamp": decision_log["timestamp"],
                        "category": "suggestion_decision",
                        "data": decision_log,
                        "confidence": 1.0,
                        "immutable": True
                    }) + '\n')

                return {
                    "status": "success",
                    "decision": "approved" if approved else "rejected",
                    "suggestion_id": suggestion_id,
                    "reviewed_by": user
                }
            else:
                return {"status": "error", "message": f"Suggestion {suggestion_id} not found"}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def get_version(self):
        return self.VERSION

if __name__ == "__main__":
    # Test mode: Generate advisory from current peer state
    print("🔍 CALI Cooperative Advisory - Test Mode")
    print("=" * 50)

    worker = CooperativeAdvisoryWorker()
    result = worker.run({"action": "generate_advisory"})

    if result["status"] == "success":
        advisory = result["advisory"]
        print("\n🤖 Advisory Generated:")
        print(f"   Action: {advisory['action']}")
        print(f"   Priority: {advisory['priority']}")
        print(f"   Confidence: {advisory['confidence']:.2%}")
        print(f"   Reason: {advisory['reason']}")
        print("\n📊 Peer Consensus:")
        print(f"   Load: {result['consensus_load']:.2%}")
        print(f"🔴 Stressed Peers: {result['stressed_peers']}")
        print("\n✅ Advisory logged immutably to CALI vault")
    else:
        print(f"❌ Error: {result['message']}")