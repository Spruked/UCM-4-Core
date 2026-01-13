#!/usr/bin/env python3
"""
SoftMax Advisory SKG - Statistical Consensus Engine
Location: UCM_4_Core/CALI/softmax_advisory_skor/consensus_advisor.py

PURPOSE:
  - Takes verdicts from external sibling Core 4 brains
  - Produces confidence-weighted statistical signals
  - Detects outliers using statistical methods
  - Provides Byzantine-resilient advisory (non-authoritative)
  - Deterministic, stateless, never learns or mutates

PRINCIPLE:
  "Advises orchestration, never touches cognition.
   Statistical harmonizer, not a judge."
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class ConsensusLevel(Enum):
    """Statistical consensus thresholds"""
    UNANIMOUS = 0.95      # All cores aligned, high confidence
    STRONG = 0.80         # Clear majority, moderate-high confidence
    WEAK = 0.60           # Simple majority, moderate confidence
    FRAGMENTED = 0.40     # Split decision, caution advised
    CONFLICTED = 0.20     # Significant disagreement, escalation likely

class AdvisoryRecommendation(Enum):
    """Non-authoritative recommendations to CALI"""
    PROCEED = "proceed"                    # High consensus, normal operations
    PROCEED_CAUTIOUSLY = "proceed_cautiously"  # Moderate consensus, monitor closely
    PAUSE_AND_VERIFY = "pause_verify"     # Weak consensus, validate inputs
    ESCALATE_TO_REVIEW = "escalate"       # Conflict detected, manual review needed
    OUTLIER_INVESTIGATION = "investigate_outlier"  # Statistical anomaly detected

@dataclass
class Core4Verdict:
    """Input from a sibling Core 4 brain"""
    core_name: str
    verdict: str  # e.g., "approve", "reject", "defer", "modify"
    confidence: float  # 0.0 to 1.0
    reasoning_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdvisorySignal:
    """Statistical output (non-authoritative)"""
    consensus_level: float  # 0.0 to 1.0
    raw_confidences: List[float]  # Original confidences
    softmax_probabilities: List[float]  # Normalized weights
    dominant_verdict: str  # Verdict with highest weighted score
    outlier_detected: Optional[str]  # Name of statistical outlier
    confidence_clustering: str  # "tight", "moderate", "wide", "bimodal"
    recommendation: AdvisoryRecommendation
    advisory_explanation: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Export for CALI memory storage"""
        return {
            "consensus_level": self.consensus_level,
            "raw_confidences": self.raw_confidences,
            "softmax_probabilities": self.softmax_probabilities,
            "dominant_verdict": self.dominant_verdict,
            "outlier_detected": self.outlier_detected,
            "confidence_clustering": self.confidence_clustering,
            "recommendation": self.recommendation.value,
            "advisory_explanation": self.advisory_explanation,
            "timestamp": self.timestamp
        }

