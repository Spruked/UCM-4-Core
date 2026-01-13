#!/usr/bin/env python3
"""
ORB Bridge - Integration Layer for Core-4 + ORB
Single entry point for verdict recording and escalation
"""

import asyncio
from pathlib import Path
from typing import Dict, Any

# Import singletons (not instances)
from CALI.orb.orb_vessel import ORB_VESSEL
from CALI.orb.resolution_engine import ResolutionEngine
from CALI.orb.consciousness_probe import CONSCIOUSNESS_PROBE

# Singleton bridge functions
def bridge_core_verdict(core_id: str, verdict: Dict[str, Any],
                       context: Dict[str, Any]):
    """
    Core-4 push verdicts to ORB via this single entry point.
    ORB records immutably. Tension is evaluated automatically.
    """
    valid_cores = ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]
    if core_id not in valid_cores:
        raise ValueError(f"Invalid core_id: {core_id}")
    
    # Start ORB if not already observing
    if not ORB_VESSEL.is_observing:
        ORB_VESSEL.start_observation()
    
    # Record to ontological matrix (immutable)
    ORB_VESSEL.receive_verdict(core_id, verdict, context)
    
    print(f"[BRIDGE] {core_id} → ORB: {verdict.get('recommendation', 'unknown')}")

async def trigger_worker_escalation(worker_id: str, user_query: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker escalates to ORB. ORB synthesizes or escalates to human.
    """
    # Ensure ORB is observing
    if not ORB_VESSEL.is_observing:
        ORB_VESSEL.start_observation()
    
    # Create fresh resolution engine instance for this escalation
    resolution_engine = ResolutionEngine()
    
    # Process escalation
    result = await resolution_engine.resolve_user_escalation(
        worker_id=worker_id,
        user_query=user_query,
        context=context
    )
    
    return result

def get_orb_state_for_core(core_id: str) -> Dict[str, Any]:
    """
    Core-4 may query sanitized ORB state (read-only)
    """
    if core_id not in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
        raise ValueError(f"Invalid core_id: {core_id}")
    
    state = ORB_VESSEL.get_state()
    
    return {
        "cali_depth": state["cali_position"]["depth"],
        "tension_level": state["tension_summary"]["tension_level"],
        "emergence_readiness": CONSCIOUSNESS_PROBE.get_readiness_score(),
        "matrix_size": state["matrix_size"]["total_observations"],
        "collective_state": "forming" if state["tension_summary"]["tension_level"] > 0.5 else "observing"
    }

# Export for external use
__all__ = ["bridge_core_verdict", "trigger_worker_escalation", "get_orb_state_for_core"]