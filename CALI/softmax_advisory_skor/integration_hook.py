#!/usr/bin/env python3
"""
CALI SoftMax Integration Hook (plural, non-hierarchical)
Coordinates SoftMax advisory with CALI's immutable memory and sibling routing.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from softmax_advisory_skor.consensus_advisor import (
    AdvisoryRecommendation,
    AdvisorySignal,
    Core4Verdict,
    SoftMaxConsensusAdvisor,
)
from softmax_advisory_skor.verdict_provider import http_verdict_provider
from cali_immutable_matrix.system_memory import (
    CALIPeerOrchestrationMatrix,
    CALIOperationType,
    SiblingCore4,
)


class CALISoftMaxIntegration:
    """Bridge between SoftMax Advisory and CALI orchestration."""

    def __init__(self, ucm_4_core_path: Path, verdict_provider: Optional[Callable[[str, int], List[Core4Verdict]]] = None):
        self.ucm_root = Path(ucm_4_core_path)
        self.advisor = SoftMaxConsensusAdvisor()
        self.cali_memory = CALIPeerOrchestrationMatrix(self.ucm_root)
        self.sibling_map = {
            "KayGee_1.0": SiblingCore4.KAYGEE_10,
            "Cali_X_One": SiblingCore4.CALI_X_ONE,
            "UCM_Core_ECM": SiblingCore4.UMC_CORE_ECM,
            "Caleon_Genesis_1.12": SiblingCore4.CALEON_GENESIS,
        }
        self._verdict_provider = verdict_provider or self._default_verdict_provider

    def _default_verdict_provider(self, decision_context: str, timeout_ms: int) -> List[Core4Verdict]:
        # Use HTTP provider with auto-discovered endpoints; fall back to empty if none available.
        return http_verdict_provider(decision_context, timeout_ms=timeout_ms, base_path=self.ucm_root)

    def gather_core4_verdicts(self, decision_context: str, timeout_ms: int = 5000) -> List[Core4Verdict]:
        verdicts = self._verdict_provider(decision_context, timeout_ms) or []
        self.cali_memory.record_sibling_monitoring(
            sibling=self.sibling_map["KayGee_1.0"],
            detection_type="verdict_collection",
            detected_metric="verdicts_collected",
            metric_value=len(verdicts),
            metadata={"decision_context": decision_context, "timeout_ms": timeout_ms},
        )
        return verdicts

    def get_consensus_advisory(self, decision_context: str, write_to_memory: bool = True) -> AdvisorySignal:
        verdicts = self.gather_core4_verdicts(decision_context)
        advisory = self.advisor.process_verdicts(verdicts)
        if write_to_memory:
            self._record_advisory_in_memory(decision_context, advisory, verdicts)
        return advisory

    def _record_advisory_in_memory(self, decision_context: str, advisory: AdvisorySignal, verdicts: List[Core4Verdict]):
        self.cali_memory.record_capability_evolution(
            capability_name=f"consensus_advisory_{decision_context}",
            significance=advisory.consensus_level,
            derivation_context={
                "advisory_output": advisory.to_dict(),
                "verdicts_used": len(verdicts),
                "consensus_calculation_method": "softmax_weighted",
                "outlier_detection_method": "iqr",
            },
            metadata={
                "softmax_advisory": advisory.to_dict(),
                "verdict_sources": [v.core_name for v in verdicts],
                "decision_context": decision_context,
                "advisory_source": "softmax_skg",
                "note": "Advisory output recorded; SoftMax is stateless",
            },
        )

    def interpret_advisory_for_action(self, advisory: AdvisorySignal, decision_context: str) -> Dict[str, Any]:
        actions = {
            "recommendation": advisory.recommendation.value,
            "advisory_confidence": advisory.consensus_level,
            "context": decision_context,
            "cali_action": None,
            "action_justification": None,
        }

        if advisory.recommendation == AdvisoryRecommendation.PROCEED:
            actions["cali_action"] = "execute_immediately"
            actions["action_justification"] = "High consensus across Core 4 siblings"
        elif advisory.recommendation == AdvisoryRecommendation.PROCEED_CAUTIOUSLY:
            actions["cali_action"] = "execute_with_monitoring"
            actions["action_justification"] = "Moderate consensus, proceed with observation"
        elif advisory.recommendation == AdvisoryRecommendation.PAUSE_AND_VERIFY:
            actions["cali_action"] = "defer_and_validate"
            actions["action_justification"] = f"Weak consensus ({advisory.consensus_level:.2f}), validate inputs"
        elif advisory.recommendation == AdvisoryRecommendation.ESCALATE_TO_REVIEW:
            actions["cali_action"] = "escalate_for_manual_review"
            actions["action_justification"] = "Significant disagreement among Core 4 siblings"
        elif advisory.recommendation == AdvisoryRecommendation.OUTLIER_INVESTIGATION:
            actions["cali_action"] = "investigate_outlier"
            actions["action_justification"] = f"Statistical outlier detected: {advisory.outlier_detected}"

        target_sibling = self._infer_primary_sibling(decision_context)
        if target_sibling:
            self.cali_memory.record_authority_command(
                sibling=target_sibling,
                command=actions["cali_action"],
                justification=actions["action_justification"],
                command_params={
                    "advisory_consensus": advisory.consensus_level,
                    "advisory_recommendation": advisory.recommendation.value,
                    "context": decision_context,
                },
                assertion_level="command" if advisory.consensus_level > 0.7 else "suggestion",
            )
        return actions

    def _infer_primary_sibling(self, decision_context: str) -> Optional[SiblingCore4]:
        context_lower = decision_context.lower()
        if "kaygee" in context_lower or "empirical" in context_lower:
            return SiblingCore4.KAYGEE_10
        if "ecm" in context_lower or "convergent" in context_lower:
            return SiblingCore4.UMC_CORE_ECM
        if "genesis" in context_lower:
            return SiblingCore4.CALEON_GENESIS
        if "cali_x" in context_lower:
            return SiblingCore4.CALI_X_ONE
        return None

    def get_advisory_statistics(self) -> Dict[str, Any]:
        memory_summary = self.cali_memory.get_operational_summary()
        advisory_records = []
        for entry in self.cali_memory.entries:
            if entry.metadata.get("advisory_source") == "softmax_skg":
                advisory_records.append(entry)
        consensus_distribution: Dict[str, int] = {}
        recommendation_counts: Dict[str, int] = {}
        for entry in advisory_records:
            advisory_data = entry.metadata.get("softmax_advisory", {})
            consensus = advisory_data.get("consensus_level", 0.0)
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
            rec = advisory_data.get("recommendation", "unknown")
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        return {
            "memory_summary": memory_summary,
            "total_advisories_recorded": len(advisory_records),
            "consensus_distribution": consensus_distribution,
            "recommendation_history": recommendation_counts,
            "softmax_skg_state": "stateless_deterministic",
        }


def get_softmax_advisory(ucm_4_core_path: str, decision_context: str, write_to_memory: bool = True, verdict_provider: Optional[Callable[[str, int], List[Core4Verdict]]] = None) -> AdvisorySignal:
    integration = CALISoftMaxIntegration(Path(ucm_4_core_path), verdict_provider=verdict_provider)
    return integration.get_consensus_advisory(decision_context, write_to_memory)
