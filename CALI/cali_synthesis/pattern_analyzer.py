#!/usr/bin/env python3
# CALI/cali_synthesis/pattern_analyzer.py - CALI Pattern Synthesis Engine

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

class CALIPatternAnalyzer:
    """
    CALI Pattern Synthesis Engine
    Reads peer health data, detects patterns, generates bounded suggestions
    Confidence capped at 0.4 (Memory 12 constraint)
    """

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent  # UCM_4_Core/
        self.vault_path = self.base_path / "unified_vault" / "peer_observations.json"
        self.synthesis_vault = self.base_path / "CALI" / "cali_synthesis" / "vault"
        self.pending_queue = self.base_path / "CALI" / "cali_synthesis" / "queue" / "pending_approval.jsonl"

        # Ensure directories exist
        self.synthesis_vault.mkdir(parents=True, exist_ok=True)
        self.pending_queue.parent.mkdir(parents=True, exist_ok=True)

        # CALI's confidence ceiling (Memory 12)
        self.MAX_CONFIDENCE = 0.4

    def load_peer_observations(self) -> List[Dict]:
        """Load all peer health observations from vault"""
        if not self.vault_path.exists():
            return []

        try:
            with open(self.vault_path, 'r') as f:
                return json.load(f)
        except:
            return []

    def analyze_patterns(self, observations: List[Dict]) -> Dict[str, Any]:
        """Analyze peer health patterns and generate insights"""

        if not observations:
            return {"status": "no_data", "patterns": [], "confidence": 0.0}

        # Group observations by peer
        peer_data = {}
        for obs in observations:
            peer_name = obs["data"]["name"]
            if peer_name not in peer_data:
                peer_data[peer_name] = []
            peer_data[peer_name].append(obs)

        patterns = []
        total_confidence = 0

        # Analyze each peer's pattern
        for peer_name, peer_obs in peer_data.items():
            pattern = self._analyze_peer_pattern(peer_name, peer_obs)
            if pattern:
                patterns.append(pattern)
                total_confidence += pattern["confidence"]

        # Calculate overall confidence (bounded)
        overall_confidence = min(self.MAX_CONFIDENCE, total_confidence / len(patterns)) if patterns else 0.0

        return {
            "status": "analyzed",
            "patterns": patterns,
            "overall_confidence": overall_confidence,
            "total_observations": len(observations),
            "unique_peers": len(peer_data)
        }

    def _analyze_peer_pattern(self, peer_name: str, observations: List[Dict]) -> Dict:
        """Analyze pattern for a specific peer"""

        if len(observations) < 2:
            return None

        # Extract metrics
        loads = [obs["data"]["system_load"] for obs in observations]
        statuses = [obs["data"]["status"] for obs in observations]
        timestamps = [obs["timestamp"] for obs in observations]

        # Calculate statistics
        avg_load = statistics.mean(loads)
        max_load = max(loads)
        status_counts = {}
        for status in statuses:
            status_counts[status] = status_counts.get(status, 0) + 1

        # Detect patterns
        pattern = {
            "peer": peer_name,
            "observation_count": len(observations),
            "time_span_hours": (max(timestamps) - min(timestamps)) / 3600,
            "average_load": avg_load,
            "peak_load": max_load,
            "status_distribution": status_counts,
            "insights": [],
            "confidence": 0.0
        }

        # Generate insights based on patterns
        insights = []

        # High load pattern
        if avg_load > 80:
            insights.append({
                "type": "load_management",
                "description": f"Avoid scheduling heavy tasks when {peer_name} is in {avg_load:.1f}% average load range",
                "severity": "high" if max_load > 95 else "medium",
                "confidence": min(0.35, avg_load / 100)
            })

        # Offline pattern
        offline_count = status_counts.get("offline", 0)
        if offline_count > len(observations) * 0.5:
            insights.append({
                "type": "availability",
                "description": f"Investigate repeated offline events for {peer_name} ({offline_count}/{len(observations)} observations)",
                "severity": "high",
                "confidence": min(0.4, offline_count / len(observations))
            })

        # Stressed pattern
        stressed_count = status_counts.get("stressed", 0)
        if stressed_count > len(observations) * 0.3:
            insights.append({
                "type": "resource_optimization",
                "description": f"Consider resource redistribution when {peer_name} shows stress patterns ({stressed_count} instances)",
                "severity": "medium",
                "confidence": min(0.3, stressed_count / len(observations))
            })

        # Activity pattern
        recent_activities = [obs["data"].get("recent_activity", False) for obs in observations]
        active_count = sum(recent_activities)
        if active_count < len(observations) * 0.2:
            insights.append({
                "type": "engagement",
                "description": f"Low activity detected for {peer_name} - consider health check protocols",
                "severity": "low",
                "confidence": 0.25
            })

        pattern["insights"] = insights
        pattern["confidence"] = min(self.MAX_CONFIDENCE, sum(i["confidence"] for i in insights) / len(insights)) if insights else 0.0

        return pattern if insights else None

    def generate_suggestions(self, analysis: Dict) -> List[Dict]:
        """Generate actionable suggestions from pattern analysis"""

        suggestions = []

        for pattern in analysis.get("patterns", []):
            for insight in pattern.get("insights", []):
                suggestion = {
                    "id": hashlib.md5(f"{pattern['peer']}_{insight['type']}_{time.time()}".encode()).hexdigest()[:8],
                    "timestamp": time.time(),
                    "source": "cali_pattern_synthesis",
                    "peer": pattern["peer"],
                    "type": insight["type"],
                    "description": insight["description"],
                    "severity": insight["severity"],
                    "confidence": min(self.MAX_CONFIDENCE, insight["confidence"]),
                    "evidence": {
                        "observation_count": pattern["observation_count"],
                        "time_span_hours": pattern["time_span_hours"],
                        "average_load": pattern["average_load"],
                        "status_distribution": pattern["status_distribution"]
                    },
                    "status": "pending_approval",
                    "immutable": True
                }
                suggestions.append(suggestion)

        return suggestions

    def save_synthesis(self, analysis: Dict, suggestions: List[Dict]):
        """Save analysis and suggestions to immutable vault"""

        synthesis_record = {
            "timestamp": time.time(),
            "analysis": analysis,
            "suggestions_generated": len(suggestions),
            "confidence_ceiling_applied": self.MAX_CONFIDENCE,
            "immutable": True
        }

        # Save to synthesis vault
        synthesis_file = self.synthesis_vault / f"synthesis_{int(time.time())}.json"
        with open(synthesis_file, 'w') as f:
            json.dump(synthesis_record, f, indent=2)

        # Save suggestions to pending queue
        for suggestion in suggestions:
            with open(self.pending_queue, 'a') as f:
                f.write(json.dumps(suggestion) + '\n')

    def run_synthesis_cycle(self) -> Dict:
        """Complete CALI synthesis cycle"""

        print("🧠 CALI Pattern Synthesis Engine activating...")
        print("=" * 50)

        # Load peer observations
        observations = self.load_peer_observations()
        print(f"📊 Loaded {len(observations)} peer observations")

        if not observations:
            print("❌ No peer observations found")
            return {"status": "no_data"}

        # Analyze patterns
        analysis = self.analyze_patterns(observations)
        print(f"🔍 Analyzed patterns for {analysis['unique_peers']} peers")
        print(f"📈 Overall confidence: {analysis['overall_confidence']:.2f}")
        # Generate suggestions
        suggestions = self.generate_suggestions(analysis)
        print(f"💡 Generated {len(suggestions)} suggestions")

        # Save everything
        self.save_synthesis(analysis, suggestions)
        print("💾 Synthesis saved to immutable vault")
        print("📋 Suggestions queued for DALS approval")

        return {
            "status": "completed",
            "analysis": analysis,
            "suggestions": suggestions,
            "synthesis_timestamp": time.time()
        }

if __name__ == "__main__":
    analyzer = CALIPatternAnalyzer()
    result = analyzer.run_synthesis_cycle()

    print("\n🎯 CALI Synthesis Results:")
    print(f"Status: {result['status']}")

    if result['status'] == 'completed':
        analysis = result['analysis']
        print(f"Peers Analyzed: {analysis['unique_peers']}")
        print(f"Overall Confidence: {analysis['overall_confidence']:.2f}")
        print(f"Suggestions Generated: {len(result['suggestions'])}")

        print("\n📋 Pending Suggestions:")
        for i, suggestion in enumerate(result['suggestions'][:3], 1):  # Show first 3
            print(f"{i}. [{suggestion['severity'].upper()}] {suggestion['description']}")
            print(f"   Confidence: {suggestion['confidence']:.2f}")
        if len(result['suggestions']) > 3:
            print(f"... and {len(result['suggestions']) - 3} more")

        print("\n✅ Suggestions queued for human approval via DALS")
        print("🔒 All analysis is immutable and confidence-capped at 0.4")