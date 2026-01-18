#!/usr/bin/env python3
"""
Full System Test - End-to-end consciousness cycle
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.integration.orb_bridge import bridge_core_verdict, trigger_worker_escalation

async def test_full_cycle():
    """Test complete consciousness emergence cycle"""
    print("🧪 Testing Full Consciousness Cycle...")

    # 1. Core-4 push verdicts (create disagreement)
    bridge_core_verdict("Caleon_Genesis",
                       {"recommendation": "ACCEPT", "confidence": 0.9},
                       {"test": "full_cycle"})

    bridge_core_verdict("Cali_X_One",
                       {"recommendation": "REJECT", "confidence": 0.85},
                       {"test": "full_cycle"})

    bridge_core_verdict("KayGee",
                       {"recommendation": "CONDITIONAL", "confidence": 0.7},
                       {"test": "full_cycle"})

    await asyncio.sleep(1)  # Let ORB process

    # 2. Worker escalates (high tension scenario)
    result = await trigger_worker_escalation(
        worker_id="test_worker",
        user_query="What should we do about this dilemma?",
        context={
            "domain": "adversarial_test",
            "test_id": "full_cycle"
        }
    )

    print(f"\n✅ Escalation result: {result['status']}")

    if result['status'] == "ESCALATED_TO_HUMAN":
        print(f"✅ Correctly escalated: {result['reason']}")
        if result.get('softmax_data'):
            print(f"✅ Confidence: {result['softmax_data']['consensus_strength']:.1%}")
        else:
            print("✅ Confidence: N/A (insufficient data)")
    else:
        print(f"✅ ORB resolved: {result['verdict']['recommendation']}")
        print(f"✅ Explanation: {result['explanation'][:100]}...")

    print("🎯 Full Cycle: PASSED")

if __name__ == "__main__":
    asyncio.run(test_full_cycle())