# UCM_4_Core/CALI/orb/ui_overlay/escalation_handler.py
"""
Escalation Handler: Manages the complete pipeline from worker escalation to resolution or human handoff.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
from .floating_window import FLOATING_UI
from ..resolution_engine import RESOLUTION_ENGINE

class EscalationHandler:
    """
    Handles worker escalation requests and orchestrates ORB response.
    """

    def __init__(self):
        self.handler_root = Path(__file__).resolve().parents[3] / "CALI" / "orb" / "escalation"
        self.handler_root.mkdir(parents=True, exist_ok=True)

        # Active escalations
        self.active_escalations = {}

        # Escalation statistics
        self.stats_file = self.handler_root / "escalation_stats.yaml"

    async def handle_worker_escalation(self, worker_id: str, user_query: str,
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry when worker calls for ORB escalation.
        Returns resolution or escalates to human.

        Workflow:
        1. Log escalation request
        2. Check if ORB has relevant ontological memory
        3. Activate resolution engine
        4. Deploy floating UI if user-facing interaction needed
        5. Return resolution OR trigger human escalation
        """
        # Step 1: Log escalation
        escalation_id = f"ESC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{worker_id}"

        self.active_escalations[escalation_id] = {
            "worker_id": worker_id,
            "query": user_query,
            "context": context,
            "status": "PROCESSING",
            "started_at": datetime.utcnow().isoformat(),
            "resolution": None
        }

        print(f"[ESCALATION] {escalation_id} initiated by worker {worker_id}")

        # Step 2: Check browser/dashboard context (if permission granted)
        browser_context = FLOATING_UI.get_browser_context()
        if browser_context:
            context["browser_data"] = browser_context["data"]
            print(f"[ESCALATION] Browser context loaded: {len(context.get('browser_data', {}))} items")

        # Step 3: Activate resolution engine
        try:
            resolution = await asyncio.to_thread(
                RESOLUTION_ENGINE.resolve_user_escalation,
                worker_id, user_query, context
            )

            # Step 4: Update escalation record
            self.active_escalations[escalation_id]["resolution"] = resolution
            self.active_escalations[escalation_id]["completed_at"] = datetime.utcnow().isoformat()

            if resolution["status"] == "RESOLVED":
                self.active_escalations[escalation_id]["status"] = "ORB_RESOLVED"

                # Deploy UI to show resolution
                await FLOATING_UI.deploy_resolution_interface(resolution)

                print(f"[ESCALATION] {escalation_id} resolved by ORB")

            elif resolution["status"] == "ESCALATED_TO_HUMAN":
                self.active_escalations[escalation_id]["status"] = "HUMAN_ESCALATED"

                # Show escalation notice in UI
                await self._show_escalation_notice(resolution)

                print(f"[ESCALATION] {escalation_id} escalated to human")

            # Step 5: Update statistics
            self._update_stats(resolution["status"])

            return resolution

        except Exception as e:
            print(f"[ESCALATION ERROR] {escalation_id}: {e}")

            # Emergency escalation to human on error
            emergency_resolution = {
                "status": "ESCALATED_TO_HUMAN",
                "reason": f"orb_error: {str(e)}",
                "worker_id": worker_id,
                "query": user_query,
                "error": str(e)
            }

            self.active_escalations[escalation_id]["status"] = "ERROR_ESCALATED"
            self.active_escalations[escalation_id]["resolution"] = emergency_resolution

            return emergency_resolution

    async def _show_escalation_notice(self, escalation: Dict):
        """Show escalation notice to user"""
        notice = {
            "command": "show_escalation",
            "message": "ORB has escalated this issue to human support.",
            "reason": escalation.get("reason", "Unknown"),
            "estimated_response": "Within 15 minutes"
        }
        await FLOATING_UI._send_ui_command(notice)

    def _update_stats(self, resolution_status: str):
        """Update escalation statistics"""
        stats = {"total": 0, "orb_resolved": 0, "human_escalated": 0, "error_rate": 0.0}

        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                stats = yaml.safe_load(f) or stats

        stats["total"] += 1
        if resolution_status == "RESOLVED":
            stats["orb_resolved"] += 1
        elif resolution_status == "ESCALATED_TO_HUMAN":
            stats["human_escalated"] += 1

        # Calculate rates
        stats["orb_resolution_rate"] = stats["orb_resolved"] / stats["total"]
        stats["human_escalation_rate"] = stats["human_escalated"] / stats["total"]

        with open(self.stats_file, 'w') as f:
            yaml.dump(stats, f)

# Singleton handler
ESCALATION_HANDLER = EscalationHandler()