#!/usr/bin/env python3
"""
Test CALI SKG Self-Repair functionality
"""

from CALI.cali_skg import CALISKGEngine
from pathlib import Path

def test_self_repair():
    print("🔬 Testing CALI SKG Self-Repair functionality...")

    try:
        # Initialize CALI with self-repair
        cali = CALISKGEngine(Path("."))
        print("✅ CALI SKG initialized with self-repair capabilities")

        # Manually add some problematic edges to test detection
        print("\n🧪 Adding test edges for clutter detection...")

        # Add redundant edges (same relationship type between same nodes with different values)
        cali.kg.add_edge("test_node_1", "test_node_2",
                         relationship="connects_to", importance=0.1)
        cali.kg.add_edge("test_node_1", "test_node_2",
                         relationship="connects_to", importance=0.9)  # Same relationship, higher value

        # Add conflicting edges (direct contradictions)
        cali.kg.add_edge("test_node_3", "test_node_4",
                         relationship="enables", importance=0.8)
        cali.kg.add_edge("test_node_3", "test_node_4",
                         relationship="inhibits", importance=0.7)  # Direct conflict on same edge

        # Add very low-value edge (will be below threshold)
        cali.kg.add_edge("test_node_5", "test_node_6",
                         relationship="weak_connection", importance=0.0)

        print(f"Knowledge graph now has {len(cali.kg.nodes())} nodes and {len(cali.kg.edges())} edges")

        # Run clutter detection
        print("\n🔍 Detecting clutter...")
        report = cali.detect_edge_clutter()
        print(f"Found {report['clutter_found']} problematic edges")
        print(f"Integrity impact: {report['integrity_impact']:.2f}")
        print(f"Redundant edges: {len(report['redundant_edges'])}")
        print(f"Conflicting edges: {len(report['conflicting_edges'])}")
        print(f"Low-value edges: {len(report['low_value_edges'])}")

        # Run self-repair (without auto-approval)
        print("\n🔧 Running self-repair...")
        repair_report = cali.run_self_repair(auto_approve=False)
        print(f"Actions requiring approval: {len(repair_report['actions_pending_approval'])}")
        print(f"Actions executed: {len(repair_report['actions_taken'])}")
        print(f"Integrity before: {repair_report['integrity_before']:.2f}")
        print(f"Integrity after: {repair_report['integrity_after']:.2f}")

        # Show pending actions
        if repair_report["actions_pending_approval"]:
            print("\n📋 Pending repair actions:")
            for action in repair_report["actions_pending_approval"]:
                print(f"  - {action['severity'].upper()}: {action['description']}")

        # View repair statistics
        print("\n📊 Repair Statistics:")
        stats = cali.get_repair_statistics()
        for key, value in stats.items():
            if key.startswith(('clutter_', 'edges_', 'redundant_', 'integrity_', 'repairs_')):
                print(f"  {key}: {value}")

        # Test auto-approve repair
        print("\n🔧 Running self-repair with auto-approval...")
        auto_repair_report = cali.run_self_repair(auto_approve=True)
        print(f"Auto-approved actions executed: {len(auto_repair_report['actions_taken'])}")

        # Final status
        final_status = cali.get_system_status()
        print("\n🎯 Final Status:")
        print(f"  Compositional integrity: {final_status['compositional_integrity']:.2f}")
        print(f"  Knowledge graph: {final_status['kg_nodes']} nodes, {final_status['kg_edges']} edges")

        print("\n🎉 CALI Self-Repair test completed successfully!")

    except Exception as e:
        print(f"❌ CALI Self-Repair test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_self_repair()