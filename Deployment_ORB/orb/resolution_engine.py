# UCM_4_Core/CALI/orb/resolution_engine.py
"""
Resolution Engine - User-Facing Synthesis
Activated **only** when worker escalates.
Generates SoftMax consensus from Core-4 observations.
Escalates to human if confidence < 0.4.
Advisory only. Never overrides.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import yaml
import numpy as np
from .orb_vessel import ORB_VESSEL
from .tension_ledger import TENSION_LEDGER

# SoftMax consensus generation (advisory, not authoritative)
def generate_softmax_consensus(observations: List[Dict],
                             matrix: 'OntologicalMatrix',
                             tension: 'TensionLedger') -> Dict[str, Any]:
    """
    Generate SoftMax-weighted consensus from Core-4 observations.
    Temperature=0.7 ensures exploration, not exploitation.
    Tension penalty reduces confidence when disagreement is high.
    NEVER returns 100% confidence (that's a bug).
    """
    if not observations:
        return {"consensus_verdict": None, "confidence": 0.0, "consensus_strength": 0.0}

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

    # Get current tension level (affects confidence)
    tension_summary = tension.get_summary()
    tension_level = tension_summary["tension_level"]

    for core_id in core_groups.keys():
        # Base weight from historical accuracy
        base_weight = historical_accuracy.get(core_id, 0.5)

        # Apply tension penalty: high tension = reduce confidence
        # When tension > 0.6, all weights are reduced proportionally
        tension_penalty = tension_level * 0.3

        # Apply depth penalty: if CALI is deep, increase exploration
        cali_depth = ORB_VESSEL.cali_position["depth"]
        depth_bonus = cali_depth * 0.1  # Slight bonus for deep contemplation

        # Final weight
        core_weights[core_id] = max(0.2, base_weight - tension_penalty + depth_bonus)

    # Apply SoftMax with temperature scaling
    # Temperature = 0.7 ensures no single voice dominates completely
    # SoftMax formula: exp(weight/temp) / sum(exp(all_weights/temp))
    weights_array = np.array(list(core_weights.values()))
    temperature = 0.7

    # Numerical stability: subtract max before exp
    weights_scaled = weights_array / temperature
    exp_weights = np.exp(weights_scaled - np.max(weights_scaled))
    probabilities = exp_weights / exp_weights.sum()

    # Map back to cores
    core_softmax = dict(zip(core_weights.keys(), probabilities))

    # Generate consensus verdict (weighted average of confidences)
    consensus_verdict = _generate_weighted_verdict(core_groups, core_softmax)

    # Calculate consensus strength (weighted average confidence)
    # This is the probability of the most likely outcome
    consensus_strength = np.max(probabilities)

    # Critical: Confidence cannot exceed soft max probability
    # If consensus_strength is 0.85, max confidence is 0.85
    final_confidence = min(consensus_verdict["confidence"], consensus_strength)

    # Hard ceiling: 95% (even with perfect history, uncertainty remains)
    final_confidence = min(0.95, final_confidence)

    # If tension > 0.7, additional ceiling applies
    if tension_level > 0.7:
        final_confidence = min(0.75, final_confidence)

    return {
        "consensus_verdict": consensus_verdict,
        "core_weights": core_softmax,
        "consensus_strength": float(consensus_strength),
        "tension_penalty_applied": float(tension_penalty),
        "raw_confidence": float(consensus_verdict["confidence"]),
        "final_confidence": float(final_confidence),
        "generated_at": datetime.utcnow().isoformat()
    }

def _calculate_historical_accuracy(core_ids: List[str], matrix: 'OntologicalMatrix') -> Dict[str, float]:
    """Calculate each core's historical accuracy from ontological matrix"""
    accuracy = {}
    
    for core_id in core_ids:
        observations = matrix.get_observations_by_core(core_id, limit=50)
        
        if not observations:
            accuracy[core_id] = 0.5  # Default neutral
            continue
        
        # Simple accuracy: high confidence + resolved tension
        correct = sum(1 for obs in observations 
                     if obs["verdict"].get("confidence", 0.5) > 0.6)
        total = len(observations)
        
        accuracy[core_id] = correct / total if total > 0 else 0.5
    
    return accuracy

def _calculate_tension_penalty(core_id: str, tension: 'TensionLedger') -> float:
    """Calculate penalty for cores currently in high tension"""
    summary = tension.get_summary()
    if summary["tension_level"] > 0.7:
        return 0.3  # Reduce weight for high-tension cores
    return 0.0

def _generate_weighted_verdict(core_groups: Dict, core_softmax: Dict) -> Dict[str, Any]:
    """Generate weighted consensus verdict"""
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


class ResolutionEngine:
    """
    Handles worker escalation requests and orchestrates ORB response.
    Generates consensus-based guidance without overriding Core-4 sovereignty.
    Escalates to human when confidence is insufficient.
    """
    
    def __init__(self):
        self.resolution_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "resolution"
        self.resolution_root.mkdir(parents=True, exist_ok=True)
        
        # Human escalation threshold
        # Confidence < 40% means ORB is uncertain - escalate to human
        self.escalation_threshold = 0.4
        
        # Resolution history (for learning what works, not judging cores)
        self.history_file = self.resolution_root / "resolution_history.yaml"
        
    async def resolve_user_escalation(self, worker_id: str, user_query: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point when worker calls for ORB intervention.
        Returns resolution or triggers human escalation.
        """
        print(f"[RESOLUTION] Worker {worker_id} escalated: {user_query[:50]}...")
        
        # Step 1: Gather relevant Core-4 observations
        relevant_observations = self._gather_relevant_observations(user_query, context)
        
        # Step 2: Check if we have sufficient ontological memory
        if not relevant_observations:
            return self._escalate_to_human(
                reason="insufficient_ontological_memory",
                query=user_query,
                worker_id=worker_id
            )
        
        # Step 3: Generate SoftMax consensus
        softmax_result = generate_softmax_consensus(
            observations=relevant_observations,
            matrix=ORB_VESSEL.matrix,
            tension=TENSION_LEDGER
        )
        
        # Step 4: Evaluate resolution confidence
        resolution_confidence = softmax_result["final_confidence"]
        
        # Step 5: Return resolution or escalate
        if resolution_confidence >= self.escalation_threshold:
            return self._generate_resolution(
                softmax_result,
                relevant_observations,
                worker_id,
                user_query,
                confidence=resolution_confidence
            )
        else:
            return self._escalate_to_human(
                reason="low_resolution_confidence",
                query=user_query,
                worker_id=worker_id,
                softmax_data=softmax_result
            )
    
    def _gather_relevant_observations(self, query: str, context: Dict) -> List[Dict]:
        """
        Search ontological matrix for observations relevant to user query.
        Uses semantic similarity and context matching.
        """
        # Get recent observations from all cores (last 100 per core)
        all_obs = []
        for core in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
            obs = ORB_VESSEL.matrix.get_observations_by_core(core, limit=100)
            all_obs.extend(obs)
            
        # Simple relevance scoring (string matching for now)
        relevant = []
        for obs in all_obs:
            relevance = self._calculate_relevance(obs, query, context.get("domain", ""))
            if relevance > 0.3:  # Threshold for relevance
                relevant.append({
                    "observation": obs,
                    "relevance": relevance
                })
                
        # Sort by relevance and return top 20
        relevant.sort(key=lambda x: x["relevance"], reverse=True)
        return relevant[:20]
    
    def _calculate_relevance(self, observation: Dict, query: str, domain: str) -> float:
        """Calculate relevance score between observation and query"""
        # Domain match
        obs_domain = observation["context"].get("domain", "")
        domain_match = 1.0 if obs_domain == domain else 0.5 if obs_domain else 0.0
        
        # Query term overlap
        query_terms = set(query.lower().split())
        obs_text = str(observation["verdict"]).lower()
        obs_terms = set(obs_text.split())
        overlap = len(query_terms & obs_terms) / max(len(query_terms), 1)
        
        # Recency weight
        age_days = (datetime.utcnow() - datetime.fromisoformat(observation["timestamp"])).days
        recency = max(0.0, 1.0 - (age_days / 30.0))
        
        return (domain_match * 0.3) + (overlap * 0.5) + (recency * 0.2)
    
    def _generate_resolution(self, softmax: Dict, observations: List,
                           worker_id: str, query: str, confidence: float) -> Dict:
        """Generate user-facing resolution guidance"""
        consensus_verdict = softmax["consensus_verdict"]
        
        # Generate explanation
        explanation = self._generate_explanation(softmax, observations)
        
        resolution = {
            "status": "RESOLVED",
            "worker_id": worker_id,
            "query": query,
            "verdict": consensus_verdict,
            "confidence": confidence,
            "explanation": explanation,
            "synthesized_from": len(observations),
            "human_escalation_available": True,  # User can always request human
            "resolved_at": datetime.utcnow().isoformat()
        }
        
        # Record resolution for learning
        self._record_resolution(resolution)
        
        return resolution
    
    def _generate_explanation(self, softmax: Dict, observations: List) -> str:
        """Generate human-readable explanation of reasoning"""
        consensus = softmax["consensus_verdict"]
        weights = softmax["core_weights"]
        
        lines = [
            "Based on synthesis of Core-4 observations:",
            ""
        ]
        
        for core, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            confidence = weight * 100
            lines.append(f"- {core}: {confidence:.1f}% confidence in perspective")
            
        lines.extend([
            "",
            f"Consensus recommendation: {consensus.get('recommendation', 'UNKNOWN')}",
            "",
            "Note: This is advisory. Individual cores may have valid alternative perspectives."
        ])
        
        return "\n".join(lines)
    
    def _escalate_to_human(self, reason: str, query: str, worker_id: str,
                          softmax_data: Optional[Dict] = None) -> Dict:
        """Trigger human escalation with full context"""
        escalation = {
            "status": "ESCALATED_TO_HUMAN",
            "reason": reason,
            "worker_id": worker_id,
            "query": query,
            "softmax_data": softmax_data,
            "ontological_context": {
                "tension_level": TENSION_LEDGER.get_summary(),
                "matrix_size": ORB_VESSEL.matrix.get_size(),
                "recent_observations": ORB_VESSEL.matrix.get_observation_count()
            },
            "escalated_at": datetime.utcnow().isoformat(),
            "human_handler": None,  # To be assigned by escalation system
            "priority": "medium" if reason == "low_resolution_confidence" else "high"
        }
        
        # Save escalation record
        self._record_escalation(escalation)
        
        # Trigger notification (placeholder)
        self._notify_human_team(escalation)
        
        return escalation
    
    def _record_resolution(self, resolution: Dict):
        """Record successful resolution for pattern learning"""
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = yaml.safe_load(f) or []
        
        history.append(resolution)
        
        with open(self.history_file, 'w') as f:
            yaml.dump(history, f)
    
    def _record_escalation(self, escalation: Dict):
        """Record escalation patterns for analysis"""
        escalation_file = self.resolution_root / "escalation_history.yaml"
        
        history = []
        if escalation_file.exists():
            with open(escalation_file, 'r') as f:
                history = yaml.safe_load(f) or []
        
        history.append(escalation)
        
        # Keep only last 1000
        if len(history) > 1000:
            history = history[-1000:]
            
        with open(escalation_file, 'w') as f:
            yaml.dump(history, f)
    
    def _notify_human_team(self, escalation: Dict):
        """Notify human team of escalation (placeholder)"""
        # In production, integrate with Slack/Email/PagerDuty
        print(f"\n🚨 HUMAN ESCALATION REQUESTED 🚨")
        print(f"Worker: {escalation['worker_id']}")
        print(f"Reason: {escalation['reason']}")
        print(f"Query: {escalation['query'][:100]}...")
        if escalation.get('softmax_data'):
            print(f"Confidence: {escalation['softmax_data']['consensus_strength']:.1%}")
        else:
            print("Confidence: N/A (insufficient data)")
        print(f"Tension Level: {escalation['ontological_context']['tension_level']['tension_level']:.2f}")
        print("=" * 60)