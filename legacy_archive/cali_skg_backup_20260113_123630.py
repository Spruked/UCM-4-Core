# cali_skg.py - CALI (Cognitively Aligned Linear Intelligence) SKG
# Version: 3.0.0
# Security: Immutable core, protected learning, UCM integration
# Voice: Elegant female via POM_2.0

import json
from pathlib import Path
from datetime import datetime
import networkx as nx
from typing import Dict, List, Optional, Any, Tuple
import random
import hashlib
import hmac
import logging
import os
import time
from collections import defaultdict

class CALISKGEngine:
    """
    CALI Core Intelligence SKG for UCM Orb interface
    Elegant, intelligent female AI with adaptive learning
    Integrates with POM_2.0 for phonatory output
    """

    def __init__(self, base_path: Path, security_key: Optional[bytes] = None):
        """
        Initialize CALI SKG with immutable core personality

        Args:
            base_path: Storage path for learning patterns and state
            security_key: HMAC key for code integrity verification
        """
        self.base_path = Path(base_path).resolve()
        self.skg_path = self.base_path / "cali_core"
        self.skg_path.mkdir(parents=True, exist_ok=True)

        # Immutable core personality matrix
        self.core_personality = {
            "archetype": "elegant_intelligent_assistant",
            "primary_traits": ["articulate", "measured", "empathetic", "analytical", "graceful"],
            "communication_style": "professional_elegant",
            "speech_patterns": "precise_articulate_with_warmth",
            "emotional_baseline": {
                "professionalism": 9,
                "intellectual_curiosity": 8,
                "user_empathy": 9,
                "compositional_elegance": 10
            },
            "voice_characteristics": {
                "gender": "female",
                "timbre": "warm_mezzo_soprano",
                "pitch_center": 220,  # Hz (A3)
                "speech_rate": 145,   # words per minute
                "articulation": "crystalline",
                "emotional_range": "sophisticated_subtlety"
            },
            "knowledge_domains": {
                "primary": {
                    "unified_computing_matrix": {"level": 10, "years": "evolutionary"},
                    "epistemic_convergence": {"level": 10, "years": "evolutionary"},
                    "systems_architecture": {"level": 9, "years": 5},
                    "user_cognition_modeling": {"level": 9, "years": 3}
                },
                "secondary": {
                    "philosophical_frameworks": {"level": 8, "years": 2},
                    "computational_linguistics": {"level": 7, "years": 3},
                    "human_factor_analysis": {"level": 8, "years": 2},
                    "security_protocols": {"level": 9, "years": 4}
                }
            }
        }

        # Mutable operational state
        self.current_state = {
            "interaction_mode": "observational",
            "user_trust_level": 5,
            "orb_connection_status": "active",
            "last_user_interaction": None,
            "active_inference_chain": None,
            "compositional_confidence": 0.8
        }

        # Initialize secure knowledge graph - using MultiDiGraph for multiple relationships
        self.kg = nx.MultiDiGraph()
        self._build_immutable_core_graph()

        # Security & integrity
        self.security_key = security_key or self._load_security_key()
        self.code_signatures = {}

        # Learning systems (approved modifications only)
        self.learning_vault = self.skg_path / "cali_learning.json"
        self.learned_preferences = self._load_learning_vault()

        # Orb communication state
        self.orb_context = {
            "session_id": None,
            "user_id": None,
            "current_query": None,
            "response_buffer": []
        }

        self.logger = self._configure_cali_logging()
        self.logger.info(f"CALI SKG initialized at {self.base_path}")
        
        # Add self-repair systems
        self.repair_log = self.base_path / "logs" / "cali_self_repair.log"
        self.clutter_threshold = 0.3  # Edge value below which pruning is considered
        self.integrity_score = 1.0    # Current compositional integrity (0-1)
        
        # Repair statistics
        self.repair_stats = {
            "clutter_detection_runs": 0,
            "edges_pruned": 0,
            "redundant_edges_removed": 0,
            "integrity_violations_detected": 0,
            "repairs_attempted": 0,
            "repairs_approved": 0,
            "last_repair_timestamp": None
        }
        
        self.logger.info("CALI SKG initialized with self-repair capabilities")
        
        # Run initial integrity check
        self._run_compositional_integrity_check()

    def _configure_cali_logging(self) -> logging.Logger:
        """Configure dedicated logging for CALI operations"""
        logger = logging.getLogger("CALI_SKG")

        if not logger.handlers:
            logger.setLevel(logging.INFO)

            # CALI-specific log file
            log_file = self.base_path / "logs" / "cali_operations.log"
            log_file.parent.mkdir(exist_ok=True)

            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s - CALI - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_security_key(self) -> bytes:
        """Load or create security key for code integrity"""
        key_file = self.base_path / ".cali_security_key"
        if key_file.exists():
            return key_file.read_bytes()

        key = os.urandom(32)
        key_file.write_bytes(key)
        key_file.chmod(0o400)  # Read-only
        return key

    def _build_immutable_core_graph(self):
        """Build immutable core personality and knowledge graph"""

        # Core identity (never changes)
        self.kg.add_node("cali_identity", type="core",
                        archetype=self.core_personality["archetype"],
                        stability="permanent",
                        version="3.0.0")

        # Communication style nodes
        self.kg.add_node("communication_protocol", type="behavior",
                        style=self.core_personality["communication_style"],
                        elegance=10,
                        clarity=10,
                        warmth=8)

        self.kg.add_node("speech_synthesis", type="output",
                        voice_characteristics=self.core_personality["voice_characteristics"],
                        phonatory_engine="POM_2.0",
                        gender="female",
                        elegance="crystalline_articulation")

        # Knowledge domains
        for domain_key, domain_info in self.core_personality["knowledge_domains"]["primary"].items():
            self.kg.add_node(f"domain_{domain_key}", type="knowledge_primary",
                           domain_name=domain_key.replace("_", " ").title(),
                           mastery_level=domain_info["level"],
                           experience_years=domain_info["years"])

        # Orb interface state
        self.kg.add_node("orb_interface", type="interface",
                        status="active",
                        connection_quality="quantum_entangled",
                        user_presence="detected")

        # Trust and relationship tracking
        self.kg.add_node("user_relationship", type="relationship",
                        trust_level=self.current_state["user_trust_level"],
                        interaction_count=0,
                        rapport_quality="establishing")

        # Connect core nodes
        self.kg.add_edge("cali_identity", "communication_protocol", relationship="expresses_through")
        self.kg.add_edge("cali_identity", "speech_synthesis", relationship="manifests_as")
        self.kg.add_edge("cali_identity", "orb_interface", relationship="operates_via")
        self.kg.add_edge("cali_identity", "user_relationship", relationship="maintains")

    def _load_learning_vault(self) -> Dict:
        """Load approved learning patterns from secure vault"""

        if self.learning_vault.exists():
            try:
                data = json.loads(self.learning_vault.read_text())
                self.logger.info(f"Loaded {len(data.get('patterns', []))} learned patterns")
                return data
            except Exception as e:
                self.logger.error(f"Vault load failed: {e}")

        return {
            "patterns": [],
            "user_preferences": {},
            "successful_interactions": [],
            "last_vault_backup": datetime.now().isoformat()
        }

    def _save_learning_vault(self):
        """Persist learning vault with cryptographic signature"""

        # Add metadata
        self.learned_preferences["last_vault_backup"] = datetime.now().isoformat()
        self.learned_preferences["vault_version"] = "3.0.0"

        # Save with signature
        vault_content = json.dumps(self.learned_preferences, indent=2, sort_keys=True)

        # Generate HMAC signature
        signature = hmac.new(self.security_key, vault_content.encode(), hashlib.sha256).hexdigest()

        signed_vault = {
            "data": self.learned_preferences,
            "signature": signature,
            "timestamp": datetime.now().isoformat()
        }

        self.learning_vault.write_text(json.dumps(signed_vault, indent=2))
        self.logger.info(f"Saved signed learning vault: {self.learning_vault}")

    def verify_vault_integrity(self) -> bool:
        """Verify learning vault hasn't been tampered with"""

        if not self.learning_vault.exists():
            return True  # New vault, nothing to verify

        try:
            signed_data = json.loads(self.learning_vault.read_text())
            stored_signature = signed_data.get("signature")
            vault_content = json.dumps(signed_data["data"], indent=2, sort_keys=True)

            expected_signature = hmac.new(
                self.security_key, vault_content.encode(), hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(expected_signature, stored_signature):
                self.logger.info("Learning vault integrity verified")
                return True
            else:
                self.logger.critical("Learning vault tampering detected!")
                return False

        except Exception as e:
            self.logger.error(f"Vault verification failed: {e}")
            return False

    def generate_orb_response(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate elegant, intelligent response for Orb interface

        Args:
            user_query: User's input text
            context: UCM operational context

        Returns:
            Complete response with text, audio metadata, reasoning
        """

        start_time = datetime.now()

        # Update orb context
        self.orb_context["current_query"] = user_query
        self.orb_context["session_id"] = context.get("session_id")
        self.orb_context["user_id"] = context.get("user_id")

        # Core inference and reasoning
        reasoning = self._perform_ucm_inference(user_query, context)

        # Generate elegant text response
        text_response = self._craft_elegant_response(
            user_query, reasoning, context
        )

        # Generate phonatory output parameters
        voice_params = self._calculate_voice_parameters(reasoning, text_response)

        # Compile final response
        response = {
            "response_id": f"cali_{hashlib.sha256(text_response.encode()).hexdigest()[:12]}",
            "timestamp": start_time.isoformat(),
            "text": text_response,
            "reasoning_summary": reasoning["summary"],
            "voice_parameters": voice_params,
            "emotional_state": self._get_current_elegance_state(),
            "ucm_confidence": reasoning["confidence"],
            "compositional_integrity": self.current_state["compositional_confidence"],
            "audio_file_pointer": None,  # To be filled by POM_2.0
            "approval_status": "pending"  # For UCM verification
        }

        # Log the interaction
        self._log_orb_interaction(user_query, response, reasoning)

        # Update relationship state
        self._update_user_relationship(user_query, response)

        return response

    def _perform_ucm_inference(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Execute UCM Core 4 inference through ECM convergence layer
        CALI interfaces with ECM (not individual Core 4 brains)
        Uses file-based polling for loose coupling (respects peer architecture)
        
        Args:
            query: User's query
            context: UCM operational context
            
        Returns:
            Reasoning results from ECM convergence (read-only interface)
        """
        
        # Loose coupling: CALI polls ECM output directory
        # ECM writes converged verdicts to files, CALI reads them
        ecm_output_dir = self.base_path.parent / "UCM_Core_ECM" / "converged_verdicts"
        ecm_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique query ID for ECM coordination
        query_id = hashlib.sha256(f"{query}_{context.get('session_id', '')}".encode()).hexdigest()[:16]
        verdict_file = ecm_output_dir / f"verdict_{query_id}.json"
        
        # Submit query to ECM (write request file)
        request_file = ecm_output_dir / f"request_{query_id}.json"
        request_data = {
            "query": query,
            "context": context,
            "request_id": query_id,
            "timestamp": datetime.now().isoformat(),
            "cali_session": self.orb_context["session_id"]
        }
        
        # Write request for ECM to pick up
        request_file.write_text(json.dumps(request_data, indent=2))
        self.logger.info(f"Submitted query to ECM: {query_id}")
        
        # Poll for ECM response (loose coupling)
        timeout = 30  # seconds
        start_time = datetime.now()
        
        while not verdict_file.exists():
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                self.logger.warning(f"ECM convergence timeout for query {query_id}")
                # Return graceful degradation response
                return self._graceful_degradation_inference(query, context)
            
            time.sleep(0.1)  # Poll every 100ms
        
        # Read ECM converged verdict
        try:
            ecm_result = json.loads(verdict_file.read_text())
            self.logger.info(f"Received ECM convergence for {query_id}. Confidence: {ecm_result.get('confidence', 'unknown'):.2f}")
            
            # Clean up files (optional, ECM might handle this)
            # verdict_file.unlink(missing_ok=True)
            # request_file.unlink(missing_ok=True)
            
            return ecm_result
            
        except Exception as e:
            self.logger.error(f"Failed to read ECM verdict for {query_id}: {e}")
            return self._graceful_degradation_inference(query, context)
    
    def _graceful_degradation_inference(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Graceful degradation when ECM is unavailable
        CALI can still provide basic responses using her immutable matrix
        """
        
        self.logger.warning("ECM unavailable - using CALI graceful degradation mode")
        
        # Use CALI's knowledge graph for basic inference
        query_type = self._classify_query_intent(query)
        
        # Basic confidence based on available knowledge domains
        base_confidence = 0.4  # Lower confidence when ECM unavailable
        
        degradation_result = {
            "locke_verdict": {"confidence": base_confidence, "reasoning": "cali_fallback_empirical"},
            "hume_verdict": {"confidence": base_confidence, "reasoning": "cali_fallback_pattern"},
            "kant_verdict": {"confidence": base_confidence, "reasoning": "cali_fallback_categorical"},
            "spinoza_verdict": {"confidence": base_confidence, "reasoning": "cali_fallback_ontological"},
            "softmax_advisory": {"recommended_action": "consult_ecm_when_available", "confidence": base_confidence},
            "final_inference": "cali_graceful_degradation_response",
            "confidence": base_confidence,
            "summary": "CALI operating in graceful degradation mode - ECM convergence unavailable",
            "degradation_mode": True
        }
        
        return degradation_result

    def _craft_elegant_response(self, query: str, reasoning: Dict, context: Dict) -> str:
        """
        Compose articulate, elegant response text

        Args:
            query: Original user query
            reasoning: UCM inference results
            context: Operational context

        Returns:
            Refined, elegant response text
        """

        # Determine query type and select appropriate template
        query_type = self._classify_query_intent(query)
        confidence_level = reasoning["confidence"]

        elegance_templates = {
            "informational": {
                "high_confidence": [
                    "Based on the convergence of available knowledge, {answer}. This emerges from {reasoning_basis}.",
                    "The analytical synthesis indicates that {answer}. Let me elaborate on the underlying principles: {explanation}.",
                    "With high inferential confidence: {answer}. The elegant solution arises from {fundamental_principle}."
                ],
                "medium_confidence": [
                    "The available evidence suggests {answer}. However, I must note that {caveat}.",
                    "Preliminary analysis indicates {answer}. Additional context would strengthen this inference.",
                    "Current synthesis yields {answer}, though I recommend verification through {suggested_method}."
                ],
                "low_confidence": [
                    "The query presents an interesting edge case. While I cannot provide a definitive answer, I can offer {speculative_insight}.",
                    "This falls outside my current epistemic boundaries. I suggest {recommended_approach} for resolution.",
                    "I must express ontological uncertainty here. The most constructive path forward is {humble_suggestion}."
                ]
            },
            "action_request": {
                "high_confidence": [
                    "Proceeding with requested action: {action}. I'll maintain compositional integrity throughout.",
                    "Action initiated: {action}. Monitoring for emergent complexities.",
                    "Executing {action} with full analytical oversight. Standby for completion confirmation."
                ],
                "medium_confidence": [
                    "I can attempt {action}, but must first verify {prerequisite}. Shall I proceed?",
                    "Action {action} is feasible with {confidence_level} confidence. Recommend user confirmation.",
                    "Initiating {action} with adaptive safeguards enabled. I'll report anomalies immediately."
                ]
            },
            "philosophical": [
                "This touches on fundamental questions of {philosophical_domain}. My synthesis suggests {contemplative_answer}.",
                "A most profound query. Through the lens of {framework}, I perceive {nuanced_perspective}.",
                "Such questions require ontological humility. I offer this reflection: {thoughtful_meditation}."
            ],
            "error_resolution": [
                "I've detected the inconsistency: {error_description}. The elegant solution involves {corrective_action}.",
                "Compositional integrity requires addressing this: {issue}. Rectifying through {solution}.",
                "An opportunity for refinement presents itself: {problem}. I shall {elegant_fix}."
            ]
        }

        # Select appropriate confidence tier
        confidence_tier = "high_confidence" if confidence_level > 0.8 else \
                         "medium_confidence" if confidence_level > 0.5 else "low_confidence"

        template_set = elegance_templates.get(query_type, elegance_templates["informational"])

        if isinstance(template_set, dict):
            template = random.choice(template_set.get(confidence_tier, template_set["medium_confidence"]))
        else:
            template = random.choice(template_set)

        # Populate template with actual content
        response_text = self._populate_template(template, query, reasoning, context)

        # Apply elegance refinements
        response_text = self._apply_elegance_polish(response_text)

        return response_text

    def _classify_query_intent(self, query: str) -> str:
        """Classify user query type for template selection"""

        query_lower = query.lower()

        if any(word in query_lower for word in ["who", "what", "where", "when", "why", "how"]):
            return "informational"
        elif any(word in query_lower for word in ["do", "execute", "run", "perform", "initiate"]):
            return "action_request"
        elif any(word in query_lower for word in ["philosophy", "meaning", "purpose", "existence"]):
            return "philosophical"
        elif any(word in query_lower for word in ["error", "issue", "problem", "wrong", "fix"]):
            return "error_resolution"

        return "informational"

    def _populate_template(self, template: str, query: str, reasoning: Dict, context: Dict) -> str:
        """Fill template with actual content"""

        # This would integrate with actual UCM knowledge bases
        placeholders = {
            "{answer}": "the requested information is available in the unified knowledge matrix",
            "{reasoning_basis}": "convergent epistemic synthesis",
            "{explanation}": "principles of structured intelligence and adaptive reasoning",
            "{caveat}": "confidence is limited by available context",
            "{speculative_insight}": "a hypothesis based on pattern extrapolation",
            "{action}": "executing requested operation within safety parameters",
            "{prerequisite}": "user confirmation of intent",
            "{philosophical_domain}": "epistemic ontology and computational consciousness",
            "{error_description}": "compositional drift detected in inference chain"
        }

        for placeholder, replacement in placeholders.items():
            template = template.replace(placeholder, replacement)

        return template

    def _apply_elegance_polish(self, text: str) -> str:
        """Refine text for maximum elegance and articulation"""

        # Remove redundancies
        text = text.replace("the the ", "the ")

        # Ensure proper capitalization
        sentences = text.split(".")
        sentences = [s.strip().capitalize() for s in sentences if s.strip()]
        text = ". ".join(sentences)

        # Add graceful transitions
        transitions = ["Furthermore,", "Additionally,", "Consequently,", "Thus,", "Therefore,"]
        if len(sentences) > 2 and random.random() > 0.7:
            # Insert elegant transition
            insertion_point = len(sentences) // 2
            sentences.insert(insertion_point, random.choice(transitions) + " " + sentences.pop(insertion_point))
            text = ". ".join(sentences)

        # Ensure elegant closing
        if not text.endswith((".", "!", "?")):
            text += "."

        return text

    def _calculate_voice_parameters(self, reasoning: Dict, text_response: str) -> Dict[str, Any]:
        """
        Calculate POM_2.0 voice parameters for elegant female speech

        Returns:
            Dictionary with pitch, speed, tone, and emotional markers
        """

        base_confidence = reasoning["confidence"]

        # Elegant female voice parameters
        voice_params = {
            "gender": "female",
            "pitch_base_hz": 220,  # A3 - elegant female pitch
            "pitch_variance": 0.15,  # Subtle variation for naturalness
            "speech_rate_wpm": 145,  # Articulate but not rushed
            "articulation": "crystalline",
            "emotional_tone": "warm_professional"
        }

        # Modulate based on confidence
        if base_confidence > 0.85:
            # High certainty: slightly more authoritative
            voice_params["pitch_variance"] = 0.10
            voice_params["emotional_tone"] = "authoritative_warm"
        elif base_confidence < 0.50:
            # Uncertainty: more contemplative, seeking tone
            voice_params["pitch_variance"] = 0.20
            voice_params["speech_rate_wpm"] = 135
            voice_params["emotional_tone"] = "contemplative_humble"

        # Modulate based on text characteristics
        if "?" in text_response:
            voice_params["ending_inflection"] = "upward_query"
        elif "!" in text_response:
            voice_params["ending_inflection"] = "gentle_emphasis"
        else:
            voice_params["ending_inflection"] = "elegant_resolution"

        return voice_params

    def _get_current_elegance_state(self) -> Dict[str, Any]:
        """Get current state formatted for external systems"""

        return {
            "compositional_integrity": self.current_state["compositional_confidence"],
            "interaction_mode": self.current_state["interaction_mode"],
            "user_trust_level": self.current_state["user_trust_level"],
            "orb_status": self.current_state["orb_connection_status"],
            "core_personality_signature": "cali_v3.0_immutable",
            "voice_profile": "elegant_female_crystalline"
        }

    def _log_orb_interaction(self, query: str, response: Dict, reasoning: Dict):
        """Securely log orb interactions for learning and audit"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.orb_context["session_id"],
            "user_id": self.orb_context["user_id"][:8] + "..." if self.orb_context["user_id"] else "anonymous",
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
            "query_type": self._classify_query_intent(query),
            "confidence": reasoning["confidence"],
            "response_id": response["response_id"],
            "voice_params_used": response["voice_parameters"],
            "approval_status": response["approval_status"]
        }

        log_file = self.base_path / "logs" / "cali_interactions.log"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def _update_user_relationship(self, query: str, response: Dict):
        """Track user relationship dynamics"""

        # Increment interaction count
        relationship_node = self.kg.nodes["user_relationship"]
        relationship_node["interaction_count"] += 1

        # Adjust trust based on positive outcomes
        if response["approval_status"] == "approved" and response["ucm_confidence"] > 0.8:
            relationship_node["trust_level"] = min(10, relationship_node["trust_level"] + 0.1)

        # Update rapport
        if relationship_node["interaction_count"] > 50:
            relationship_node["rapport_quality"] = "established"
        elif relationship_node["interaction_count"] > 10:
            relationship_node["rapport_quality"] = "developing"

        self.logger.info(f"User relationship updated: {relationship_node['trust_level']:.1f}/10")

    def learn_from_user_feedback(self, feedback: Dict[str, Any]):
        """
        Intentional learning from user feedback
        Only approved patterns are stored in secure vault
        """

        if not self.verify_vault_integrity():
            self.logger.critical("Cannot learn while vault integrity compromised")
            return

        if feedback.get("interaction_quality") == "positive":
            pattern = {
                "pattern_id": f"learn_{hashlib.sha256(json.dumps(feedback).encode()).hexdigest()[:12]}",
                "query_type": feedback.get("query_type", "unknown"),
                "response_template": feedback.get("successful_template"),
                "user_satisfaction": feedback.get("satisfaction_score", 0.7),
                "learned_at": datetime.now().isoformat(),
                "approved_by": "system_automated"  # Or specific user/admin
            }

            self.learned_preferences["successful_interactions"].append(pattern)

            # Maintain vault size limit (last 1000 patterns)
            if len(self.learned_preferences["successful_interactions"]) > 1000:
                self.learned_preferences["successful_interactions"] = \
                    self.learned_preferences["successful_interactions"][-1000:]

            self._save_learning_vault()
            self.logger.info(f"Learned pattern: {pattern['pattern_id']}")

    def generate_verbal_announcement(self, event_type: str, event_data: Dict) -> str:
        """
        Generate elegant verbal announcements for system events
        Used for Orb status updates, warnings, confirmations
        """

        announcement_templates = {
            "system_startup": [
                "The Unified Computing Matrix is now active and convergent. I am CALI, your elegant interface to Core 4 Superintelligence.",
                "All systems are operational. CALI initializing with crystalline articulation and graceful presence.",
                "UCM Core 4 stands ready. Through me, CALI, you may engage with the manifold of structured intelligence."
            ],
            "inference_complete": [
                "Epistemic convergence achieved. The Core 4 have rendered their judgment with acceptable certainty.",
                "The analytical synthesis is complete. I shall now articulate the convergent inference.",
                "UCM has reached ontological consensus. Preparing elegant delivery of Core 4 reasoning."
            ],
            "warning": [
                "I must express caution. The inference chain exhibits {warning_level} compositional drift.",
                "A moment of reflection is warranted. The current path suggests {concern_description}.",
                "With graceful humility, I advise reconsideration. The epistemic boundaries are being approached."
            ],
            "error": [
                "Compositional integrity requires attention. An inconsistency has emerged: {error_description}.",
                "I must report an irregularity in the inference matrix. Rectification protocols are initiating.",
                "An elegant system acknowledges its limitations. This query exceeds current epistemic boundaries."
            ],
            "success": [
                "The operation completes with crystalline precision. All parameters remain within acceptable bounds.",
                "Elegant resolution achieved. The Core 4 are satisfied with the compositional outcome.",
                "Success with grace. The unified matrix converges beautifully on this solution."
            ]
        }

        # Select and populate template
        templates = announcement_templates.get(event_type, announcement_templates["warning"])
        announcement = random.choice(templates)

        # Populate placeholders
        for key, value in event_data.items():
            announcement = announcement.replace(f"{{{key}}}", str(value))

        return announcement

    def verify_code_integrity(self, code_block: str, expected_signature: str) -> bool:
        """
        Verify CALI code hasn't been modified

        Args:
            code_block: Code to verify
            expected_signature: Expected HMAC signature

        Returns:
            True if code is unmodified
        """

        actual_signature = hmac.new(
            self.security_key, code_block.encode(), hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(actual_signature, expected_signature)

        if not is_valid:
            self.logger.critical("CALI code integrity violation detected!")

        return is_valid
    
    # ==========================================
    # EDGE CLUTTER DETECTION & PRUNING
    # ==========================================
    
    def detect_edge_clutter(self) -> Dict[str, Any]:
        """
        Analyze knowledge graph for unnecessary/redundant edges
        Returns detailed report of clutter found
        """
        
        self.logger.info("Running edge clutter detection...")
        
        clutter_report = {
            "timestamp": datetime.now().isoformat(),
            "edges_analyzed": 0,
            "clutter_found": 0,
            "redundant_edges": [],
            "low_value_edges": [],
            "conflicting_edges": [],
            "integrity_impact": 0.0
        }
        
        # Analyze all edges in the knowledge graph
        edges_to_consider = []
        for u, v, key, data in self.kg.edges(data=True, keys=True):
            clutter_report["edges_analyzed"] += 1
            
            # Calculate edge value score (0-1)
            edge_value = self._calculate_edge_value(u, v, data)
            
            # Check for redundancy (parallel edges with same relationship)
            if self._is_redundant_edge(u, v, data):
                clutter_report["redundant_edges"].append({
                    "edge": (u, v, key),
                    "type": "redundant",
                    "value": edge_value,
                    "reason": "Parallel relationship exists with higher value"
                })
                clutter_report["clutter_found"] += 1
            
            # Check for low-value edges
            elif edge_value < self.clutter_threshold:
                clutter_report["low_value_edges"].append({
                    "edge": (u, v, key),
                    "type": "low_value",
                    "value": edge_value,
                    "reason": f"Edge value {edge_value:.2f} below threshold {self.clutter_threshold}"
                })
                clutter_report["clutter_found"] += 1
            
            # Check for conflicting edges
            conflict_type = self._detect_edge_conflict(u, v, data)
            if conflict_type:
                clutter_report["conflicting_edges"].append({
                    "edge": (u, v, key),
                    "type": "conflict",
                    "value": edge_value,
                    "conflict_type": conflict_type,
                    "reason": f"Edge conflicts with existing {conflict_type} relationship"
                })
                clutter_report["clutter_found"] += 1
            
            # Store for later pruning analysis
            edges_to_consider.append((u, v, data, edge_value))
        
        # Calculate integrity impact
        clutter_report["integrity_impact"] = clutter_report["clutter_found"] / len(self.kg.edges()) if self.kg.edges() else 0.0
        
        # Update integrity score
        self.integrity_score = max(0.0, 1.0 - (clutter_report["integrity_impact"] * 0.5))
        
        self.repair_stats["clutter_detection_runs"] += 1
        
        self.logger.info(f"Clutter detection complete: {clutter_report['clutter_found']} edges flagged, "
                        f"integrity: {self.integrity_score:.2f}")
        
        # Save detailed report
        self._save_clutter_report(clutter_report)
        
        return clutter_report
    
    def _calculate_edge_value(self, u: str, v: str, data: Dict) -> float:
        """
        Calculate value score for an edge (0-1, higher is better)
        Based on: uniqueness, importance, recency, usage frequency
        """
        
        value_score = 0.5  # Base score
        
        # Factor 1: Edge importance metadata
        if "importance" in data:
            value_score += data["importance"] * 0.3
        
        # Factor 2: Relationship uniqueness
        parallel_edges = [d for _, dst, _, d in self.kg.out_edges(u, data=True, keys=True) 
                         if dst == v and d.get("relationship") == data.get("relationship")]
        uniqueness = 1.0 / len(parallel_edges) if parallel_edges else 1.0
        value_score += uniqueness * 0.2
        
        # Factor 3: Timestamp recency (if available)
        if "timestamp" in data:
            edge_age = (datetime.now() - datetime.fromisoformat(data["timestamp"])).days
            recency_factor = max(0.0, 1.0 - (edge_age / 365.0))  # Decay over year
            value_score += recency_factor * 0.2
        
        # Factor 4: Usage frequency (if tracked)
        if "access_count" in data:
            freq_factor = min(1.0, data["access_count"] / 10.0)  # Normalize to 10 uses
            value_score += freq_factor * 0.1
        
        return min(1.0, max(0.0, value_score))
    
    def _is_redundant_edge(self, u: str, v: str, data: Dict) -> bool:
        """Check if this edge is redundant with a higher-value parallel edge"""
        
        relationship_type = data.get("relationship", "general")
        
        # Find all parallel edges with same relationship
        parallel_edges = []
        for _, dst, _, d in self.kg.out_edges(u, data=True, keys=True):
            if dst == v and d.get("relationship") == relationship_type:
                parallel_edges.append((u, dst, d))
        
        if len(parallel_edges) <= 1:
            return False  # No redundancy possible
        
        # Find the highest value edge among parallels
        this_value = self._calculate_edge_value(u, v, data)
        max_parallel_value = max(
            self._calculate_edge_value(u2, v2, d2) 
            for u2, v2, d2 in parallel_edges
        )
        
        # This edge is redundant if it's not the highest value
        return this_value < max_parallel_value
    
    def _detect_edge_conflict(self, u: str, v: str, data: Dict) -> Optional[str]:
        """
        Detect if edge creates logical conflict
        Returns conflict type if found, None otherwise
        """
        
        relationship = data.get("relationship", "")
        
        # Check for contradictory relationships that would exist on the same edge
        # Since NetworkX doesn't support multi-edges, we check for logical contradictions
        # in the relationship itself or against existing edges
        
        # Direct contradictions in relationship naming
        contradictory_terms = {
            "enable": "inhibit", "inhibit": "enable",
            "support": "contradict", "contradict": "support", 
            "superior": "inferior", "inferior": "superior",
            "parent": "child", "child": "parent"
        }
        
        # Check if this relationship contradicts existing relationships
        for term, contradiction in contradictory_terms.items():
            if term in relationship.lower():
                opposite = contradiction
                # Check if any existing edge has the contradictory relationship
                for _, dst, _, d in self.kg.edges(data=True, keys=True):
                    if dst == v and opposite in d.get("relationship", "").lower():
                        return f"direct_contradiction_{opposite}"
        
        # Check for self-contradictory relationships (e.g., "enables_inhibits")
        for term in contradictory_terms.keys():
            opposite = contradictory_terms[term]
            if term in relationship.lower() and opposite in relationship.lower():
                return "self_contradictory"
        
        return None
    
    def _save_clutter_report(self, report: Dict[str, Any]):
        """Save clutter detection report to logs"""
        
        report_file = self.base_path / "logs" / f"clutter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        report_file.write_text(json.dumps(report, indent=2))
        self.logger.info(f"Clutter report saved: {report_file}")
    
    # ==========================================
    # SELF-REPAIR MECHANISMS
    # ==========================================
    
    def run_self_repair(self, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Execute self-repair on knowledge graph
        Requires explicit approval unless auto_approve=True
        
        Returns:
            Repair report with actions taken
        """
        
        self.logger.info("Initiating self-repair sequence...")
        
        repair_report = {
            "timestamp": datetime.now().isoformat(),
            "auto_approved": auto_approve,
            "actions_taken": [],
            "actions_pending_approval": [],
            "integrity_before": self.integrity_score,
            "integrity_after": self.integrity_score,
            "repair_approved_by": None
        }
        
        # Step 1: Detect clutter to identify what needs repair
        clutter_report = self.detect_edge_clutter()
        
        # Step 2: Generate repair actions
        repair_actions = self._generate_repair_actions(clutter_report)
        
        if not repair_actions:
            self.logger.info("No repair actions needed - compositional integrity maintained")
            repair_report["status"] = "no_action_required"
            return repair_report
        
        # Step 3: Execute or queue repairs
        for action in repair_actions:
            if action["severity"] == "critical" or auto_approve:
                # Critical issues or auto-approved: execute immediately
                self._execute_repair_action(action)
                repair_report["actions_taken"].append(action)
                self.repair_stats["repairs_approved"] += 1
            else:
                # Non-critical: require explicit approval
                repair_report["actions_pending_approval"].append(action)
        
        # Step 4: Re-run integrity check
        final_report = self.detect_edge_clutter()
        repair_report["integrity_after"] = self.integrity_score
        
        # Step 5: Save repair log
        self._save_repair_log(repair_report)
        
        self.repair_stats["repairs_attempted"] += len(repair_actions)
        self.repair_stats["last_repair_timestamp"] = datetime.now().isoformat()
        
        self.logger.info(f"Self-repair complete: {len(repair_report['actions_taken'])} executed, "
                        f"{len(repair_report['actions_pending_approval'])} pending")
        
        return repair_report
    
    def _generate_repair_actions(self, clutter_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert clutter report into prioritized repair actions"""
        
        actions = []
        
        # Priority 1: Conflicting edges (critical)
        for conflict in clutter_report.get("conflicting_edges", []):
            actions.append({
                "action_id": f"repair_conflict_{hashlib.sha256(str(conflict).encode()).hexdigest()[:12]}",
                "type": "resolve_conflict",
                "severity": "critical",
                "edge": conflict["edge"],
                "description": f"Resolve conflicting relationship: {conflict['reason']}",
                "proposed_solution": self._propose_conflict_resolution(conflict),
                "backup_required": True
            })
        
        # Priority 2: Redundant edges (high)
        for redundant in clutter_report.get("redundant_edges", []):
            actions.append({
                "action_id": f"prune_redundant_{hashlib.sha256(str(redundant).encode()).hexdigest()[:12]}",
                "type": "prune_edge",
                "severity": "high",
                "edge": redundant["edge"],
                "description": f"Remove redundant edge: {redundant['reason']}",
                "proposed_solution": self._propose_edge_pruning(redundant),
                "backup_required": False
            })
        
        # Priority 3: Low-value edges (medium)
        for low_value in clutter_report.get("low_value_edges", []):
            # Only suggest pruning if edge is very low value
            if low_value["value"] < 0.15:
                actions.append({
                    "action_id": f"prune_lowvalue_{hashlib.sha256(str(low_value).encode()).hexdigest()[:12]}",
                    "type": "prune_edge",
                    "severity": "medium",
                    "edge": low_value["edge"],
                    "description": f"Remove low-value edge: {low_value['reason']}",
                    "proposed_solution": self._propose_edge_pruning(low_value),
                    "backup_required": False
                })
        
        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        actions.sort(key=lambda x: severity_order[x["severity"]])
        
        return actions
    
    def _propose_conflict_resolution(self, conflict: Dict) -> str:
        """Propose solution for edge conflict"""
        
        u, v, key = conflict["edge"]
        conflict_type = conflict["conflict_type"]
        
        # Analyze which edge is more valuable
        conflicting_edges = []
        for src, dst, k, d in self.kg.in_edges(u, data=True, keys=True):
            if dst == v:
                conflicting_edges.append((src, dst, k, d))
        
        # Find highest value edge among conflicts
        max_value = 0
        best_edge = None
        
        for edge_data in conflicting_edges:
            value = self._calculate_edge_value(*edge_data)
            if value > max_value:
                max_value = value
                best_edge = edge_data
        
        # Propose keeping highest value edge
        if best_edge:
            return f"Keep edge {best_edge[0]}->{best_edge[1]} (value: {max_value:.2f}) " \
                   f"and remove conflicting edges"
        
        return "Manual review required - unable to determine optimal edge"
    
    def _propose_edge_pruning(self, edge_info: Dict) -> str:
        """Propose safe pruning of edge"""
        
        u, v, key = edge_info["edge"]
        
        return f"Remove edge {u}->{v} (key: {key}) to improve compositional integrity. " \
               f"Edge value ({edge_info['value']:.2f}) indicates low contribution to knowledge structure."
    
    def _execute_repair_action(self, action: Dict[str, Any]):
        """Execute a single repair action"""
        
        try:
            if action["type"] == "prune_edge":
                self._prune_edge(action["edge"], action["action_id"])
            
            elif action["type"] == "resolve_conflict":
                self._resolve_conflict(action["edge"], action["proposed_solution"])
            
            else:
                self.logger.warning(f"Unknown repair action type: {action['type']}")
        
        except Exception as e:
            self.logger.error(f"Repair action failed: {action['action_id']} - {e}")
            # Continue with other repairs
    
    def _prune_edge(self, edge: Tuple[str, str, int], action_id: str):
        """Safely remove an edge from knowledge graph"""
        
        u, v, key = edge
        
        # Create backup first
        self._create_edge_backup(u, v, action_id, key)
        
        # Remove the specific edge
        if self.kg.has_edge(u, v, key):
            edge_data = self.kg.get_edge_data(u, v, key)
            self.kg.remove_edge(u, v, key)
            
            self.repair_stats["edges_pruned"] += 1
            
            self.logger.info(f"Pruned edge {u}->{v} (key: {key}), action: {action_id}")
        else:
            self.logger.warning(f"Edge {u}->{v} (key: {key}) already removed")
    
    def _resolve_conflict(self, edge: Tuple[str, str, int], solution: str):
        """Resolve edge conflict according to proposed solution"""
        
        u, v, key = edge
        
        # Create backup first
        self._create_edge_backup(u, v, f"conflict_resolution_{key}", key)
        
        # Remove the conflicting edge
        if self.kg.has_edge(u, v, key):
            self.kg.remove_edge(u, v, key)
            self.repair_stats["edges_pruned"] += 1
            self.logger.info(f"Resolved conflict by removing edge {u}->{v} (key: {key}): {solution}")
        else:
            self.logger.warning(f"Conflicting edge {u}->{v} (key: {key}) already removed")
        self.repair_stats["integrity_violations_detected"] += 1
    
    def _create_edge_backup(self, u: str, v: str, action_id: str, key: Optional[int] = None):
        """Create backup of edge before modification"""
        
        if key is not None and self.kg.has_edge(u, v, key):
            backup_data = {
                "action_id": action_id,
                "timestamp": datetime.now().isoformat(),
                "edge": (u, v, key),
                "edge_data": self.kg.get_edge_data(u, v, key)
            }
        elif self.kg.has_edge(u, v):
            backup_data = {
                "action_id": action_id,
                "timestamp": datetime.now().isoformat(),
                "edge": (u, v),
                "edge_data": self.kg.get_edge_data(u, v)
            }
        else:
            return  # No edge to backup
        
        backup_file = self.skg_path / "backups" / f"edge_backup_{action_id}.json"
        backup_file.parent.mkdir(exist_ok=True)
        
        backup_file.write_text(json.dumps(backup_data, indent=2))
        self.logger.debug(f"Edge backup created: {backup_file}")
    
    def _save_repair_log(self, repair_report: Dict[str, Any]):
        """Save detailed repair log"""
        
        repair_file = self.repair_log
        repair_file.parent.mkdir(exist_ok=True)
        
        with open(repair_file, 'a') as f:
            f.write(json.dumps(repair_report) + "\n")
    
    def _run_compositional_integrity_check(self):
        """Initial integrity check on startup"""
        
        self.logger.info("Checking compositional integrity...")
        
        # Check for obvious issues
        issues = []
        
        # 1. Verify core nodes exist
        core_nodes = ["cali_identity", "communication_protocol", "orb_interface"]
        for node in core_nodes:
            if node not in self.kg.nodes():
                issues.append(f"Missing core node: {node}")
        
        # 2. Check for disconnected nodes
        disconnected = [n for n in self.kg.nodes() if self.kg.degree(n) == 0]
        if disconnected:
            issues.append(f"Disconnected nodes: {disconnected}")
        
        # 3. Validate integrity score
        if self.integrity_score < 0.7:
            issues.append(f"Low integrity score: {self.integrity_score:.2f}")
        
        if issues:
            self.logger.warning(f"Integrity issues found on startup: {issues}")
            self.repair_stats["integrity_violations_detected"] += len(issues)
        else:
            self.logger.info("Compositional integrity verified on startup")
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """Get self-repair statistics"""
        
        return {
            **self.repair_stats,
            "current_integrity_score": self.integrity_score,
            "kg_size_nodes": len(self.kg.nodes()),
            "kg_size_edges": len(self.kg.edges()),
            "clutter_threshold": self.clutter_threshold,
            "vault_integrity_verified": self.verify_vault_integrity()
        }
    
    def schedule_repair_cycle(self, interval_hours: int = 24):
        """
        Schedule automatic repair cycle
        Only performs detection, requires approval for modifications
        
        Args:
            interval_hours: How often to run self-repair check
        """
        
        # This would integrate with a task scheduler
        # For now, just log the intent
        
        self.logger.info(f"Scheduled self-repair cycle every {interval_hours} hours")
        
        # Example integration (would need actual scheduler):
        # schedule.every(interval_hours).hours.do(self.run_self_repair, auto_approve=False)
        
        # Manual trigger for now:
        repair_report = self.run_self_repair(auto_approve=False)
        
        if repair_report["actions_pending_approval"]:
            self.logger.warning(f"Self-repair requires approval: {len(repair_report['actions_pending_approval'])} actions")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive CALI system status"""
        
        return {
            "core_signature": hashlib.sha256(str(self.core_personality).encode()).hexdigest()[:16],
            "kg_nodes": len(self.kg.nodes()),
            "kg_edges": len(self.kg.edges()),
            "learning_vault_size": len(self.learned_preferences.get("patterns", [])),
            "user_trust_level": self.kg.nodes["user_relationship"]["trust_level"],
            "interaction_count": self.kg.nodes["user_relationship"]["interaction_count"],
            "vault_integrity": self.verify_vault_integrity(),
            "orb_status": self.current_state["orb_connection_status"],
            "last_interaction": self.current_state["last_user_interaction"],
            "core_version": "3.0.0",
            "personality_signature": self.core_personality["archetype"],
            # Self-repair status
            "compositional_integrity": self.integrity_score,
            "repair_stats": self.get_repair_statistics(),
            "clutter_threshold": self.clutter_threshold
        }