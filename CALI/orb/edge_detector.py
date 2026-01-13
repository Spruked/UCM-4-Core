#!/usr/bin/env python3
"""
Edge Detector - Real-Time Clutter Detection
Monitors SKG graph for low-confidence edges and triggers repair.
Runs as background service in ORB observation loop.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import numpy as np
from .skg_engine import SKG_ENGINE

class EdgeDetector:
    """
    Continuously monitors SKG edges for clutter.
    Triggers self-repair when confidence is high enough.
    Logs all detections for audit.
    """
    
    def __init__(self):
        self.detector_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "edge_detection"
        self.detector_root.mkdir(parents=True, exist_ok=True)
        
        # Detection threshold (adapts based on repair success)
        self.detection_threshold = 0.35
        
        # Background monitoring task
        self.is_monitoring = False
        self.monitor_task = None
        
        # Persistence
        self.detection_log = self.detector_root / "detection_log.yaml"
        
    async def start_monitoring(self):
        """Start background edge monitoring (runs every 30 seconds)"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(
            self._monitor_loop(),
            name="EdgeDetectorMonitor"
        )
        print("[EDGE DETECTOR] Clutter monitoring started")
        
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
        print("[EDGE DETECTOR] Clutter monitoring stopped")
        
    async def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.is_monitoring:
            try:
                # Detect clutter edges
                clutter_edges = SKG_ENGINE.detect_clutter_edges()
                
                if clutter_edges:
                    print(f"[EDGE DETECTOR] Found {len(clutter_edges)} potential clutter edges")
                    await self._evaluate_and_repair(clutter_edges)
                
                # Adapt thresholds every hour
                if datetime.utcnow().minute == 0:
                    SKG_ENGINE.adapt_thresholds()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[EDGE DETECTOR] Monitor error (recovered): {e}")
                await asyncio.sleep(5)
    
    async def _evaluate_and_repair(self, clutter_edges: List[Dict[str, Any]]):
        """Evaluate clutter edges and trigger repairs if warranted"""
        for edge in clutter_edges:
            edge_id = edge["edge_id"]
            current_confidence = edge["confidence"]
            clutter_score = edge["clutter_score"]
            
            # Check if we have enough evidence to repair
            # Need 3+ supporting observations from same domain
            supporting_obs = self._find_supporting_observations(edge)
            
            if len(supporting_obs) >= 3:
                # Calculate new confidence based on support
                support_confidence = np.mean([obs["confidence"] for obs in supporting_obs])
                new_confidence = max(current_confidence, support_confidence * 0.9)
                
                # Attempt repair (only if confident enough)
                if new_confidence > SKG_ENGINE.repair_threshold:
                    SKG_ENGINE.self_repair_edge(
                        edge_id=edge_id,
                        new_confidence=new_confidence,
                        repair_reason=f"Supported by {len(supporting_obs)} observations"
                    )
                else:
                    # Log proposed repair for human review
                    self._log_proposed_repair(edge_id, new_confidence, len(supporting_obs))
            else:
                # Not enough support - flag for human review
                self._flag_for_review(edge_id, clutter_score)
    
    def _find_supporting_observations(self, edge: Dict) -> List[Dict]:
        """Find observations from same domain that support this edge"""
        source_obs = edge["source"]
        target_obs = edge["target"]
        
        # Get domain from source or target node
        source_domain = SKG_ENGINE.graph.nodes[source_obs].get("verdict", {}).get("domain", "")
        
        # Find other observations from same domain
        supporting = []
        for node_id, node_data in SKG_ENGINE.graph.nodes.items():
            if node_id in [source_obs, target_obs]:
                continue
                
            node_domain = node_data.get("verdict", {}).get("domain", "")
            if node_domain == source_domain:
                supporting.append(node_data)
        
        return supporting
    
    def _log_proposed_repair(self, edge_id: str, confidence: float, support_count: int):
        """Log repair proposal for human review"""
        proposal = {
            "edge_id": edge_id,
            "proposed_confidence": confidence,
            "support_count": support_count,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending_review"
        }
        
        proposals = []
        proposal_file = self.detector_root / "repair_proposals.yaml"
        if proposal_file.exists():
            with open(proposal_file, 'r') as f:
                proposals = yaml.safe_load(f) or []
        
        proposals.append(proposal)
        
        with open(proposal_file, 'w') as f:
            yaml.dump(proposals, f)
    
    def _flag_for_review(self, edge_id: str, clutter_score: float):
        """Flag edge as high-clutter, low-support (requires human)"""
        flag = {
            "edge_id": edge_id,
            "clutter_score": clutter_score,
            "reason": "Insufficient support for auto-repair",
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": "human_review"
        }
        
        self._log_detection(flag)
    
    def _log_detection(self, detection: Dict[str, Any]):
        """Immutable log of all clutter detections"""
        history = []
        if self.detection_log.exists():
            with open(self.detection_log, 'r') as f:
                history = yaml.safe_load(f) or []
        
        history.append(detection)
        
        # Keep last 50000 for analysis
        if len(history) > 50000:
            history = history[-50000:]
            
        with open(self.detection_log, 'w') as f:
            yaml.dump(history, f)


# Singleton edge detector
# Runs continuously in ORB observation loop
EDGE_DETECTOR = EdgeDetector()