#!/usr/bin/env python3
"""
Test Resolution Path (Not Escalation)
Prime ORB with historical data, then verify synthesis
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.integration.orb_bridge import bridge_core_verdict, trigger_worker_escalation

async def test_resolution_path():
    """Test that ORB resolves when confidence is high"""
    print("🧪 Testing Resolution Path (High Confidence Scenario)")

    # 1. PRIME: Feed ORB 20 observations about "booklet chapter ordering"
    print("\n[PRIMING] Feeding ORB historical observations...")

    for i in range(20):
        # 80% of observations show "CONDITIONAL" is the right answer
        if i < 16:
            verdict = {"recommendation": "CONDITIONAL", "confidence": 0.85}
        else:
            verdict = {"recommendation": "ACCEPT", "confidence": 0.6}

        bridge_core_verdict(
            "Caleon_Genesis",
            verdict,
            {"domain": "booklet_ordering", "scenario": "chapter_flow", "prime_id": i}
        )

        await asyncio.sleep(0.1)  # Small delay between injections

    print(f"✅ Primed {20} observations")

    # 2. QUERY: Submit similar query
    print("\n[QUERY] Submitting similar query...")

    result = await trigger_worker_escalation(
        worker_id="booklet_maker",
        user_query="How should I order chapters for optimal narrative flow?",
        context={
            "domain": "booklet_ordering",
            "scenario": "chapter_flow",  # Same scenario as priming
            "user_intent": "optimal_flow"
        }
    )

    # 3. VERIFY: Should RESOLVE, not escalate
    print(f"\n📊 Result:")
    print(f"   Status: {result['status']}")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")

    if result["status"] == "RESOLVED":
        print(f"✅ ORB RESOLVED (did not escalate)")
        print(f"   Recommendation: {result['verdict']['recommendation']}")
        print(f"   Explanation: {result['explanation'][:100]}...")
        print(f"   Synthesized from {result['synthesized_from']} observations")

        # Verify confidence is high (> 0.6)
        assert result["confidence"] > 0.6, "Confidence should be high with primed data"

        print("🎯 Resolution Path: PASSED")
        return True

    else:
        print(f"❌ Unexpected escalation: {result['reason']}")
        print("This suggests priming didn't create sufficient confidence")
        return False

if __name__ == "__main__":
    asyncio.run(test_resolution_path())