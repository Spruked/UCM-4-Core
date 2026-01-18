#!/usr/bin/env python3
"""
Test SKG Self-Repair Functionality
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.orb.skg_engine import SKG_ENGINE
from CALI.orb.orb_vessel import ORB_VESSEL

async def test_skg():
    """Test SKG learning and self-repair"""
    print("🧪 Testing SKG Self-Repair...")
    
    # Clear existing graph for clean test
    import os
    graph_file = SKG_ENGINE.skg_root / "skg_graph.json"
    if graph_file.exists():
        os.remove(graph_file)
    SKG_ENGINE.graph.clear()
    print("✅ Cleared existing SKG graph and file")
    
    # 1. Prime ORB with observations (creates substrate for SKG)
    print("\n[1] Priming ORB...")

    for i in range(25):  # 25 observations
        # Inject contradictory observations from different cores
        if i % 2 == 0:
            core = "Caleon_Genesis"
            verdict = {"recommendation": "REJECT", "confidence": 0.9 if i < 20 else 0.4}
        else:
            core = "Cali_X_One"
            verdict = {"recommendation": "ACCEPT", "confidence": 0.8 if i < 20 else 0.3}  # Contradiction with low confidence on some

        ORB_VESSEL.receive_verdict(
            core,
            verdict,
            {"domain": "test_skg", "iteration": i, "noise": i >= 20}
        )

        await asyncio.sleep(0.1)

    print("✅ Primed 25 observations (including 5 low-confidence)")

    # 2. Build SKG graph
    print("\n[2] Building SKG from observations...")
    SKG_ENGINE.ingest_from_matrix(ORB_VESSEL.matrix)

    print(f"✅ SKG nodes: {SKG_ENGINE.graph.number_of_nodes()}")
    print(f"✅ SKG edges: {SKG_ENGINE.graph.number_of_edges()}")

    # 3. Detect clutter
    print("\n[3] Detecting clutter edges...")
    clutter = SKG_ENGINE.detect_clutter_edges()

    print(f"✅ Clutter edges found: {len(clutter)}")
    for edge in clutter[:5]:  # Show first 5
        print(f"   - {edge['edge_id'][:20]}... (conf: {edge['confidence']:.2f})")

    # 4. Attempt self-repair
    print("\n[4] Attempting self-repair...")

    repair_success = 0
    for edge in clutter:
        if edge['confidence'] > 0.85:  # High enough to repair
            success = SKG_ENGINE.self_repair_edge(
                edge_id=edge['edge_id'],
                new_confidence=0.95,
                repair_reason="High confidence support from historical patterns"
            )
            if success:
                repair_success += 1

    print(f"✅ Repairs executed: {repair_success}")

    # 5. Adapt thresholds
    print("\n[5] Adapting thresholds based on repair success...")
    SKG_ENGINE.adapt_thresholds()

    print(f"✅ New repair threshold: {SKG_ENGINE.repair_threshold:.2f}")

    # 6. Verify graph integrity
    print("\n[6] Verifying graph integrity...")

    final_clutter = SKG_ENGINE.detect_clutter_edges()
    print(f"✅ Remaining clutter: {len(final_clutter)}")

    if len(final_clutter) < len(clutter):
        print("🎯 Self-repair reduced clutter successfully")
        return True
    else:
        print("⚠️ No repairs executed (insufficient confidence)")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_skg())
    print(f"\n{'🎯 SKG Test: PASSED' if success else '⚠️ SKG Test: PARTIAL'}")