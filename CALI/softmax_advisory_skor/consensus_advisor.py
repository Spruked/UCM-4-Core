#!/usr/bin/env python3
"""
SoftMax Advisory SKG - Statistical Consensus Engine v2.1
Location: UCM_4_Core/CALI/softmax_advisory_skor/consensus_advisor.py

PURPOSE:
  - Byzantine-resilient statistical aggregation of Core 4 verdicts
  - Confidence-weighted softmax fusion with outlier detection
  - Purely advisory: never overrides, never learns, fully deterministic
  - Emphasizes transparency, clustering analysis, and disagreement signaling
"""

import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

import numpy as np

logger = logging.getLogger(__name__)


# ==================== CONFIGURATION CONSTANTS ====================

class Config:
    """Magic numbers as named constants."""
    OUTLIER_Z_THRESHOLD = 2.5
    CLUSTERING_CV_THRESHOLDS = (0.10, 0.25, 0.50, 0.80)
    ENTROPY_HIGH_THRESHOLD = 0.7
    ENTROPY_LOW_THRESHOLD = 0.2
    MIN_CORES_FOR_CONSENSUS = 2
    MAX_EXPLANATION_LENGTH = 300


# ==================== ENUMS ====================

class ConsensusLevel(Enum):
    UNANIMOUS = 0.95
    STRONG = 0.80
    MODERATE = 0.60
    FRAGMENTED = 0.40
    CONFLICTED = 0.20


class AdvisoryRecommendation(Enum):
    PROCEED = auto()
    PROCEED_CAUTIOUSLY = auto()
    PAUSE_AND_VERIFY = auto()
    ESCALATE_TO_REVIEW = auto()
    INVESTIGATE_OUTLIER = auto()
    ABSTAIN_INSUFFICIENT = auto()


# ==================== DATA STRUCTURES ====================

@dataclass(frozen=True)
class Core4Verdict:
    """Validated Core 4 verdict container."""
    core_name: str
    verdict: str
    confidence: float  # Must be in [0.0, 1.0]
    reasoning_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Runtime validation."""
        if not isinstance(self.core_name, str) or not self.core_name.strip():
            raise ValueError("core_name must be a non-empty string")
        if not isinstance(self.verdict, str) or not self.verdict.strip():
            raise ValueError("verdict must be a non-empty string")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")
        if np.isnan(self.confidence) or np.isinf(self.confidence):
            raise ValueError("confidence cannot be NaN or infinite")


@dataclass(frozen=True)
class AdvisorySignal:
    """Immutable advisory signal with strict validation."""
    consensus_level: float
    raw_confidences: Tuple[float, ...]
    softmax_weights: Tuple[float, ...]
    dominant_verdict: str
    verdict_distribution: Dict[str, int]
    outlier_core: Optional[str]
    confidence_clustering: str
    effective_entropy: float
    recommendation: AdvisoryRecommendation
    advisory_explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate signal integrity."""
        if not (0.0 <= self.consensus_level <= 1.0):
            raise ValueError(f"consensus_level must be in [0.0, 1.0], got {self.consensus_level}")
        if not isinstance(self.raw_confidences, (tuple, list)) or len(self.raw_confidences) == 0:
            raise ValueError("raw_confidences must be a non-empty sequence")
        if not isinstance(self.softmax_weights, (tuple, list)) or len(self.softmax_weights) == 0:
            raise ValueError("softmax_weights must be a non-empty sequence")
        if len(self.raw_confidences) != len(self.softmax_weights):
            raise ValueError("confidence and weight arrays must have same length")
        if not isinstance(self.dominant_verdict, str) or not self.dominant_verdict.strip():
            raise ValueError("dominant_verdict must be a non-empty string")
        if not (0.0 <= self.effective_entropy <= 1.0 + 1e-9):  # Allow tiny floating point error
            raise ValueError(f"effective_entropy must be in [0.0, 1.0], got {self.effective_entropy}")

    def to_dict(self) -> Dict[str, Any]:
        """Export to serializable dict."""
        return {
            "consensus_level": round(self.consensus_level, 4),
            "raw_confidences": list(self.raw_confidences),
            "softmax_weights": list(self.softmax_weights),
            "dominant_verdict": self.dominant_verdict,
            "verdict_distribution": dict(self.verdict_distribution),
            "outlier_core": self.outlier_core,
            "confidence_clustering": self.confidence_clustering,
            "effective_entropy": round(self.effective_entropy, 4),
            "recommendation": self.recommendation.name,
            "advisory_explanation": self.advisory_explanation[:Config.MAX_EXPLANATION_LENGTH],
            "timestamp": self.timestamp,
        }


