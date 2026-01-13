#!/usr/bin/env python3
"""
Control dispatcher for CALI supervisory layer.

Accepts attributed control packets, routes either directly to target handlers
or via DALS handler, and records intent/outcome in the state hub. No retries,
no inference, no hierarchy.

CALI COGNITIVE AUTHORITY DECLARATION:
CALI is the cognitive authority.
ORB is her ontological vessel.
All cognition expressed through the ORB belongs to CALI.
SoftMax SKG provides +1 advisory only (pre-verdict, non-authoritative).
POM 2.0 is CALI's exclusive phonatory expression.
"""

import time
from typing import Any, Callable, Dict, Optional

from cali_state_hub import CALISystemStateHub


ControlHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class CALIControlDispatcher:
    def __init__(self, state_hub: CALISystemStateHub):
        self.state_hub = state_hub
        self._direct_handlers: Dict[str, ControlHandler] = {}
        self._dals_handler: Optional[ControlHandler] = None

        # CALI Phonatory Authority Declaration
        self.phonatory_config = {
            "phonatory_module": "POM_2.0",
            "exclusive": True,
            "shared_with_cores": False,
            "voice_oracle": "POM_2.0.caleon_voice_oracle.CaleonVoiceOracle",
            "output_authority": "CALI_ONLY"
        }

    def register_direct_handler(self, target: str, handler: ControlHandler):
        self._direct_handlers[target] = handler

    def register_dals_handler(self, handler: ControlHandler):
        self._dals_handler = handler

    def dispatch(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a control packet. Packet should include:
        actor, surface, target, action, parameters, via (direct|dals), timestamp.
        No retries; outcome is recorded as-is.
        """

        via = (packet.get("via") or "direct").lower()
        target = packet.get("target")
        handler: Optional[ControlHandler] = None

        if via == "dals":
            handler = self._dals_handler
        else:
            handler = self._direct_handlers.get(str(target))

        parameters = packet.get("parameters", packet.get("params"))

        intent_event = {
            "type": "intent_issued",
            "actor": packet.get("actor"),
            "surface": packet.get("surface"),
            "target": target,
            "action": packet.get("action"),
            "parameters": parameters,
            "via": via,
            "timestamp": packet.get("timestamp"),
        }
        self.state_hub.record_event(intent_event)

        outcome: Dict[str, Any] = {"status": "not_dispatched", "detail": "no handler"}

        if handler:
            try:
                outcome = handler(packet) or {"status": "unknown"}
            except Exception as exc:
                outcome = {"status": "error", "detail": str(exc)}

        outcome_event = {
            "type": "outcome_observed",
            "actor": packet.get("actor"),
            "surface": packet.get("surface"),
            "target": target,
            "action": packet.get("action"),
            "parameters": parameters,
            "via": via,
            "timestamp": packet.get("timestamp") or time.time(),
            "outcome": outcome,
        }
        self.state_hub.record_event(outcome_event)
        return outcome
