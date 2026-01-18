#!/usr/bin/env python3
# dals_approval.py - Human approval interface for CALI advisories

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from CALI.cooperative_advisory import CooperativeAdvisoryWorker

def approve_suggestion(suggestion_id: str, user: str, rationale: str = ""):
    """Approve a CALI advisory"""
    worker = CooperativeAdvisoryWorker()
    
    result = worker.run({
        "action": "approve_suggestion",
        "suggestion_id": suggestion_id,
        "approved": True,
        "approved_by": user,
        "rationale": rationale
    })
    
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print(f"\n✅ Approved: {suggestion_id}")
        print("🏗️ DALS will now queue deployment via forge")
    else:
        print(f"\n❌ Failed: {result.get('message')}")

def reject_suggestion(suggestion_id: str, user: str, rationale: str):
    """Reject a CALI advisory"""
    worker = CooperativeAdvisoryWorker()
    
    result = worker.run({
        "action": "approve_suggestion",
        "suggestion_id": suggestion_id,
        "approved": False,
        "rejected_by": user,
        "rationale": rationale
    })
    
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print(f"\n❌ Rejected: {suggestion_id}")
        print("📊 CALI will weight this pattern down in future analysis")
    else:
        print(f"\n❌ Failed: {result.get('message')}")

def list_recent_advisories(count: int = 5):
    """List recent advisories"""
    worker = CooperativeAdvisoryWorker()
    
    result = worker.run({
        "action": "list_recent_advisories",
        "count": count
    })
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dals_approval.py <approve|reject|list> [suggestion_id] [user] [rationale]")
        print("\nExamples:")
        print("  python dals_approval.py approve emergency_scaling_001 bryan 'System needs scaling'")
        print("  python dals_approval.py reject emergency_scaling_001 bryan 'Investigating root cause'")
        print("  python dals_approval.py list 5")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "approve":
        if len(sys.argv) < 4:
            print("Error: approve requires suggestion_id and user")
            sys.exit(1)
        suggestion_id = sys.argv[2]
        user = sys.argv[3]
        rationale = sys.argv[4] if len(sys.argv) > 4 else ""
        approve_suggestion(suggestion_id, user, rationale)
    
    elif action == "reject":
        if len(sys.argv) < 4:
            print("Error: reject requires suggestion_id and user")
            sys.exit(1)
        suggestion_id = sys.argv[2]
        user = sys.argv[3]
        rationale = sys.argv[4] if len(sys.argv) > 4 else ""
        reject_suggestion(suggestion_id, user, rationale)
    
    elif action == "list":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        list_recent_advisories(count)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)