# ==================== CORE LOGIC ====================

class SoftMaxConsensusAdvisor:
    """Stateless, deterministic, Byzantine-resilient consensus advisor"""
    
    def __init__(self):
        """Initialize with no state - purely functional."""
        self._epsilon = 1e-12  # Numerical stability constant

    def _safe_softmax(self, confidences: np.ndarray) -> np.ndarray:
        """
        Numerically stable softmax with edge case handling.
        Returns uniform distribution if all inputs are -inf or NaN.
        """
        if confidences.size == 0:
            return np.array([], dtype=np.float64)
        
        # Guard against NaN/inf
        if not np.all(np.isfinite(confidences)):
            logger.warning("Non-finite values detected in confidences, sanitizing")
            confidences = np.nan_to_num(confidences, nan=0.0, posinf=1.0, neginf=0.0)
        
        # If all values are identical, return uniform distribution
        if np.max(confidences) == np.min(confidences):
            return np.full_like(confidences, 1.0 / len(confidences))
        
        shifted = confidences - confidences.max()
        exp_shifted = np.exp(shifted)
        result = exp_shifted / (exp_shifted.sum() + self._epsilon)
        return result

    def _detect_outlier_modified_zscore(
        self, confidences: np.ndarray, threshold: float = Config.OUTLIER_Z_THRESHOLD
    ) -> Optional[int]:
        """
        Modified Z-score for outlier detection (robust for small samples).
        Returns None if no outlier or insufficient data.
        """
        n = len(confidences)
        if n < 3:
            return None
        
        # Guard against NaN/inf
        if not np.all(np.isfinite(confidences)):
            return None
        
        median = np.median(confidences)
        mad = np.median(np.abs(confidences - median))
        
        if mad == 0:
            return None  # All identical
        
        modified_z = 0.6745 * (confidences - median) / mad
        abs_z = np.abs(modified_z)
        outlier_idx = int(np.argmax(abs_z))
        
        return outlier_idx if abs_z[outlier_idx] > threshold else None

    def _confidence_clustering_cv(self, confidences: np.ndarray) -> str:
        """Coefficient of variation for clustering assessment."""
        n = len(confidences)
        if n < 2:
            return "insufficient"
        
        if not np.all(np.isfinite(confidences)):
            return "invalid_values"
        
        mean = confidences.mean()
        if mean == 0:
            return "uniform_zero"
        
        cv = confidences.std() / mean
        
        thresholds = Config.CLUSTERING_CV_THRESHOLDS
        if cv < thresholds[0]:
            return "very_tight"
        if cv < thresholds[1]:
            return "tight"
        if cv < thresholds[2]:
            return "moderate"
        if cv < thresholds[3]:
            return "wide"
        return "highly_fragmented"

    def _normalized_shannon_entropy(self, probs: np.ndarray) -> float:
        """Normalized entropy: 0 (perfect consensus) → 1 (uniform disagreement)."""
        if probs.size == 0:
            return 0.0
        
        if not np.all(np.isfinite(probs)):
            return 0.0
        
        # Remove zero probabilities to avoid log(0)
        probs = probs[probs > 0]
        if len(probs) == 0:
            return 0.0
        
        entropy = -(probs * np.log2(probs)).sum()
        max_entropy = np.log2(len(probs)) if len(probs) > 1 else 1.0
        
        return float(entropy / max_entropy if max_entropy > 0 else 0.0)

    def _weighted_verdict_consensus(
        self, verdicts: List[str], weights: np.ndarray
    ) -> Tuple[str, float, Dict[str, int]]:
        """Determine dominant verdict using softmax-weighted voting."""
        if not verdicts:
            return "no_verdicts", 0.0, {}
        
        if not np.all(np.isfinite(weights)):
            weights = np.ones_like(weights) / len(weights)  # Fallback to uniform
        
        counter = Counter(verdicts)
        total_weight = float(weights.sum())
        
        if total_weight <= self._epsilon:
            # Fallback to majority if weights are degenerate
            dominant = max(counter, key=counter.get)
            consensus = counter[dominant] / len(verdicts)
        else:
            weighted_scores = {
                verdict: sum(weights[i] for i, v in enumerate(verdicts) if v == verdict)
                for verdict in counter
            }
            dominant = max(weighted_scores, key=weighted_scores.get)
            consensus = weighted_scores[dominant] / total_weight
        
        return dominant, consensus, dict(counter)

    def _map_to_recommendation(
        self,
        consensus: float,
        entropy: float,
        outlier: bool,
        clustering: str,
        n_cores: int
    ) -> AdvisoryRecommendation:
        """Map consensus metrics to concrete advisory recommendation."""
        if n_cores < Config.MIN_CORES_FOR_CONSENSUS:
            return AdvisoryRecommendation.ABSTAIN_INSUFFICIENT
        
        if outlier and consensus < 0.75:
            return AdvisoryRecommendation.INVESTIGATE_OUTLIER
        
        if consensus >= ConsensusLevel.UNANIMOUS.value and entropy < Config.ENTROPY_LOW_THRESHOLD:
            return AdvisoryRecommendation.PROCEED
        
        if consensus >= ConsensusLevel.STRONG.value and entropy < 0.40:
            return AdvisoryRecommendation.PROCEED_CAUTIOUSLY
        
        if consensus >= ConsensusLevel.MODERATE.value:
            if clustering in ("wide", "highly_fragmented") or entropy > Config.ENTROPY_HIGH_THRESHOLD:
                return AdvisoryRecommendation.PAUSE_AND_VERIFY
            return AdvisoryRecommendation.PROCEED_CAUTIOUSLY
        
        if consensus >= ConsensusLevel.FRAGMENTED.value:
            return AdvisoryRecommendation.PAUSE_AND_VERIFY
        
        return AdvisoryRecommendation.ESCALATE_TO_REVIEW

    def _generate_explanation(
        self,
        consensus_level: float,
        dominant: str,
        distribution: Dict[str, int],
        outlier: Optional[str],
        clustering: str,
        entropy: float,
        verdicts: List[Core4Verdict]
    ) -> str:
        """Generate human-readable explanation with conciseness limits."""
        parts = []
        
        # Consensus strength with semantic labels
        if consensus_level >= 0.95:
            parts.append("Near-unanimous agreement")
        elif consensus_level >= 0.80:
            parts.append("Strong weighted consensus")
        elif consensus_level >= 0.60:
            parts.append("Moderate consensus")
        elif consensus_level >= 0.40:
            parts.append("Fragmented alignment")
        else:
            parts.append("Deep disagreement detected")
        
        parts.append(f"→ dominant: {dominant} ({consensus_level:.1%})")
        
        # Distribution summary (concise)
        if len(distribution) <= 3:
            dist_str = ", ".join(f"{k}:{v}" for k, v in sorted(distribution.items()))
        else:
            top2 = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:2]
            dist_str = f"{top2[0][0]}:{top2[0][1]}, {top2[1][0]}:{top2[1][1]} (+{len(distribution)-2} more)"
        
        parts.append(f"votes: {dist_str}")
        
        # Confidence clustering
        clustering_readable = clustering.replace('_', ' ')
        if clustering == "very_tight":
            parts.append("confidences highly aligned")
        elif clustering == "highly_fragmented":
            parts.append(f"confidences {clustering_readable}")
        else:
            parts.append(f"confidence spread: {clustering_readable}")
        
        # Entropy signal (only if notable)
        if entropy < 0.2:
            parts.append("low decision entropy")
        elif entropy > 0.7:
            parts.append("high uncertainty (split council)")
        
        # Outlier detection (only if present)
        if outlier:
            parts.append(f"statistical outlier: {outlier}")
        
        explanation = "; ".join(parts)
        return explanation[:Config.MAX_EXPLANATION_LENGTH]

    def process_verdicts(
        self,
        verdicts: List[Core4Verdict],
        context: Optional[Dict[str, Any]] = None  # Reserved for future context injection
    ) -> AdvisorySignal:
        """
        Main entry point: process Core 4 verdicts and return advisory signal.
        
        Args:
            verdicts: List of validated Core4Verdict objects
            context: Optional context dict (currently unused, reserved for future)
            
        Returns:
            AdvisorySignal with consensus analysis and recommendation
        """
        if not verdicts:
            return AdvisorySignal(
                consensus_level=0.0,
                raw_confidences=(),
                softmax_weights=(),
                dominant_verdict="no_input",
                verdict_distribution={},
                outlier_core=None,
                confidence_clustering="insufficient",
                effective_entropy=0.0,
                recommendation=AdvisoryRecommendation.ABSTAIN_INSUFFICIENT,
                advisory_explanation="No Core 4 verdicts received",
            )
        
        # Extract and validate data
        try:
            confidences = np.array([v.confidence for v in verdicts], dtype=np.float64)
            verdict_strs = [v.verdict for v in verdicts]
            core_names = [v.core_name for v in verdicts]
        except (AttributeError, TypeError) as e:
            raise ValueError(f"Invalid verdict structure: {e}")
        
        # Softmax weighting (with edge case handling)
        softmax_weights = self._safe_softmax(confidences)
        
        # Outlier detection
        outlier_idx = self._detect_outlier_modified_zscore(confidences)
        outlier_core = core_names[outlier_idx] if outlier_idx is not None else None
        
        # Clustering & entropy analysis
        clustering = self._confidence_clustering_cv(confidences)
        entropy = self._normalized_shannon_entropy(softmax_weights)
        
        # Weighted consensus determination
        dominant_verdict, consensus_level, distribution = self._weighted_verdict_consensus(
            verdict_strs, softmax_weights
        )
        
        # Map to recommendation
        recommendation = self._map_to_recommendation(
            consensus_level, entropy, outlier_core is not None, clustering, len(verdicts)
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            consensus_level, dominant_verdict, distribution,
            outlier_core, clustering, entropy, verdicts
        )
        
        return AdvisorySignal(
            consensus_level=round(consensus_level, 4),
            raw_confidences=tuple(float(c) for c in confidences),
            softmax_weights=tuple(float(w) for w in softmax_weights),
            dominant_verdict=dominant_verdict,
            verdict_distribution=distribution,
            outlier_core=outlier_core,
            confidence_clustering=clustering,
            effective_entropy=round(entropy, 4),
            recommendation=recommendation,
            advisory_explanation=explanation,
        )


# ==================== CONVENIENCE WRAPPER ====================

def process_core4_consensus(core4_verdicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process raw Core 4 verdicts and return advisory signal as dict.
    
    Args:
        core4_verdicts: List of dicts with keys: core, verdict, confidence, reasoning, metadata
        
    Returns:
        AdvisorySignal serialized as dict (safe for JSON encoding)
    """
    if not isinstance(core4_verdicts, list):
        raise TypeError("core4_verdicts must be a list")
    
    advisor = SoftMaxConsensusAdvisor()
    
    try:
        verdicts = [
            Core4Verdict(
                core_name=v["core"],
                verdict=v["verdict"],
                confidence=float(v["confidence"]),
                reasoning_summary=v.get("reasoning"),
                metadata=v.get("metadata", {}),
            )
            for v in core4_verdicts
        ]
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid verdict structure in list: {e}")
    
    signal = advisor.process_verdicts(verdicts)
    return signal.to_dict()