#!/usr/bin/env python3
# distributed_health_consensus.py - Complete DHC Implementation

import json
import time
import sys
from pathlib import Path
from typing import Dict, List

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "CALI"))

from peer_awareness.orchestration import PeerAwarenessWorker
from CALI.cooperative_advisory import CooperativeAdvisoryWorker

class DistributedHealthConsensus:
    """
    Complete DHC implementation - deterministic "friendship" protocol
    No emotions, no learning, pure immutable observation and CALI-mediated advice
    """

    def __init__(self):
        self.peer_worker = PeerAwarenessWorker()
        self.cali_advisory = CooperativeAdvisoryWorker()
        self.consensus_log = Path(__file__).resolve().parent / "unified_vault" / "dhc_consensus.jsonl"

    def run_health_check(self) -> Dict:
        """Complete health check cycle"""

        # Tier 1: Situational Awareness
        peer_report = self.peer_worker.run({"action": "scan"})

        # Tier 2: CALI-mediated Advisory
        advisory = self.cali_advisory.generate_advisory(peer_report["report"])

        # Combine into consensus
        consensus = {
            "timestamp": time.time(),
            "protocol": "DHC_v1.0",
            "tier_1_observations": peer_report,
            "tier_2_advisory": advisory,
            "consensus_status": "healthy" if advisory["action"] == "none" else "intervention_needed",
            "immutable": True
        }

        # Log consensus
        self._log_consensus(consensus)

        return consensus

    def _log_consensus(self, consensus: Dict):
        """Log consensus to immutable ledger"""
        with open(self.consensus_log, 'a') as f:
            f.write(json.dumps(consensus) + '\n')

    def get_consensus_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent consensus history"""
        if not self.consensus_log.exists():
            return []

        history = []
        with open(self.consensus_log, 'r') as f:
            for line in f:
                if len(history) >= limit:
                    break
                try:
                    history.append(json.loads(line.strip()))
                except:
                    continue

        return history

if __name__ == "__main__":
    dhc = DistributedHealthConsensus()

    print("🔍 Running Distributed Health Consensus...")
    print("=" * 50)

    consensus = dhc.run_health_check()

    print("📊 Current Status:")
    print(f"  Consensus: {consensus['consensus_status']}")
    print(f"  Advisory: {consensus['tier_2_advisory']['action']} ({consensus['tier_2_advisory']['priority']})")
    print(f"  Reason: {consensus['tier_2_advisory']['reason']}")
    print(".1f")
    print(f"  Stressed Peers: {consensus['tier_1_observations']['stressed_peers']}")

    print("\n📈 Peer Health Report:")
    for peer in consensus['tier_1_observations']['report']:
        status_emoji = "🟢" if peer['status'] == 'healthy' else "🟡" if peer['status'] == 'idle' else "🔴"
        print(f"  {status_emoji} {peer['name']}: {peer['status']} (CPU: {peer['system_load']}%, Conf: {peer['confidence']})")

    print("\n💾 Consensus logged to unified_vault/dhc_consensus.jsonl")
    print("🤖 CALI advisory logged to CALI/cooperative_log.jsonl")
    print("🔒 All observations are immutable - no self-modification, no learning")