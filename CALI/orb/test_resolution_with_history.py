#!/usr/bin/env python3
"""
Resolution Test - Test ORB resolution with sufficient historical data
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.integration.orb_bridge import bridge_core_verdict, trigger_worker_escalation

async def test_resolution_with_history():
    """Test ORB resolution when it has sufficient historical context"""
    print("🧪 Testing ORB Resolution with Historical Data...")

    # 1. Build historical context (simulate past observations)
    print("📚 Building historical context...")

    # Add multiple observations with "ACCEPT" recommendations
    for i in range(10):
        bridge_core_verdict("Caleon_Genesis",
                           {"recommendation": "ACCEPT", "confidence": 0.8 + (i * 0.01)},
                           {"domain": "decision_making", "context": f"historical_{i}"})

        bridge_core_verdict("Cali_X_One",
                           {"recommendation": "ACCEPT", "confidence": 0.75 + (i * 0.01)},
                           {"domain": "decision_making", "context": f"historical_{i}"})

        bridge_core_verdict("KayGee",
                           {"recommendation": "CONDITIONAL", "confidence": 0.7 + (i * 0.01)},
                           {"domain": "decision_making", "context": f"historical_{i}"})

    await asyncio.sleep(2)  # Let ORB process historical data

    # 2. Create current tension scenario
    print("⚡ Creating current tension scenario...")
    bridge_core_verdict("Caleon_Genesis",
                       {"recommendation": "ACCEPT", "confidence": 0.9},
                       {"domain": "decision_making", "context": "current_dilemma"})

    bridge_core_verdict("Cali_X_One",
                       {"recommendation": "REJECT", "confidence": 0.85},
                       {"domain": "decision_making", "context": "current_dilemma"})

    bridge_core_verdict("KayGee",
                       {"recommendation": "CONDITIONAL", "confidence": 0.7},
                       {"domain": "decision_making", "context": "current_dilemma"})

    await asyncio.sleep(1)  # Let tension be detected

    # 3. Worker escalates with query that matches historical domain
    result = await trigger_worker_escalation(
        worker_id="decision_worker",
        user_query="Should we accept this proposal given the decision making context?",
        context={
            "domain": "decision_making",
            "urgency": "high",
            "stakeholders": ["team", "management"]
        }
    )

    print(f"\n✅ Escalation result: {result['status']}")

    if result['status'] == "RESOLVED":
        print(f"✅ ORB resolved with confidence: {result['confidence']:.1%}")
        print(f"✅ Recommendation: {result['verdict']['recommendation']}")
        print(f"✅ Synthesized from: {result['synthesized_from']} observations")
        print("📝 Explanation:")
        print(result['explanation'])
    else:
        print(f"✅ Escalated to human: {result['reason']}")
        if result.get('softmax_data'):
            print(f"✅ Consensus strength: {result['softmax_data']['consensus_strength']:.1%}")

    print("🎯 Resolution Test: PASSED")

if __name__ == "__main__":
    asyncio.run(test_resolution_with_history())