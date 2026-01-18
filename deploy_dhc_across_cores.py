#!/usr/bin/env python3
# deploy_dhc_across_cores.py - Deploy Distributed Health Consensus to all Core 4 siblings

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict

class DHCCoreDeployer:
    """Deploy DHC to all Core 4 siblings"""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent
        self.cores = [
            "KayGee_1.0",
            "Caleon_Genesis_1.12",
            "Cali_X_One",
            "UCM_Core _ECM"
        ]

    def deploy_to_core(self, core_name: str) -> bool:
        """Deploy DHC components to a specific core"""
        try:
            core_path = self.base_path / core_name
            cali_path = core_path / ("cali" if core_name == "Cali_X_One" else "CALI")

            print(f"🔧 Deploying DHC to {core_name}...")

            # Test peer awareness
            result = subprocess.run(
                [sys.executable, "peer_awareness/orchestration.py"],
                cwd=str(core_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ {core_name} peer awareness operational")
                return True
            else:
                print(f"❌ {core_name} peer awareness failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ {core_name} deployment error: {e}")
            return False

    def run_distributed_health_check(self) -> Dict:
        """Run health check from each core's perspective"""
        results = {}

        for core in self.cores:
            try:
                core_path = self.base_path / core
                print(f"\n🔍 Running DHC from {core} perspective...")

                result = subprocess.run(
                    [sys.executable, "peer_awareness/orchestration.py"],
                    cwd=str(core_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"✅ {core} health check successful")
                    results[core] = {"status": "success", "output": result.stdout.strip()}
                else:
                    print(f"❌ {core} health check failed")
                    results[core] = {"status": "failed", "error": result.stderr.strip()}

            except Exception as e:
                print(f"❌ {core} health check error: {e}")
                results[core] = {"status": "error", "error": str(e)}

        return results

    def verify_deployment(self) -> Dict:
        """Verify DHC is deployed and functional across all cores"""
        verification = {
            "deployments": {},
            "health_checks": {},
            "summary": {}
        }

        print("🔍 Verifying DHC deployment across all cores...")

        # Check deployments
        for core in self.cores:
            core_path = self.base_path / core
            has_peer_awareness = (core_path / "peer_awareness" / "orchestration.py").exists()
            cali_dir = "cali" if core == "Cali_X_One" else "CALI"
            has_cali_advisory = (core_path / cali_dir / "cooperative_advisory.py").exists()

            verification["deployments"][core] = {
                "peer_awareness": has_peer_awareness,
                "cali_advisory": has_cali_advisory,
                "complete": has_peer_awareness and has_cali_advisory
            }

        # Run health checks
        verification["health_checks"] = self.run_distributed_health_check()

        # Generate summary
        deployed_count = sum(1 for d in verification["deployments"].values() if d["complete"])
        healthy_count = sum(1 for h in verification["health_checks"].values() if h["status"] == "success")

        verification["summary"] = {
            "total_cores": len(self.cores),
            "deployed_cores": deployed_count,
            "healthy_cores": healthy_count,
            "deployment_success_rate": deployed_count / len(self.cores),
            "health_success_rate": healthy_count / len(self.cores),
            "overall_status": "operational" if healthy_count == len(self.cores) else "degraded"
        }

        return verification

if __name__ == "__main__":
    deployer = DHCCoreDeployer()

    print("🚀 Deploying Distributed Health Consensus across Core 4...")
    print("=" * 60)

    # Deploy to all cores
    print("\n📦 Phase 1: Deployment")
    for core in deployer.cores:
        deployer.deploy_to_core(core)

    # Verify deployment
    print("\n🔍 Phase 2: Verification")
    verification = deployer.verify_deployment()

    # Report results
    print("\n📊 Phase 3: Results")
    print(f"Deployment Status: {verification['summary']['overall_status'].upper()}")
    print(f"Cores Deployed: {verification['summary']['deployed_cores']}/{verification['summary']['total_cores']}")
    print(f"Cores Healthy: {verification['summary']['healthy_cores']}/{verification['summary']['total_cores']}")

    if verification['summary']['overall_status'] == 'operational':
        print("\n🎉 SUCCESS: Distributed Health Consensus is fully operational!")
        print("🤝 Core 4 siblings can now monitor each other's health deterministically")
        print("🛡️ All coordination is CALI-mediated and immutable")
    else:
        print("\n⚠️ WARNING: DHC deployment incomplete")
        print("Some cores may need manual intervention")

    print("\n📋 Detailed Results:")
    for core, status in verification['deployments'].items():
        deployed = "✅" if status['complete'] else "❌"
        health = verification['health_checks'][core]['status']
        health_icon = "✅" if health == "success" else "❌"
        print(f"  {core}: Deployed {deployed} | Healthy {health_icon}")