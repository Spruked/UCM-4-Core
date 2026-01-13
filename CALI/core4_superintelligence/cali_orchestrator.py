#!/usr/bin/env python3
"""Lean orchestrator scaffold (non-hierarchical, no mock data).

Holds last-observed availability assertions from sibling cores. No inference,
no prediction, no hierarchy.
"""

from enum import Enum
from typing import Dict


class BrainState(Enum):
    AVAILABLE = "available"
    SILENT = "silent"
    UNAVAILABLE = "unavailable"
class CALIOrchestrationCore:
    def __init__(self, ucm_root):
        self.ucm_root = ucm_root
        self._states: Dict[str, BrainState] = {}

    def get_all_brain_states(self) -> Dict[str, BrainState]:
        return self._states

    def update_brain_state(self, name: str, state: BrainState):
        self._states[name] = state
