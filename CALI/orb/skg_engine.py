#!/usr/bin/env python3
"""
SKG Engine - Super-Knowledge Graph Layer for ORB
Learns from immutable ontological matrix without modifying it.
Detects patterns, relationships, and clutter edges.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple
import json
import yaml
import networkx as nx
from dataclasses import dataclass
import hashlib

@dataclass
class SKGEdge:
    """Structured representation of relationship between observations"""
    source_obs_id: str
    target_obs_id: str
    edge_type: str  # "contradiction", "support", "temporal", "conceptual"
    confidence: float  # 0.0-1.0 (probability edge is real, not noise)
    detected_at: str
    repair_history: List[Dict]  # Immutable log of confidence adjustments

class SKGEngine:
    """
    Super-Knowledge Graph Engine
    - Reads immutable observations from OntologicalMatrix
    - Builds graph of relationships
    - Detects clutter: low-confidence edges, redundant observations
    - Self-repairs: adjusts edge weights based on new evidence
    - Never modifies original observations (only learns from them)
    """
    
    def __init__(self):
        self.skg_root = Path(__file__).resolve().parents[2] / "CALI" / "orb" / "skg"
        self.skg_root.mkdir(parents=True, exist_ok=True)
        
        # NetworkX graph representing relationships
        self.graph = nx.DiGraph()
        
        # Clutter detection thresholds (adapt over time)
        self.clutter_threshold = 0.3  # Edges below this are clutter candidates
        self.repair_threshold = 0.9   # Confidence needed to auto-repair
        
        # Persistence files
        self.graph_file = self.skg_root / "skg_graph.json"
        self.repair_log = self.skg_root / "repair_log.yaml"
        
        # Load existing graph if present
        self._load_graph()
        
    def _load_graph(self):
        """Load SKG graph from disk"""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, 'r') as f:
                    data = json.load(f)
                    if 'edges' in data and 'nodes' in data:
                        self.graph = nx.node_link_graph(data)
                    else:
                        print(f"[SKG] Graph file missing required keys, starting fresh")
                        self.graph = nx.DiGraph()
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[SKG] Error loading graph: {e}, starting fresh")
                self.graph = nx.DiGraph()
                
    def _save_graph(self):
        """Persist graph to disk"""
        data = nx.node_link_data(self.graph)
        with open(self.graph_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _log_repair(self, edge_id: str, action: str, reason: str, confidence: float):
        """Immutable log of all repairs"""
        log_entry = {
            "edge_id": edge_id,
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "graph_version": self._get_graph_version()
        }
        
        history = []
        if self.repair_log.exists():
            with open(self.repair_log, 'r') as f:
                history = yaml.safe_load(f) or []
        
        history.append(log_entry)
        
        # Keep last 10000 for forensic analysis
        if len(history) > 10000:
            history = history[-10000:]
            
        with open(self.repair_log, 'w') as f:
            yaml.dump(history, f)
            
    def _get_graph_version(self) -> str:
        """Deterministic version hash of current graph"""
        graph_data = nx.node_link_data(self.graph)
        graph_string = json.dumps(graph_data, sort_keys=True)
        return hashlib.sha256(graph_string.encode()).hexdigest()[:16]
    
    def ingest_from_matrix(self, matrix: 'OntologicalMatrix'):
        """
        Read latest observations from OntologicalMatrix (immutable source)
        Build SKG graph representing relationships
        """
        # Collect all observations from all cores
        all_observations = []
        for core in ["Caleon_Genesis", "Cali_X_One", "KayGee", "UCM_Core_ECM"]:
            observations = matrix.get_observations_by_core(core, limit=100)
            all_observations.extend(observations)
        
        # Add nodes for all observations
        for obs in all_observations:
            node_id = obs["id"]
            if not self.graph.has_node(node_id):
                self.graph.add_node(
                    node_id,
                    core_id=obs.get("core_id", "unknown"),
                    verdict=obs["verdict"],
                    timestamp=obs["timestamp"],
                    confidence=obs["verdict"].get("confidence", 0.5),
                    clutter_score=0.0  # Will be evaluated below
                )
        
        # Detect relationships between ALL observations
        for obs in all_observations:
            self._detect_relationships(obs, all_observations)
                
        self._save_graph()
        self._evaluate_clutter()
        
    def _detect_relationships(self, obs: Dict, all_obs: List[Dict]):
        """Detect edges (relationships) between observations"""
        obs_id = obs["id"]
        obs_verdict = obs["verdict"]
        
        for other in all_obs:
            if other["id"] == obs_id:
                continue
                
            other_verdict = other["verdict"]
            
            # Detect contradiction edge
            if self._is_contradiction(obs_verdict, other_verdict):
                edge_id = f"contradiction_{obs_id}_{other['id']}"
                self._add_edge(
                    edge_id=edge_id,
                    source=obs_id,
                    target=other["id"],
                    edge_type="contradiction",
                    confidence=self._calculate_contradiction_confidence(obs_verdict, other_verdict)
                )
            
            # Detect temporal edge
            if self._is_temporal_sequence(obs, other):
                edge_id = f"temporal_{obs_id}_{other['id']}"
                self._add_edge(
                    edge_id=edge_id,
                    source=obs_id,
                    target=other["id"],
                    edge_type="temporal",
                    confidence=0.8  # Temporal sequence is deterministic
                )
            
            # Detect conceptual similarity
            similarity = self._calculate_conceptual_similarity(obs_verdict, other_verdict)
            if similarity > 0.6:
                edge_id = f"conceptual_{obs_id}_{other['id']}"
                self._add_edge(
                    edge_id=edge_id,
                    source=obs_id,
                    target=other["id"],
                    edge_type="conceptual",
                    confidence=similarity
                )
    
    def _add_edge(self, edge_id: str, source: str, target: str, 
                  edge_type: str, confidence: float):
        """Add edge to graph with metadata"""
        self.graph.add_edge(
            source,
            target,
            id=edge_id,
            edge_type=edge_type,
            confidence=confidence,
            clutter_score=0.0,  # Will be evaluated
            repair_count=0
        )
    
    def _is_contradiction(self, a: Dict, b: Dict) -> bool:
        """Detect if two verdicts directly contradict"""
        rec_a = a.get("recommendation", a.get("verdict", ""))
        rec_b = b.get("recommendation", b.get("verdict", ""))
        
        contradictory = [("ACCEPT", "REJECT"), ("REJECT", "ACCEPT"), 
                        ("ACCEPT", "SUSPEND"), ("SUSPEND", "ACCEPT")]
        return (rec_a, rec_b) in contradictory or (rec_b, rec_a) in contradictory
    
    def _calculate_contradiction_confidence(self, a: Dict, b: Dict) -> float:
        """Calculate confidence that contradiction is real (not noise)"""
        conf_a = a.get("confidence", 0.5)
        conf_b = b.get("confidence", 0.5)
        
        # Both highly confident = real contradiction
        if conf_a > 0.8 and conf_b > 0.8:
            return 0.95
        
        # One uncertain = possible noise
        if abs(conf_a - conf_b) > 0.5:
            return 0.3
            
        return 0.6
    
    def _is_temporal_sequence(self, obs_a: Dict, obs_b: Dict) -> bool:
        """Detect if obs_b follows obs_a in time with conceptual progression"""
        time_a = datetime.fromisoformat(obs_a["timestamp"])
        time_b = datetime.fromisoformat(obs_b["timestamp"])
        
        # Within 10 seconds = possible sequence
        if 0 < (time_b - time_a).total_seconds() < 10:
            # Check if b references a's concepts
            concepts_a = set(str(obs_a["verdict"]).split())
            concepts_b = set(str(obs_b["verdict"]).split())
            
            return len(concepts_a & concepts_b) > 2
            
        return False
    
    def _calculate_conceptual_similarity(self, a: Dict, b: Dict) -> float:
        """Calculate semantic similarity (0.0-1.0)"""
        # Simple string-based similarity for now
        # Production: use embeddings (word2vec, BERT, etc.)
        text_a = str(a).lower()
        text_b = str(b).lower()
        
        words_a = set(text_a.split())
        words_b = set(text_b.split())
        
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _evaluate_clutter(self):
        """Identify edges with low confidence (clutter)"""
        for u, v, edge_data in self.graph.edges(data=True):
            confidence = edge_data['confidence']
            
            # Calculate clutter score
            clutter_score = max(0.0, self.clutter_threshold - confidence)
            
            # Update edge metadata
            self.graph.edges[u, v]['clutter_score'] = clutter_score
            
            # Flag nodes connected to high-clutter edges
            if clutter_score > 0.5:
                # Mark nodes as potentially corrupt
                self.graph.nodes[u]['clutter_score'] = max(
                    self.graph.nodes[u].get('clutter_score', 0.0),
                    clutter_score
                )
                self.graph.nodes[v]['clutter_score'] = max(
                    self.graph.nodes[v].get('clutter_score', 0.0),
                    clutter_score
                )
    
    def detect_clutter_edges(self) -> List[Dict[str, Any]]:
        """Return list of edges identified as clutter (confidence < threshold)"""
        clutter = []
        for u, v, data in self.graph.edges(data=True):
            if data['confidence'] < self.clutter_threshold:
                clutter.append({
                    "edge_id": data['id'],
                    "source": u,
                    "target": v,
                    "confidence": data['confidence'],
                    "type": data['edge_type'],
                    "clutter_score": data['clutter_score']
                })
        
        # Debug: print some edge confidences
        print(f"[DEBUG] Total edges: {len(self.graph.edges)}")
        if self.graph.number_of_edges() > 0:
            print(f"[DEBUG] Sample edge confidences:")
            count = 0
            for u, v, data in self.graph.edges(data=True):
                if count < 5:
                    print(f"  {data['id']}: {data['confidence']:.3f} (type: {data['edge_type']})")
                    count += 1
        
        return clutter
    
    def self_repair_edge(self, edge_id: str, new_confidence: float, 
                        repair_reason: str) -> bool:
        """
        Self-repair an edge by adjusting confidence.
        Repair only if new_confidence > repair_threshold (0.9)
        Immutable repair log is created.
        
        Returns: True if repaired, False if insufficient confidence
        """
        if new_confidence < self.repair_threshold:
            # Not confident enough to repair - requires human review
            self._log_repair(edge_id, "proposed", 
                           f"Insufficient confidence: {new_confidence}", 0.0)
            return False
        
        if edge_id not in self.graph.edges:
            return False
        
        # Update edge confidence (graph is mutable, matrix is immutable)
        source, target = next((u, v) for u, v, d in self.graph.edges(data=True) 
                             if d['id'] == edge_id)
        old_confidence = self.graph.edges[source, target]['confidence']
        
        self.graph.edges[source, target]['confidence'] = new_confidence
        self.graph.edges[source, target]['repair_count'] += 1
        
        # Log the repair (immutable)
        self._log_repair(edge_id, "executed", repair_reason, new_confidence)
        
        print(f"[SKG REPAIR] Edge {edge_id}: {old_confidence:.2f} → {new_confidence:.2f}")
        print(f"             Reason: {repair_reason}")
        
        return True
    
    def adapt_thresholds(self):
        """
        Adapt clutter/repair thresholds based on repair success rates.
        Called periodically (e.g., daily).
        """
        if not self.repair_log.exists():
            return
            
        with open(self.repair_log, 'r') as f:
            repairs = yaml.safe_load(f) or []
        
        # Calculate repair success rate
        executed_repairs = [r for r in repairs if r['action'] == "executed"]
        if len(executed_repairs) < 10:
            return  # Need more data
        
        # If most repairs stabilized confidence > 0.95, we can be more aggressive
        successful_repairs = [r for r in executed_repairs 
                            if r['confidence'] > 0.95]
        success_rate = len(successful_repairs) / len(executed_repairs)
        
        # Adapt threshold
        if success_rate > 0.8:
            self.repair_threshold = max(0.8, self.repair_threshold - 0.02)
        elif success_rate < 0.5:
            self.repair_threshold = min(0.95, self.repair_threshold + 0.02)
        
        print(f"[SKG ADAPT] Repair threshold adjusted to {self.repair_threshold:.2f}")


# Singleton SKG engine
# SKG is interpretive layer, not replacement for matrix
SKG_ENGINE = SKGEngine()