class SoftMaxConsensusAdvisor:
    """
    Statistical Consensus Engine - Deterministic & Stateless
    
    Takes verdicts from external sibling Core 4 brains.
    Outputs confidence-weighted statistical advisory signals.
    
    CHARACTERISTICS:
    ❌ Does NOT reason
    ❌ Does NOT override cores
    ❌ Does NOT learn
    ❌ Does NOT mutate state
    ✅ Purely statistical
    ✅ Deterministic (same input → same output)
    ✅ Advisory only (no authority)
    
    CALI Integration:
    - Called by CALI orchestration logic
    - Output may be written to CALI's immutable memory
    - SoftMax SKG itself never remembers or learns
    """
    
    @staticmethod
    def compute_softmax(confidences: List[float]) -> np.ndarray:
        """
        Compute SoftMax probabilities from confidences
        Deterministic, no state, pure function
        """
        if not confidences:
            return np.array([])
        
        # Convert to numpy array
        conf_array = np.array(confidences, dtype=np.float64)
        
        # Normalize to avoid overflow
        max_conf = np.max(conf_array)
        exp_conf = np.exp(conf_array - max_conf)
        
        # Compute probabilities
        softmax_probs = exp_conf / np.sum(exp_conf)
        
        return softmax_probs
    
    @staticmethod
    def detect_statistical_outlier(confidences: List[float], 
                                   method: str = "iqr") -> Optional[int]:
        """
        Detect statistical outliers in confidence distribution
        Returns index of outlier, or None if none detected
        """
        if len(confidences) < 3:
            return None  # Need at least 3 points for outlier detection
        
        conf_array = np.array(confidences)
        
        if method == "iqr":
            # Interquartile Range method
            q1 = np.percentile(conf_array, 25)
            q3 = np.percentile(conf_array, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find outliers
            outliers = np.where((conf_array < lower_bound) | (conf_array > upper_bound))[0]
            
            # Return the most extreme outlier (highest deviation from median)
            if len(outliers) > 0:
                median = np.median(conf_array)
                deviations = np.abs(conf_array[outliers] - median)
                most_extreme_idx = outliers[np.argmax(deviations)]
                return int(most_extreme_idx)
        
        elif method == "zscore":
            # Z-score method
            mean = np.mean(conf_array)
            std = np.std(conf_array)
            if std == 0:
                return None
            
            z_scores = np.abs((conf_array - mean) / std)
            outliers = np.where(z_scores > 2.0)[0]  # 2 standard deviations
            
            if len(outliers) > 0:
                # Return the one with highest z-score
                return int(outliers[np.argmax(z_scores[outliers])])
        
        return None
    
    @staticmethod
    def analyze_confidence_clustering(confidences: List[float]) -> str:
        """
        Analyze clustering of confidence scores
        Returns clustering pattern description
        """
        if len(confidences) < 2:
            return "insufficient_data"
        
        conf_array = np.array(confidences)
        
        # Compute coefficient of variation
        mean = np.mean(conf_array)
        if mean == 0:
            return "uniform_zero"
        
        std = np.std(conf_array)
        cv = std / mean
        
        # Analyze distribution
        if cv < 0.15:
            return "tight_cluster"  # All similar confidence
        elif cv < 0.35:
            return "moderate_spread"  # Reasonable variation
        elif cv < 0.60:
            return "wide_spread"  # Significant disagreement
        else:
            return "bimodal_fragmented"  # Strongly split opinions
    
    @staticmethod
    def compute_weighted_verdict(verdicts: List[str], 
                                 weights: np.ndarray) -> Tuple[str, float]:
        """
        Compute weighted consensus verdict
        Returns (dominant_verdict, consensus_score)
        """
        if not verdicts or len(weights) == 0:
            return "insufficient_data", 0.0
        
        # Group by verdict
        verdict_scores = {}
        for verdict, weight in zip(verdicts, weights):
            verdict_scores[verdict] = verdict_scores.get(verdict, 0.0) + weight
        
        # Find dominant verdict
        dominant_verdict = max(verdict_scores, key=verdict_scores.get)
        dominant_score = verdict_scores[dominant_verdict]
        
        # Compute consensus level (0 to 1)
        total_weight = np.sum(weights)
        if total_weight == 0:
            consensus_level = 0.0
        else:
            consensus_level = dominant_score / total_weight
        
        return dominant_verdict, float(consensus_level)
    
    @staticmethod
    def map_consensus_to_recommendation(consensus_level: float,
                                       outlier_detected: bool,
                                       clustering: str) -> AdvisoryRecommendation:
        """
        Map statistical metrics to advisory recommendation
        Deterministic mapping, no reasoning
        """
        if outlier_detected and consensus_level < 0.70:
            return AdvisoryRecommendation.OUTLIER_INVESTIGATION
        
        if consensus_level >= ConsensusLevel.UNANIMOUS.value:
            return AdvisoryRecommendation.PROCEED
        elif consensus_level >= ConsensusLevel.STRONG.value:
            return AdvisoryRecommendation.PROCEED_CAUTIOUSLY
        elif consensus_level >= ConsensusLevel.WEAK.value:
            if clustering == "wide_spread" or clustering == "bimodal_fragmented":
                return AdvisoryRecommendation.PAUSE_AND_VERIFY
            return AdvisoryRecommendation.PROCEED_CAUTIOUSLY
        elif consensus_level >= ConsensusLevel.FRAGMENTED.value:
            return AdvisoryRecommendation.PAUSE_AND_VERIFY
        else:
            return AdvisoryRecommendation.ESCALATE_TO_REVIEW
    
    def process_verdicts(self,
                        verdicts: List[Core4Verdict],
                        context: Optional[Dict[str, Any]] = None) -> AdvisorySignal:
        """
        Main entry point: Process verdicts from sibling Core 4 brains
        
        DETERMINISTIC & STATELESS:
        - Same verdicts → same output, every time
        - No memory between calls
        - No learning or adaptation
        
        Args:
            verdicts: List of verdicts from Core 4 siblings
            context: Optional metadata about the decision context
        
        Returns:
            AdvisorySignal: Statistical analysis for CALI's consideration
            
        CALI Integration Pattern:
        # In CALI orchestration logic:
        advisor = SoftMaxConsensusAdvisor()
        
        verdicts = [
            Core4Verdict("KayGee_1.0", "approve", 0.94),
            Core4Verdict("UMC_Core_ECM", "approve", 0.78),
            Core4Verdict("Caleon_Genesis_1.12", "reject", 0.91),  # Outlier?
        ]
        
        advisory = advisor.process_verdicts(verdicts)
        
        # CALI decides what to do (not the advisor)
        if advisory.recommendation == AdvisoryRecommendation.ESCALATE_TO_REVIEW:
            cali_memory.record_authority_command(
                sibling=SiblingCore4.CALEON_GENESIS,
                command="deferred_for_review",
                justification=f"Advisory: {advisory.advisory_explanation}",
                command_params={"consensus_level": advisory.consensus_level}
            )
        """
        if not verdicts:
            return AdvisorySignal(
                consensus_level=0.0,
                raw_confidences=[],
                softmax_probabilities=[],
                dominant_verdict="insufficient_data",
                outlier_detected=None,
                confidence_clustering="insufficient_data",
                recommendation=AdvisoryRecommendation.PAUSE_AND_VERIFY,
                advisory_explanation="No verdicts provided for analysis",
                timestamp=datetime.now().isoformat()
            )
        
        # Extract data from verdicts
        confidences = [v.confidence for v in verdicts]
        verdict_strings = [v.verdict for v in verdicts]
        core_names = [v.core_name for v in verdicts]
        
        # Compute SoftMax probabilities
        softmax_probs = self.compute_softmax(confidences)
        
        # Detect statistical outlier
        outlier_idx = self.detect_statistical_outlier(confidences)
        outlier_name = core_names[outlier_idx] if outlier_idx is not None else None
        
        # Analyze confidence clustering
        clustering = self.analyze_confidence_clustering(confidences)
        
        # Compute weighted consensus
        dominant_verdict, consensus_level = self.compute_weighted_verdict(
            verdict_strings, softmax_probs
        )
        
        # Map to recommendation
        recommendation = self.map_consensus_to_recommendation(
            consensus_level, outlier_name is not None, clustering
        )
        
        # Generate advisory explanation
        explanation = self._generate_explanation(
            consensus_level, dominant_verdict, outlier_name, clustering, verdicts
        )
        
        return AdvisorySignal(
            consensus_level=consensus_level,
            raw_confidences=confidences,
            softmax_probabilities=softmax_probs.tolist() if len(softmax_probs) > 0 else [],
            dominant_verdict=dominant_verdict,
            outlier_detected=outlier_name,
            confidence_clustering=clustering,
            recommendation=recommendation,
            advisory_explanation=explanation,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_explanation(self,
                             consensus_level: float,
                             dominant_verdict: str,
                             outlier_name: Optional[str],
                             clustering: str,
                             verdicts: List[Core4Verdict]) -> str:
        """
        Generate human-readable advisory explanation
        (Statistical reporting, not reasoning)
        """
        parts = []
        
        # Consensus level
        if consensus_level >= 0.95:
            parts.append("Unanimous consensus")
        elif consensus_level >= 0.80:
            parts.append("Strong consensus")
        elif consensus_level >= 0.60:
            parts.append("Moderate consensus")
        elif consensus_level >= 0.40:
            parts.append("Fragmented opinions")
        else:
            parts.append("Significant disagreement")
        
        # Dominant verdict
        parts.append(f"dominant verdict: {dominant_verdict}")
        
        # Clustering
        if clustering == "tight_cluster":
            parts.append("confidences tightly clustered")
        elif clustering == "moderate_spread":
            parts.append("moderate confidence variation")
        elif clustering == "wide_spread":
            parts.append("significant confidence disagreement")
        elif clustering == "bimodal_fragmented":
            parts.append("opinions strongly split")
        
        # Outlier
        if outlier_name:
            parts.append(f"outlier detected: {outlier_name}")
        
        # Verdict distribution
        verdict_counts = {}
        for v in verdicts:
            verdict_counts[v.verdict] = verdict_counts.get(v.verdict, 0) + 1
        
        distribution_str = ", ".join([f"{k}:{v}" for k, v in verdict_counts.items()])
        parts.append(f"distribution ({distribution_str})")
        
        return "; ".join(parts)

# Helper function for CALI orchestration
def process_core4_consensus(core4_verdicts: List[Dict[str, Any]]) -> AdvisorySignal:
    """
    Convenience function for CALI orchestration code
    
    Args:
        core4_verdicts: Raw verdicts from Core 4 siblings
        Example:
        [
            {"core": "KayGee_1.0", "verdict": "approve", "confidence": 0.94},
            {"core": "UMC_Core_ECM", "verdict": "approve", "confidence": 0.78},
            ...
        ]
    
    Returns:
        AdvisorySignal for CALI's decision-making
    """
    advisor = SoftMaxConsensusAdvisor()
    
    verdict_objects = [
        Core4Verdict(
            core_name=v["core"],
            verdict=v["verdict"],
            confidence=v["confidence"],
            reasoning_summary=v.get("reasoning"),
            metadata=v.get("metadata", {})
        )
        for v in core4_verdicts
    ]
    
    return advisor.process_verdicts(verdict_objects)