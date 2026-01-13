#!/usr/bin/env python3
"""
Canonical in-process CALI system state hub (supervisory, non-inferential).

Holds observable availability, system integration state, controls surface, and
attributed events. No cognition, no aggregation, no defaults beyond empty
containers. Read/write only through explicit methods.
"""

import threading
import time
from copy import deepcopy
from typing import Any, Dict, Optional, Callable, List


class CALISystemStateHub:
    def __init__(self):
        self._lock = threading.RLock()
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._state: Dict[str, Any] = {
            "timestamp": None,
            "cores": {},
            "systems": {
                name: {"connected": None, "last_event": None}
                for name in ("DALS", "GOAT", "TrueMark", "CertSig")
            },
            "controls": {
                "accepting": True,
                "routing_mode": {name: "via_dals" for name in ("DALS", "GOAT", "TrueMark", "CertSig")},
            },
            "events": [],
            "divergence": False,
            "last_event_by_target": {},
            "iss_now": None,
            "last_event_iss": None,
        }
        self._integrity: Dict[str, Any] = {
            "last_snapshot_ts": None,
            "last_event_ts": None,
            "replay_duration_ms": None,
            "integrity_status": "unknown",
        }

    # -------- core state --------
    def update_core(self, name: str, availability: str, last_assertion: Optional[Dict[str, Any]] = None, load: Optional[float] = None, latency_ms: Optional[int] = None, health: Optional[str] = None):
        with self._lock:
            core_entry = {
                "availability": availability,
                "last_assertion": last_assertion,
                "load": load,
                "latency_ms": latency_ms,
                "health": health,
            }
            self._state["cores"][name] = core_entry
            self._state["timestamp"] = time.time()

    # -------- system state --------
    def update_system(self, name: str, connected: Optional[bool] = None, mode: Optional[str] = None, queues: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None):
        with self._lock:
            existing = self._state["systems"].get(name, {})
            if connected is not None:
                existing["connected"] = connected
            if mode is not None:
                existing["mode"] = mode
            if queues is not None:
                existing["queues"] = queues
            if extra:
                existing.update(extra)
            self._state["systems"][name] = existing
            self._state["timestamp"] = time.time()

    # -------- controls --------
    def set_controls(self, accepting: Optional[bool] = None, routing_mode: Optional[Dict[str, str]] = None):
        with self._lock:
            if accepting is not None:
                self._state["controls"]["accepting"] = accepting
            if routing_mode:
                self._state["controls"].setdefault("routing_mode", {}).update(routing_mode)
            self._state["timestamp"] = time.time()

    # -------- events --------
    def record_event(self, event: Dict[str, Any], notify_listeners: bool = True):
        """Append-only, attributed event (no mutation)."""
        with self._lock:
            ts = event.get("timestamp", time.time())
            event = {**event, "timestamp": ts}

            target = event.get("target")
            if target:
                self._state["last_event_by_target"][target] = ts
                if target in self._state["systems"]:
                    self._state["systems"].setdefault(target, {})["last_event"] = ts

            iss_value = event.get("iss")
            if iss_value is not None:
                self._state["last_event_iss"] = iss_value
                self._state["iss_now"] = iss_value

            self._state["events"].append(event)
            self._state["timestamp"] = ts

        if notify_listeners:
            for listener in list(self._listeners):
                try:
                    listener(event)
                except Exception:
                    # Observability only; listeners must be fault-tolerant.
                    continue

    # -------- divergence flag --------
    def set_divergence(self, diverged: bool):
        with self._lock:
            self._state["divergence"] = diverged
            self._state["timestamp"] = time.time()

    # -------- snapshot --------
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def restore(self, snapshot: Dict[str, Any]):
        with self._lock:
            self._state = deepcopy(snapshot)

    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self._listeners.append(listener)

    def set_integrity(self, signals: Dict[str, Any]):
        with self._lock:
            self._integrity.update(signals)

    def get_integrity(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self._integrity)


def _get_state_hub() -> CALISystemStateHub:
    global _DEFAULT_HUB
    try:
        return _DEFAULT_HUB
    except NameError:
        _DEFAULT_HUB = CALISystemStateHub()
        return _DEFAULT_HUB


def _get_dispatcher():
    global _DEFAULT_DISPATCHER
    try:
        return _DEFAULT_DISPATCHER
    except NameError:
        from cali_control_dispatcher import CALIControlDispatcher  # local import to avoid cycle

        _DEFAULT_DISPATCHER = CALIControlDispatcher(_get_state_hub())
        return _DEFAULT_DISPATCHER


def get_snapshot() -> Dict[str, Any]:
    """Shared read-only snapshot for Orb and Dashboard surfaces."""
    return _get_state_hub().snapshot()


def submit_control(packet: Dict[str, Any]):
    """Shared control submission entry point. Returns dispatcher outcome."""
    return _get_dispatcher().dispatch(packet)
