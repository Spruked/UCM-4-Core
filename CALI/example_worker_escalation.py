# Example worker escalation (from booklet_maker worker)
import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from CALI.integration.orb_bridge import trigger_worker_escalation

async def example_escalation():
    """Worker encounters user issue it cannot resolve"""

    # Worker context
    context = {
        "domain": "booklet_making",
        "current_step": "chapter_organization",
        "error_details": "User wants non-standard chapter ordering that violates schema",
        "user_intent": "Custom narrative flow for fiction",
        "worker_confidence": 0.3  # Low confidence triggers escalation
    }

    # User's query
    user_query = "Can I reorder chapters without breaking the booklet structure?"

    # Trigger ORB escalation
    result = await trigger_worker_escalation(
        worker_id="booklet_maker",
        user_query=user_query,
        context=context
    )

    print(f"[WORKER] Escalation result: {result['status']}")

    if result["status"] == "RESOLVED":
        print(f"[WORKER] ORB resolution: {result['verdict']['recommendation']}")
        print(f"[WORKER] Explanation: {result['explanation']}")

        # Worker implements ORB's guidance (doesn't have to, but chooses to)
        return result["verdict"]["recommendation"]

    elif result["status"] == "ESCALATED_TO_HUMAN":
        print(f"[WORKER] Human escalation triggered: {result['reason']}")

        # Worker informs user that human support is on the way
        return "Human support has been notified and will assist you shortly."

# Run example
if __name__ == "__main__":
    asyncio.run(example_escalation())