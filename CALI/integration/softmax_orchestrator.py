# UCM_4_Core/CALI/integration/softmax_orchestrator.py
"""
SoftMax Orchestrator: Generates consensus for user resolution (NOT for Core-4 control).
This is the statistical advisor that translates core disagreement into user guidance.
"""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import yaml

class SoftmaxOrchestrator:
    """
    SoftMax Orchestrator: Generates consensus from Core-4 observations for user guidance.
    """

    def __init__(self):
        self.consensus_history = []

    def generate_consensus(self, verdicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate consensus from Core-4 verdicts.
        Simplified version for ORB integration.
        """
        if not verdicts:
            return {"decision": "no_data", "confidence": 0.0}

        # Simple averaging for now
        total_confidence = sum(v.get("confidence", 0.5) for v in verdicts)
        avg_confidence = total_confidence / len(verdicts)

        # Count decisions
        decisions = {}
        for v in verdicts:
            decision = v.get("decision", "unknown")
            decisions[decision] = decisions.get(decision, 0) + 1

        # Pick most common decision
        consensus_decision = max(decisions, key=decisions.get)

        return {
            "decision": consensus_decision,
            "confidence": avg_confidence,
            "verdict_count": len(verdicts)
        }

def generate_softmax_consensus(observations: List[Dict],
                             matrix: 'OntologicalMatrix',
                             tension: 'TensionLedger') -> Dict[str, Any]:
    """
    Generate SoftMax-weighted consensus from Core-4 observations.
    Used for user resolution, NOT for controlling cores.
    """
    if not observations:
        return {"consensus_verdict": None, "confidence": 0.0}

    # Group observations by core
    core_groups = {}
    for obs_data in observations:
        obs = obs_data["observation"]
        core_id = obs["core_id"]
        if core_id not in core_groups:
            core_groups[core_id] = []
        core_groups[core_id].append(obs_data)

    # Calculate historical accuracy weights for each core
    core_weights = {}
    historical_accuracy = _calculate_historical_accuracy(core_groups.keys(), matrix)

    for core_id in core_groups.keys():
        # Base weight from historical accuracy
        base_weight = historical_accuracy.get(core_id, 0.5)

        # Adjust for tension participation (cores in tension get weighted down)
        tension_penalty = _calculate_tension_penalty(core_id, tension)

        core_weights[core_id] = max(0.1, base_weight - tension_penalty)

    # Apply SoftMax
    weights_array = np.array(list(core_weights.values()))
    softmax_weights = np.exp(weights_array) / np.sum(np.exp(weights_array))

    # Map back to cores
    core_softmax = dict(zip(core_weights.keys(), softmax_weights))

    # Generate consensus verdict (weighted average of confidences/recommendations)
    consensus_verdict = _generate_weighted_verdict(core_groups, core_softmax)

    # Identify dissenting cores (those with significantly different views)
    dissenting_cores = _identify_dissent(core_groups, consensus_verdict, core_softmax)

    # Calculate consensus strength
    consensus_strength = np.max(softmax_weights)  # Higher = more agreement

    return {
        "consensus_verdict": consensus_verdict,
        "core_weights": core_softmax,
        "consensus_strength": float(consensus_strength),
        "dissenting_cores": dissenting_cores,
        "alternative_views": _collect_alternatives(dissenting_cores, core_groups),
        "generated_at": __import__('datetime').datetime.utcnow().isoformat()
    }

def _calculate_historical_accuracy(core_ids: List[str], matrix: 'OntologicalMatrix') -> Dict[str, float]:
    """Calculate each core's historical accuracy from ontological matrix"""
    accuracy = {}

    for core_id in core_ids:
        # Get recent observations where outcome is known
        observations = matrix.get_observations_by_core(core_id, limit=50)

        if not observations:
            accuracy[core_id] = 0.5  # Default neutral
            continue

        # Count "correct" vs "incorrect" (simplified - expand with actual outcome tracking)
        correct = sum(1 for obs in observations if obs["verdict"].get("confidence", 0.5) > 0.6)
        total = len(observations)

        accuracy[core_id] = correct / total if total > 0 else 0.5

    return accuracy

def _calculate_tension_penalty(core_id: str, tension: 'TensionLedger') -> float:
    """Calculate penalty for cores currently in high tension"""
    summary = tension.get_summary()
    if summary["tension_level"] > 0.7:
        # Core is in high-tension state - reduce weight
        return 0.3
    return 0.0

def _generate_weighted_verdict(core_groups: Dict, core_softmax: Dict) -> Dict[str, Any]:
    """Generate weighted consensus verdict"""
    # This is domain-specific. Base implementation averages confidence scores.
    weighted_confidence = 0.0
    recommendations = []

    for core_id, observations in core_groups.items():
        weight = core_softmax[core_id]
        for obs_data in observations[:3]:  # Top 3 per core
            verdict = obs_data["observation"]["verdict"]
            weighted_confidence += verdict.get("confidence", 0.5) * weight
            rec = verdict.get("recommendation", verdict.get("analysis", "UNKNOWN"))
            if rec not in recommendations:
                recommendations.append(rec)

    # Pick recommendation with plurality
    primary_recommendation = max(set(recommendations), key=recommendations.count) if recommendations else "UNKNOWN"

    return {
        "recommendation": primary_recommendation,
        "confidence": float(weighted_confidence),
        "alternatives_count": len(recommendations) - 1
    }

def _identify_dissent(core_groups: Dict, consensus: Dict, core_softmax: Dict) -> List[str]:
    """Identify cores with significantly different views"""
    dissenting = []
    consensus_rec = consensus["recommendation"]

    for core_id, observations in core_groups.items():
        # Check if core's top recommendation differs from consensus
        top_obs = observations[0]["observation"]["verdict"]
        core_rec = top_obs.get("recommendation", top_obs.get("analysis", ""))

        if core_rec != consensus_rec and core_softmax[core_id] > 0.15:
            dissenting.append(core_id)

    return dissenting

def _collect_alternatives(dissenting_cores: List, core_groups: Dict) -> List[Dict]:
    """Collect alternative views from dissenting cores"""
    alternatives = []
    for core_id in dissenting_cores:
        obs = core_groups[core_id][0]["observation"]["verdict"]
        alternatives.append({
            "core_id": core_id,
            "alternative_recommendation": obs.get("recommendation", obs.get("analysis")),
            "confidence": obs.get("confidence", 0.5),
            "reason": "Core has historically valid perspective in this domain"
        })
    return alternatives