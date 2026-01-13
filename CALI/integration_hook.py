#!/usr/bin/env python3
"""
CALI SoftMax Integration Hook
Connects SoftMax Advisor to CALI orchestration and memory

PATTERN:
1. Core 4 siblings produce verdicts → SoftMax SKG
2. SoftMax SKG → AdvisorySignal (statistical analysis)
3. CALI orchestration → Decides action based on advisory
4. CALI → Records decision in immutable memory
5. SoftMax SKG → Remains stateless and unchanged

This maintains "no-touch" rule: SoftMax never touches cognition, memory, or learning.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from .consensus_advisor import (
    SoftMaxConsenspusAdvisor,
    Core4Verdict,
    AdvisoryRecommendation,
    AdvisorySignal
)
from ..cali_immutable_matrix.system_memory import (
    CALIPeerOrchestrationMatrix,
    SiblingCore4,
    CALIOperationType
)
from softmax_advisory_skor.verdict_provider import http_verdict_provider

class CALISoftMaxIntegration:
    """
    Integration bridge between SoftMax Advisor and CALI orchestration
    
    RESPONSIBILITIES:
    - Collect verdicts from sibling Core 4 brains
    - Run SoftMax consensus analysis
    - Pass advisory to CALI orchestration logic
    - Record advisory output in immutable memory (optional)
    - Keep SoftMax itself stateless and untouched
    """

    def __init__(self, ucm_4_core_path: Path, verdict_provider: Optional[Callable[[str, int], List[Core4Verdict]]] = None):
        self.ucm_root = Path(ucm_4_core_path)
        
        # Initialize SoftMax advisor (stateless, lightweight)
        self.advisor = SoftMaxConsensusAdvisor()
        
        # Reference to CALI's operational memory
        # Note: CALI memory records the *advisory output*, not SoftMax state
        self.cali_memory = CALIPeerOrchestrationMatrix(self.ucm_root)
        
        # Map external Core 4 folder names to enum
        self.sibling_map = {
            "KayGee_1.0": SiblingCore4.KAYGEE_10,
            "Cali_X_One": SiblingCore4.CALI_X_ONE,
            "UCM_Core_ECM": SiblingCore4.UMC_CORE_ECM,
            "Caleon_Genesis_1.12": SiblingCore4.CALEON_GENESIS
        }

        # Real verdict provider (no mock generation). Uses HTTP endpoints by default.
        self.verdict_provider: Callable[[str, int], List[Core4Verdict]] = verdict_provider or (
            lambda decision_context, timeout_ms=5000: http_verdict_provider(
                decision_context, timeout_ms=timeout_ms, base_path=self.ucm_root
            )
        )

    def gather_core4_verdicts(self, 
                              decision_context: str,
                              timeout_ms: int = 5000) -> List[Core4Verdict]:
        """
        Gather verdicts from sibling Core 4 brains via configured provider.

        No simulated data: if endpoints or providers yield nothing, this raises
        to signal absence of real inputs.
        """

        verdicts = self.verdict_provider(decision_context, timeout_ms)

        if not verdicts:
            raise RuntimeError(
                f"No Core4 verdicts available for decision_context='{decision_context}'. "
                "Configure CORE4_VERDICT_ENDPOINTS or inject a verdict_provider."
            )

        self.cali_memory.record_sibling_monitoring(
            sibling=self.sibling_map.get("KayGee_1.0", SiblingCore4.KAYGEE_10),
            detection_type="verdict_collection",
            detected_metric="verdicts_collected",
            metric_value=len(verdicts),
            metadata={"decision_context": decision_context, "timeout_ms": timeout_ms}
        )

        return verdicts

    def get_consensus_advisory(self, 
                              decision_context: str,
                              write_to_memory: bool = True) -> AdvisorySignal:
        """
        Main orchestration hook: Get advisory from SoftMax SKG
        
        Args:
            decision_context: Description of decision being made
            write_to_memory: Whether to record advisory output in CALI memory
            
        Returns:
            AdvisorySignal for CALI's decision-making
        """
        # Step 1: Gather verdicts from Core 4 siblings
        verdicts = self.gather_core4_verdicts(decision_context)
        
        # Step 2: Run statistical consensus analysis
        advisory = self.advisor.process_verdicts(verdicts)
        
        # Step 3 (Optional): Record advisory output in CALI's immutable memory
        # CRITICAL: SoftMax SKG itself remains stateless and unchanged
        # Only CALI's memory stores the advisory output
        if write_to_memory:
            self._record_advisory_in_memory(decision_context, advisory, verdicts)
        
        return advisory

    def _record_advisory_in_memory(self,
                                  decision_context: str,
                                  advisory: AdvisorySignal,
                                  verdicts: List[Core4Verdict]):
        """
        Record SoftMax advisory output in CALI's immutable memory
        
        IMPORTANT DISTINCTION:
        - SoftMax SKG remains stateless and deterministic
        - CALI memory records the *output* for operational accountability
        - This is CALI's memory, not SoftMax's memory
        """
        # Record as an operational learning entry in CALI system memory
        self.cali_memory.record_capability_evolution(
            capability_name=f"consensus_advisory_{decision_context}",
            significance=advisory.consensus_level,
            derivation_context={
                "advisory_output": advisory.to_dict(),
                "verdicts_used": len(verdicts),
                "consensus_calculation_method": "softmax_weighted",
                "outlier_detection_method": "iqr"
            },
            metadata={
                "softmax_advisory": advisory.to_dict(),  # Store the output
                "verdict_sources": [v.core_name for v in verdicts],
                "decision_context": decision_context,
                "advisory_source": "softmax_skg",
                "note": "Advisory output recorded, SoftMax SKG remains stateless"
            }
        )

    def interpret_advisory_for_action(self, 
                                     advisory: AdvisorySignal,
                                     decision_context: str) -> Dict[str, Any]:
        """
        CALI orchestration logic: Translate advisory into potential actions
        
        IMPORTANT: SoftMax only advises. CALI decides.
        
        This function embodies CALI's decision-making policy, not SoftMax reasoning.
        """
        actions = {
            "recommendation": advisory.recommendation.value,
            "advisory_confidence": advisory.consensus_level,
            "context": decision_context,
            "cali_action": None,
            "action_justification": None
        }
        
        if advisory.recommendation == AdvisoryRecommendation.PROCEED:
            actions["cali_action"] = "execute_immediately"
            actions["action_justification"] = "High consensus across Core 4 siblings"
            
        elif advisory.recommendation == AdvisoryRecommendation.PROCEED_CAUTIOUSLY:
            actions["cali_action"] = "execute_with_monitoring"
            actions["action_justification"] = "Moderate consensus, proceed with increased observation"
            
        elif advisory.recommendation == AdvisoryRecommendation.PAUSE_AND_VERIFY:
            actions["cali_action"] = "defer_and_validate"
            actions["action_justification"] = f"Weak consensus ({advisory.consensus_level:.2f}), validate inputs"
            
        elif advisory.recommendation == AdvisoryRecommendation.ESCALATE_TO_REVIEW:
            actions["cali_action"] = "escalate_for_manual_review"
            actions["action_justification"] = "Significant disagreement among Core 4 siblings"
            
        elif advisory.recommendation == AdvisoryRecommendation.OUTLIER_INVESTIGATION:
            actions["cali_action"] = "investigate_outlier"
            actions["action_justification"] = f"Statistical outlier detected: {advisory.outlier_detected}"
        
        # Record CALI's decision in immutable memory
        # This is separate from the advisory recording
        target_sibling = self._infer_primary_sibling(decision_context)
        
        if target_sibling:
            self.cali_memory.record_authority_command(
                sibling=target_sibling,
                command=actions["cali_action"],
                justification=actions["action_justification"],
                command_params={
                    "advisory_consensus": advisory.consensus_level,
                    "advisory_recommendation": advisory.recommendation.value,
                    "context": decision_context
                },
                assertion_level="command" if consensus_level > 0.7 else "suggestion"
            )
        
        return actions

    def _infer_primary_sibling(self, decision_context: str) -> Optional[SiblingCore4]:
        """
        Infer which sibling Core 4 is primary target of decision
        (Heuristic based on decision context)
        """
        context_lower = decision_context.lower()
        
        if "kaygee" in context_lower or "empirical" in context_lower:
            return SiblingCore4.KAYGEE_10
        elif "ecm" in context_lower or "convergent" in context_lower:
            return SiblingCore4.UMC_CORE_ECM
        elif "genesis" in context_lower:
            return SiblingCore4.CALEON_GENESIS
        elif "cali_x" in context_lower:
            return SiblingCore4.CALI_X_ONE
        
        return None

    def get_advisory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about advisory patterns recorded in CALI memory
        
        Note: This queries CALI's memory of SoftMax outputs.
        SoftMax SKG itself has no internal statistics or state.
        """
        # Get CALI memory summary
        memory_summary = self.cali_memory.get_operational_summary()
        
        # Count advisory-related records
        advisory_records = []
        for entry in self.cali_memory.entries:
            if entry.metadata.get("advisory_source") == "softmax_skg":
                advisory_records.append(entry)
        
        consensus_distribution = {}
        recommendation_counts = {}
        
        for entry in advisory_records:
            advisory_data = entry.metadata.get("softmax_advisory", {})
            consensus = advisory_data.get("consensus_level", 0.0)
            
            # Bin by consensus level
            if consensus >= 0.90:
                bin_name = "unanimous"
            elif consensus >= 0.75:
                bin_name = "strong"
            elif consensus >= 0.60:
                bin_name = "moderate"
            elif consensus >= 0.40:
                bin_name = "fragmented"
            else:
                bin_name = "conflicted"
            
            consensus_distribution[bin_name] = consensus_distribution.get(bin_name, 0) + 1
            
            # Count recommendations
            rec = advisory_data.get("recommendation", "unknown")
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        return {
            "total_advisories_recorded": len(advisory_records),
            "consensus_distribution": consensus_distribution,
            "recommendation_history": recommendation_counts,
            "softmax_skg_state": "stateless_deterministic",
            "cali_memory_uses_advisory": len(advisory_records) > 0,
            "note": "These are CALI's memories of SoftMax outputs. SoftMax itself has no memory."
        }

# Convenience function for CALI orchestration modules
def get_softmax_advisory(ucm_4_core_path: str, 
                        decision_context: str,
                        write_to_memory: bool = True) -> AdvisorySignal:
    """
    One-liner for CALI orchestration code
    
    Usage in core4_superintelligence/orchestrator.py:
    
    from softmax_advisory_skor.integration_hook import get_softmax_advisory
    
    class CALIOrchestrator:
        def make_decision(self, context: str):
            # Get statistical advisory
            advisory = get_softmax_advisory(
                ucm_4_core_path="/path/to/UCM_4_Core",
                decision_context=f"Resource allocation for {context}",
                write_to_memory=True  # Record in CALI's immutable memory
            )
            
            # CALI decides based on advisory
            if advisory.consensus_level < 0.60:
                self.logger.warning("Weak consensus, escalating to manual review")
                return self.escalate_decision(context, advisory)
            
            # Proceed with execution
            return self.execute_decision(context, advisory)
    """
    integration = CALISoftMaxIntegration(Path(ucm_4_core_path))
    return integration.get_consensus_advisory(decision_context, write_to_memory)