#!/usr/bin/env python3
# peer_awareness/orchestration.py - Tier 1: Situational Awareness

import psutil
import time
import json
from pathlib import Path
from typing import Dict, List
import hashlib
import os

class PeerAwarenessVault:
    """Simple vault for peer observations - integrates with unified_vault"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.vault_path.exists():
            with open(self.vault_path, 'w') as f:
                json.dump([], f)

    def add_observation(self, category: str, data: Dict, confidence: float, immutable: bool = True):
        """Add observation to vault"""
        try:
            with open(self.vault_path, 'r') as f:
                vault_data = json.load(f)
        except:
            vault_data = []

        observation = {
            "timestamp": time.time(),
            "core_id": "peer_awareness",
            "data_type": category,
            "data": data,
            "confidence": confidence,
            "immutable": immutable,
            "vault_hash": hash(str(data))
        }

        vault_data.append(observation)

        with open(self.vault_path, 'w') as f:
            json.dump(vault_data, f, indent=2)

class PeerAwarenessWorker:
    """
    Deterministic peer monitoring for Core 4
    No self-modification, no learning, pure observation
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent  # UCM_4_Core/
        self.vault = PeerAwarenessVault(self.base_path / "unified_vault" / "peer_observations.json")
        self.peers = ["KayGee_1.0", "Caleon_Genesis_1.12", "Cali_X_One", "UCM_Core_ECM"]

    def observe_peer(self, peer_name: str) -> Dict:
        """Read-only health snapshot"""
        try:
            # Check if peer directory exists (basic health indicator)
            peer_path = self.base_path / peer_name.replace(".", "_").replace("_1", "_1.")
            directory_exists = peer_path.exists()

            # System resource check (simulating peer load)
            load = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent

            # Check for recent activity (file modification times)
            recent_activity = False
            if directory_exists:
                try:
                    # Check if any files modified in last hour
                    for root, dirs, files in os.walk(peer_path):
                        for file in files:
                            file_path = Path(root) / file
                            if file_path.stat().st_mtime > time.time() - 3600:  # 1 hour
                                recent_activity = True
                                break
                        if recent_activity:
                            break
                except:
                    pass

            status = "healthy"
            if load > 80 or memory > 85:
                status = "stressed"
            elif not directory_exists:
                status = "offline"
            elif not recent_activity:
                status = "idle"

            return {
                "name": peer_name,
                "timestamp": time.time(),
                "system_load": load,
                "memory_usage": memory,
                "directory_exists": directory_exists,
                "recent_activity": recent_activity,
                "status": status,
                "confidence": 0.90 if directory_exists else 0.50
            }
        except Exception as e:
            return {
                "name": peer_name,
                "timestamp": time.time(),
                "error": str(e),
                "status": "unknown",
                "confidence": 0.10
            }

    def scan_all_peers(self) -> List[Dict]:
        """Generate health report for all siblings"""
        report = []
        for peer in self.peers:
            snapshot = self.observe_peer(peer)
            report.append(snapshot)

            # Log immutable observation to vault
            self.vault.add_observation(
                category="peer_health",
                data=snapshot,
                confidence=snapshot["confidence"],
                immutable=True
            )

        return report

    def detect_stressed_peers(self, report: List[Dict]) -> List[str]:
        """Deterministic threshold detection"""
        stressed = []
        for peer in report:
            if peer["status"] in ["stressed", "offline"] and peer["confidence"] > 0.75:
                stressed.append(peer["name"])

        return stressed

    def run(self, job_data: dict) -> dict:
        """Entry point for peer awareness scanning"""
        action = job_data.get('action', 'scan')

        if action == 'scan':
            report = self.scan_all_peers()
            stressed = self.detect_stressed_peers(report)

            return {
                "status": "success",
                "report": report,
                "stressed_peers": stressed,
                "recommendation": "redistribute_tasks" if stressed else "none",
                "timestamp": time.time()
            }

        elif action == 'observe':
            peer_name = job_data.get('peer_name')
            if not peer_name:
                return {"status": "error", "message": "peer_name required for observe action"}

            snapshot = self.observe_peer(peer_name)
            return {
                "status": "success",
                "observation": snapshot
            }

        return {"status": "error", "message": "Unknown action"}

if __name__ == "__main__":
    worker = PeerAwarenessWorker()
    result = worker.run({"action": "scan"})
    print(json.dumps(result, indent=2))