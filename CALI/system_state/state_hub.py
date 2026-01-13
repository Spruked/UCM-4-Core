#!/usr/bin/env python3
"""
CALI System State Hub (shared, non-hierarchical)

- Single in-memory source of truth for CALI_SYSTEM_STATE
- Serves Orb and Dashboard (two skins, same state)
- Handles attributed control actions (records only; routing stubs)
- Thread-safe, no background loops, no inference
"""

import threading
import time
from copy import deepcopy
from typing import Any, Dict, List, Optional


class CALISystemStateHub:
    def __init__(self):
        self._lock = threading.Lock()
        self._state: Dict[str, Any] = self._empty_state()
        self._control_log: List[Dict[str, Any]] = []

    def _empty_state(self) -> Dict[str, Any]:
        return {
            "timestamp": None,
            "cores": {},
            "systems": {
                "DALS": {},
                "GOAT": {},
                "TrueMark": {},
                "CertSig": {},
            },
            "controls": {
                "accepting": True,
                "routing_mode": {
                    "DALS": "via_dals",
                    "GOAT": "via_dals",
                    "TrueMark": "via_dals",
                    "CertSig": "via_dals",
                },
            },
            "events": [],
            "divergence": False,
        }

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def update_core_availability(self, core_name: str, availability: str, last_assertion: Optional[Dict[str, Any]] = None):
        now = time.time()
        with self._lock:
            core = self._state["cores"].get(core_name, {})
            core.update({
                "availability": availability,
                "last_assertion": last_assertion or core.get("last_assertion"),
                "last_seen": now,
            })
            self._state["cores"][core_name] = core
            self._state["timestamp"] = now

    def record_assertion(self, core_name: str, assertion: Dict[str, Any]):
        now = time.time()
        with self._lock:
            core = self._state["cores"].get(core_name, {})
            core["last_assertion"] = assertion
            core["availability"] = core.get("availability", "AVAILABLE")
            core["last_seen"] = now
            self._state["cores"][core_name] = core
            self._state["timestamp"] = now

    def update_system_status(self, system_name: str, status: Dict[str, Any]):
        now = time.time()
        with self._lock:
            if system_name not in self._state["systems"]:
                self._state["systems"][system_name] = {}
            self._state["systems"][system_name].update(status)
            self._state["timestamp"] = now

    def set_divergence(self, flag: bool):
        with self._lock:
            self._state["divergence"] = bool(flag)

    def record_event(self, event: Dict[str, Any]):
        with self._lock:
            self._state["events"].append(event)
            if len(self._state["events"]) > 500:
                self._state["events"] = self._state["events"][-500:]

    def record_control_action(self, action: Dict[str, Any]):
        """Record an attributed control action. Does not execute it."""
        with self._lock:
            action.setdefault("timestamp", time.time())
            self._control_log.append(action)
            if len(self._control_log) > 1000:
                self._control_log = self._control_log[-1000:]
            self._state["events"].append({"type": "control", **action})
            if len(self._state["events"]) > 500:
                self._state["events"] = self._state["events"][-500:]

    def get_control_log(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(self._control_log)


class CALIControlDispatcher:
    """Stub dispatcher: routes attributed commands to targets.

    This stub only records the intent. Integration hooks to DALS/GOAT/TrueMark/CertSig
    should be added explicitly and permissioned; no implicit routing.
    """

    def __init__(self, hub: CALISystemStateHub):
        self.hub = hub

    def dispatch(self, action: Dict[str, Any]):
        # Record intent; actual routing to be wired to real adapters explicitly.
        self.hub.record_control_action(action)
        # Placeholder for future adapters (explicit only):
        # if action["target"] == "DALS": ...
        return {"status": "recorded", "timestamp": action.get("timestamp")}


def get_default_hub() -> CALISystemStateHub:
    global _DEFAULT_HUB
    try:
        return _DEFAULT_HUB
    except NameError:
        _DEFAULT_HUB = CALISystemStateHub()
        return _DEFAULT_HUB
