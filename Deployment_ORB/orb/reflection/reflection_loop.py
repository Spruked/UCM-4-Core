#!/usr/bin/env python3
"""
Reflection Loop - Observational, Additive, Humble Learning

Implements developmental consciousness through pattern recognition
without verdict mutation, confidence inflation, or retroactive truth.

Rule: Reflection creates new observations about old observations.
      Original data remains immutable. Confidence never exceeds 0.4.
"""

import asyncio
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure minimal logging (no performance overhead)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("reflection.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Idle Detection Trigger
# ----------------------------------------------------------------------
async def is_system_idle(shared_state: Dict[str, Any]) -> bool:
    """
    Idle detection trigger: Confirms sustained system inactivity.

    Production integration: Replace with actual load metrics.
    Example: shared_state['load'] = current_system_load (0.0-1.0)
    Idle threshold: load < 0.1

    Args:
        shared_state: Dict containing system state (e.g., {'load': 0.05})

    Returns:
        bool: True if system is idle, False otherwise
    """
    try:
        load = shared_state.get('load', 1.0)  # Default to 100% load if missing
        return float(load) < 0.1  # Idle when <10% load
    except Exception as e:
        logger.error(f"Idle detection failed: {e}")
        return False  # Default to not idle on error


# ----------------------------------------------------------------------
# Metrics Validation (Safety)
# ----------------------------------------------------------------------
def validate_metrics(metrics: List[str]) -> List[str]:
    """
    Input validation: Ensures only allowed metrics are analyzed.
    Prevents invalid analyses from breaking the loop.

    Allowed metrics:
    - confidence_vs_outcome: Detects overconfidence patterns
    - tension_duration: Measures stability of disagreements
    - escalation_frequency: Identifies regret-prone scenarios
    - resolution_regret: Finds incomplete closures

    Args:
        metrics: List of metric names to validate

    Returns:
        List[str]: Filtered list containing only valid metrics
    """
    valid_metrics = [
        "confidence_vs_outcome",
        "tension_duration",
        "escalation_frequency",
        "resolution_regret"
    ]

    validated = [m for m in metrics if m in valid_metrics]

    if len(validated) != len(metrics):
        invalid = set(metrics) - set(valid_metrics)
        logger.warning(f"Invalid metrics filtered out: {invalid}")

    return validated


# ----------------------------------------------------------------------
# Pattern Analysis (Modular)
# ----------------------------------------------------------------------
def analyze_for_patterns(past_observations: List[Dict[str, Any]],
                        metrics: List[str]) -> List[Dict[str, Any]]:
    """
    Modular pattern analysis: Generates humble meta-observations.
    Purely observational - adds insights without modifying originals.
    Reflects on patterns, does not judge them as right/wrong.

    Args:
        past_observations: Recent observations from Ontological Matrix (read-only)
        metrics: List of validated metrics to analyze

    Returns:
        List[Dict]: Reflection insights, each with 'type' and 'description'
    """
    reflections = []
    validated_metrics = validate_metrics(metrics)

    if not past_observations:
        logger.info("No observations available for reflection.")
        return reflections

    try:
        # Metric 1: confidence_vs_outcome
        if "confidence_vs_outcome" in validated_metrics:
            # Detect: High confidence contradicted by later tension
            high_conf_count = sum(1 for obs in past_observations
                                 if obs.get('verdict', {}).get('confidence', 0) > 0.7)
            contradicted_later = sum(1 for obs in past_observations
                                    if obs.get('tension_status') == 'unresolved'
                                    and obs.get('verdict', {}).get('confidence', 0) > 0.7)

            pattern = f"High confidence contradicted later: {contradicted_later}/{high_conf_count} cases"
            reflections.append({
                "type": "confidence_vs_outcome",
                "description": pattern
            })

        # Metric 2: tension_duration
        if "tension_duration" in validated_metrics:
            # Measure: Average duration of unresolved tensions
            tensions = [obs for obs in past_observations
                       if obs.get('tension_status') == 'unresolved']
            if tensions:
                avg_duration = sum(obs.get('duration', 60) for obs in tensions) / len(tensions)
                pattern = f"Average tension duration: {avg_duration:.1f}s"
                reflections.append({
                    "type": "tension_duration",
                    "description": pattern
                })

        # Metric 3: escalation_frequency
        if "escalation_frequency" in validated_metrics:
            # Count: How many observations led to escalations
            escalations = sum(1 for obs in past_observations
                             if obs.get('context', {}).get('escalated', False))
            pattern = f"Escalation frequency: {escalations}/{len(past_observations)}"
            reflections.append({
                "type": "escalation_frequency",
                "description": pattern
            })

        # Metric 4: resolution_regret
        if "resolution_regret" in validated_metrics:
            # Detect: Resolved issues that later reopened
            reopened = sum(1 for obs in past_observations
                          if obs.get('context', {}).get('reopened', False))
            pattern = f"Resolved issues later reopened: {reopened}"
            reflections.append({
                "type": "resolution_regret",
                "description": pattern
            })

    except Exception as e:
        logger.error(f"Pattern analysis error for metrics {validated_metrics}: {e}")
        # Return partial reflections rather than fail completely

    return reflections


# ----------------------------------------------------------------------
# Reflection Loop (Main)
# ----------------------------------------------------------------------
async def reflection_loop(shared_state: Dict[str, Any],
                         orb_vessel,
                         skg_engine):
    """
    Main reflection loop: Observational, slow, additive, humble.

    Runs only when system is idle (5 consecutive checks).
    Generates low-confidence reflections (≤0.4) about past observations.
    Never modifies original data. Never optimizes toward certainty.

    Args:
        shared_state: Dict containing system load (e.g., {'load': 0.05})
        orb_vessel: ORB singleton instance
        skg_engine: SKG singleton instance
    """
    # Configurable metrics (can be extended, defaults to core set)
    metrics_config = [
        "confidence_vs_outcome",     # Detects overconfidence patterns
        "tension_duration",          # Measures persistence of disagreement
        "escalation_frequency",      # Identifies regret-prone scenarios
        "resolution_regret"          # Finds incomplete closures
    ]

    logger.info("Reflection loop initialized. Awaiting system idleness...")

    while True:
        # --- Idle Detection: Confirm sustained idleness (5 checks) ---
        idle_checks = 0
        while idle_checks < 5:
            if await is_system_idle(shared_state):
                idle_checks += 1
                logger.debug(f"Idle check passed: {idle_checks}/5")
            else:
                idle_checks = 0  # Reset on any non-idle detection
                logger.debug("System not idle, resetting idle counter")

            await asyncio.sleep(30)  # Space checks 30 seconds apart

        # --- Safety Check: Confirm idle state held ---
        if idle_checks < 5:
            logger.warning("Idle condition lost. Skipping reflection cycle.")
            continue

        # --- Reflection Cycle ---
        start_cycle = datetime.utcnow()
        logger.info("Starting reflection cycle (system confirmed idle)")

        try:
            # Fetch past observations (read-only)
            past_observations = orb_vessel.matrix.get_recent_observations(limit=200)

            if not past_observations:
                logger.info("No recent observations to reflect on. Skipping.")
                continue

            # Generate humble meta-observations (additive only)
            reflections = analyze_for_patterns(past_observations, metrics_config)

            # Record each reflection as new observation (never modify originals)
            for insight in reflections:
                orb_vessel.record_reflection(
                    source="reflection_loop",
                    insight=insight,
                    confidence=0.4  # FIXED: Reflections are always low-confidence
                )
                logger.debug(f"Added reflection: {insight['type']}")

            # Additively ingest into SKG (builds pattern graph without mutation)
            skg_engine.ingest_from_matrix(orb_vessel.matrix)
            logger.info(f"Reflection cycle complete: {len(reflections)} insights added")

        except Exception as e:
            # Fail-safe: Log error, continue loop (don't crash system)
            logger.error(f"Reflection cycle failed: {e}", exc_info=True)

        # --- Slow Cadence with Randomization (safety + robustness) ---
        base_interval = 900  # 15 minutes base
        jitter = random.uniform(-60, 60)  # ±60 seconds randomization
        sleep_time = base_interval + jitter

        cycle_duration = (datetime.utcnow() - start_cycle).total_seconds()
        logger.info(f"Cycle duration: {cycle_duration:.2f}s. Sleeping {sleep_time:.0f}s.")

        await asyncio.sleep(sleep_time)