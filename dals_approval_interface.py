#!/usr/bin/env python3
"""
DALS Approval Interface for CALI Cooperative Advisory System
Human-sovereign approval workflow for Core 4 AI developmental autonomy
"""

import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

class DALSApprovalInterface:
    """Human approval interface for CALI suggestions"""

    def __init__(self):
        self.queue_file = Path("CALI/suggestion_queue.jsonl")
        self.advisory_log = Path("unified_vault/advisory_log.jsonl")
        self.autonomy_index = Path("CALI/autonomy_index.yaml")

    def list_pending_suggestions(self) -> List[Dict[str, Any]]:
        """List all pending suggestions for approval"""
        suggestions = []

        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    suggestion = json.loads(line.strip())
                    if suggestion.get('status') == 'pending':
                        suggestions.append(suggestion)

        return suggestions

    def list_recent_advisories(self, count: int = 5) -> List[Dict[str, Any]]:
        """List recent advisories"""
        advisories = []

        if self.advisory_log.exists():
            with open(self.advisory_log, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    obs = json.loads(line)
                    if obs.get("category") == "cooperative_advisory":
                        advisories.append(obs["data"])

        return advisories[-count:]

    def approve_suggestion(self, suggestion_id: str, user: str, rationale: str = "") -> bool:
        """Approve a suggestion"""
        from CALI.cooperative_advisory import CooperativeAdvisoryWorker

        worker = CooperativeAdvisoryWorker()
        result = worker.run({
            'action': 'approve_suggestion',
            'suggestion_id': suggestion_id,
            'approved': True,
            'approved_by': user,
            'rationale': rationale
        })

        return result.get('status') == 'success'

    def reject_suggestion(self, suggestion_id: str, user: str, rationale: str = "") -> bool:
        """Reject a suggestion"""
        from CALI.cooperative_advisory import CooperativeAdvisoryWorker

        worker = CooperativeAdvisoryWorker()
        result = worker.run({
            'action': 'approve_suggestion',
            'suggestion_id': suggestion_id,
            'approved': False,
            'rejected_by': user,
            'rationale': rationale
        })

        return result.get('status') == 'success'

    def display_suggestion(self, suggestion: Dict[str, Any]) -> None:
        """Display a suggestion in human-readable format"""
        print(f"\n{'='*60}")
        print(f"Suggestion ID: {suggestion['id']}")
        print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(suggestion['timestamp']))}")
        print(f"Confidence: {suggestion['confidence']:.1%}")
        print(f"Category: {suggestion['category']}")
        print(f"Priority: {suggestion['priority']}")
        print(f"Status: {suggestion['status']}")
        print(f"\nDescription:")
        print(f"  {suggestion['description']}")
        print(f"\nRationale:")
        print(f"  {suggestion['rationale']}")
        print(f"\nEvidence:")
        for evidence in suggestion.get('evidence', []):
            print(f"  • {evidence}")
        print(f"{'='*60}")

    def interactive_approval(self) -> None:
        """Interactive approval workflow"""
        print("DALS Approval Interface - Core 4 AI Developmental Autonomy")
        print("=" * 60)

        while True:
            pending = self.list_pending_suggestions()

            if not pending:
                print("\nNo pending suggestions for approval.")
                break

            print(f"\nFound {len(pending)} pending suggestions:")

            for i, suggestion in enumerate(pending, 1):
                print(f"{i}. {suggestion['category']} - {suggestion['description'][:50]}... (ID: {suggestion['id']})")

            try:
                choice = input("\nEnter suggestion number to review (or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    break

                idx = int(choice) - 1
                if 0 <= idx < len(pending):
                    suggestion = pending[idx]
                    self.display_suggestion(suggestion)

                    action = input("\nApprove (a), Reject (r), or Skip (s)? ").strip().lower()

                    if action == 'a':
                        user = input("Your name/initials: ").strip()
                        rationale = input("Approval rationale (optional): ").strip()
                        if self.approve_suggestion(suggestion['id'], user, rationale):
                            print("✓ Suggestion approved and logged immutably.")
                        else:
                            print("✗ Failed to approve suggestion.")

                    elif action == 'r':
                        user = input("Your name/initials: ").strip()
                        rationale = input("Rejection rationale: ").strip()
                        if self.reject_suggestion(suggestion['id'], user, rationale):
                            print("✓ Suggestion rejected and logged immutably.")
                        else:
                            print("✗ Failed to reject suggestion.")

                    elif action == 's':
                        continue
                    else:
                        print("Invalid choice.")
                else:
                    print("Invalid suggestion number.")

            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

def main():
    parser = argparse.ArgumentParser(description="DALS Approval Interface")
    parser.add_argument('--action', choices=['list', 'approve', 'reject', 'interactive'],
                       default='interactive', help='Action to perform')
    parser.add_argument('--id', help='Suggestion ID for approve/reject')
    parser.add_argument('--user', help='User name for approval/rejection')
    parser.add_argument('--rationale', default='', help='Rationale for decision')
    parser.add_argument('--count', type=int, default=5, help='Number of recent advisories to show')

    args = parser.parse_args()

    interface = DALSApprovalInterface()

    if args.action == 'list':
        print("Recent Advisories:")
        advisories = interface.list_recent_advisories(args.count)
        for adv in advisories:
            print(f"- {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(adv['timestamp']))}: {adv['description']}")

    elif args.action == 'approve':
        if not args.id or not args.user:
            print("Error: --id and --user required for approval")
            return
        if interface.approve_suggestion(args.id, args.user, args.rationale):
            print("Suggestion approved.")
        else:
            print("Failed to approve suggestion.")

    elif args.action == 'reject':
        if not args.id or not args.user:
            print("Error: --id and --user required for rejection")
            return
        if interface.reject_suggestion(args.id, args.user, args.rationale):
            print("Suggestion rejected.")
        else:
            print("Failed to reject suggestion.")

    elif args.action == 'interactive':
        interface.interactive_approval()

if __name__ == "__main__":
    main()