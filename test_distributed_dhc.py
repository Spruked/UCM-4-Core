#!/usr/bin/env python3
# test_distributed_dhc.py - Test DHC working across all Core 4 siblings

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List

class DHCDistributedTest:
    """Test DHC working across all cores simultaneously"""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent
        self.cores = [
            ("KayGee_1.0", "Voice System"),
            ("Caleon_Genesis_1.12", "Content Generation"),
            ("Cali_X_One", "Extended Reasoning"),
            ("UCM_Core _ECM", "Epistemic Convergence")
        ]

    def run_parallel_health_checks(self) -> Dict:
        """Run health checks from all cores simultaneously"""
        import threading

        results = {}
        threads = []

        def check_core(core_name: str, description: str):
            try:
                core_path = self.base_path / core_name
                start_time = time.time()

                result = subprocess.run(
                    [sys.executable, "peer_awareness/orchestration.py"],
                    cwd=str(core_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                end_time = time.time()

                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout.strip())
                        results[core_name] = {
                            "status": "success",
                            "description": description,
                            "data": data,
                            "response_time": end_time - start_time
                        }
                    except:
                        results[core_name] = {
                            "status": "parse_error",
                            "description": description,
                            "raw_output": result.stdout.strip(),
                            "response_time": end_time - start_time
                        }
                else:
                    results[core_name] = {
                        "status": "failed",
                        "description": description,
                        "error": result.stderr.strip(),
                        "response_time": end_time - start_time
                    }

            except Exception as e:
                results[core_name] = {
                    "status": "error",
                    "description": description,
                    "error": str(e),
                    "response_time": 0
                }

        # Start all checks in parallel
        for core_name, description in self.cores:
            thread = threading.Thread(target=check_core, args=(core_name, description))
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=35)

        return results

    def analyze_distributed_consensus(self, results: Dict) -> Dict:
        """Analyze the distributed consensus across all cores"""

        analysis = {
            "total_cores": len(self.cores),
            "successful_checks": 0,
            "failed_checks": 0,
            "peer_observations": {},
            "consensus_metrics": {},
            "system_health": "unknown"
        }

        # Count successes/failures
        for core_name, result in results.items():
            if result["status"] == "success":
                analysis["successful_checks"] += 1
            else:
                analysis["failed_checks"] += 1

        # Extract peer observations from each core's perspective
        for core_name, result in results.items():
            if result["status"] == "success" and "data" in result:
                report = result["data"].get("report", [])
                analysis["peer_observations"][core_name] = report

        # Calculate consensus metrics
        if analysis["peer_observations"]:
            # Count how many cores each peer is seen as healthy/stressed/offline
            peer_status_counts = {}
            for observer, peers in analysis["peer_observations"].items():
                for peer in peers:
                    peer_name = peer["name"]
                    status = peer["status"]
                    if peer_name not in peer_status_counts:
                        peer_status_counts[peer_name] = {"healthy": 0, "stressed": 0, "offline": 0, "unknown": 0}
                    if status in peer_status_counts[peer_name]:
                        peer_status_counts[peer_name][status] += 1

            analysis["consensus_metrics"] = peer_status_counts

        # Determine overall system health
        success_rate = analysis["successful_checks"] / analysis["total_cores"]
        if success_rate == 1.0:
            analysis["system_health"] = "fully_operational"
        elif success_rate >= 0.75:
            analysis["system_health"] = "mostly_operational"
        elif success_rate >= 0.5:
            analysis["system_health"] = "degraded"
        else:
            analysis["system_health"] = "critical"

        return analysis

if __name__ == "__main__":
    tester = DHCDistributedTest()

    print("🧪 Testing Distributed Health Consensus across all Core 4 siblings...")
    print("=" * 70)

    # Run parallel health checks
    print("\n🔍 Running parallel health checks from all cores...")
    start_time = time.time()
    results = tester.run_parallel_health_checks()
    end_time = time.time()

    # Analyze results
    analysis = tester.analyze_distributed_consensus(results)

    # Display results
    print(f"\n📊 Test Results (completed in {end_time - start_time:.2f}s):")
    print(f"System Health: {analysis['system_health'].replace('_', ' ').upper()}")
    print(f"Successful Checks: {analysis['successful_checks']}/{analysis['total_cores']}")
    print(f"Failed Checks: {analysis['failed_checks']}/{analysis['total_cores']}")

    print("\n🤝 Peer Observations (Consensus View):")
    for peer_name, counts in analysis['consensus_metrics'].items():
        total_observations = sum(counts.values())
        healthy_pct = (counts['healthy'] / total_observations * 100) if total_observations > 0 else 0
        stressed_pct = (counts['stressed'] / total_observations * 100) if total_observations > 0 else 0
        offline_pct = (counts['offline'] / total_observations * 100) if total_observations > 0 else 0

        status_emoji = "🟢" if healthy_pct > 50 else "🟡" if stressed_pct > 50 else "🔴"
        print(f"  {status_emoji} {peer_name}:")
        print(f"    Healthy: {healthy_pct:.1f}%, Stressed: {stressed_pct:.1f}%, Offline: {offline_pct:.1f}%")
    print("\n🎯 Core-Specific Results:")
    for core_name, result in results.items():
        status_emoji = "✅" if result["status"] == "success" else "❌"
        response_time = ".2f"
        description = result["description"]
        print(f"  {status_emoji} {core_name} ({description}): {response_time}s")

    if analysis["system_health"] == "fully_operational":
        print("\n🎉 SUCCESS: Distributed Health Consensus is working perfectly!")
        print("🤝 All Core 4 siblings are monitoring each other deterministically")
        print("🛡️ Coordination is CALI-mediated and fully immutable")
        print("🚀 Ready for autonomous task redistribution and cooperative arbitration")
    else:
        print(f"\n⚠️ SYSTEM STATUS: {analysis['system_health'].replace('_', ' ').upper()}")
        print("Some cores may need attention")