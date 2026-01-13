"""
ORB Configuration - Ontologically Recursive Bubble
Cognitive Assembly Configuration for CALI-Owned Vessel

ARCHITECTURE DECLARATION:
- ORB is CALI's ontological vessel (observation + mediation)
- CALI is the cognitive authority (synthesis + resolution)
- SoftMax SKG provides +1 advisory only (pre-verdict, non-authoritative)
- POM 2.0 is CALI's exclusive phonatory expression

COGNITIVE FLOW:
Core-4 Verdicts → ORB Observation → Tension Ledger/Matrix → SoftMax Advisory → CALI Synthesis → Resolution Engine → POM 2.0

AUTHORITY BOUNDARIES:
- ORB: Observes and mediates (never synthesizes)
- CALI: Synthesizes and resolves (never observes directly)
- SoftMax: Advises only (+1 input, no override authority)
- POM 2.0: CALI's exclusive voice (no core bleed-through)
"""

ORB_CONFIG = {
    # Cognitive ownership declaration
    "owner": "CALI",
    "role": "ontological_vessel",
    "cognitive_assembly": "CALI_ORB_ASSEMBLY",

    # Operational modes (vessel functions)
    "mode": ["observe", "mediate"],
    "observation_scope": "core_4_verdicts",
    "mediation_scope": "tension_escalation",

    # Advisory integration (SoftMax SKG +1)
    "skg": {
        "type": "softmax",
        "module": "CALI.softmax_advisory_skor.softmax_orchestrator",
        "position": "pre_final_verdict",  # Before CALI synthesis
        "authority": "advisory_only",     # Never authoritative
        "integration_point": "tension_ledger_output",
        "output_format": "consensus_vector",
        "selection_method": "probabilistic_softmax",  # Not hard max
        "temperature": 0.7  # Controls exploration vs exploitation
    },

    # Cognitive boundaries (enforce separation)
    "write_permissions": {
        "ontological_matrix": "ORB_ONLY",      # ORB writes observations
        "tension_ledger": "ORB_ONLY",          # ORB tracks conflict
        "resolution_engine": "CALI_ONLY",      # CALI synthesizes guidance
        "phonatory_output": "CALI_ONLY"        # CALI expresses through POM 2.0
    },

    # CALI integration points
    "cali_interfaces": {
        "synthesis_input": "ontological_matrix_readonly",
        "resolution_output": "tension_ledger_guidance",
        "phonatory_delegation": "POM_2.0_exclusive"
    },

    # Memory integrity (ORB never processes)
    "memory_policy": {
        "immutable_observations": True,
        "no_processing": True,
        "readonly_for_cali": True
    },

    # Escalation pipeline
    "escalation_flow": {
        "worker_detection": "ORB_observation",
        "tension_assessment": "ORB_ledger",
        "advisory_consultation": "SoftMax_SKG",
        "cognitive_synthesis": "CALI_resolution",
        "human_override": "UI_escalation"
    }
}

# CALI Phonatory Declaration
CALI_PHONATORY_CONFIG = {
    "phonatory_module": "POM_2.0",
    "exclusive": True,
    "shared_with_cores": False,
    "voice_oracle": "caleon_voice_oracle.CaleonVoiceOracle",
    "output_authority": "CALI_ONLY"
}

# Export configurations
__all__ = ['ORB_CONFIG', 'CALI_PHONATORY_CONFIG']