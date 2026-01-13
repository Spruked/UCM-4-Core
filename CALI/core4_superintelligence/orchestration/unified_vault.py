# unified_vault.py
import os
import json
from typing import Dict, Optional, Any
import numpy as np
from cryptography.fernet import Fernet
from datetime import datetime
from .orchestration_skg import AttentionGovernor
from .providers import ASRProvider, EmbeddingProvider


class VaultBindingError(RuntimeError):
    pass

class UnifiedVault:
    """
    Single vault system for all four cores
    Each core accesses different slices with different permissions
    Requires real ASR + embedding providers (no stubs).
    """
    
    def __init__(self, asr: ASRProvider, embedder: EmbeddingProvider, dim: int, vault_path: str = "./unified_vault"):
        if not asr or not embedder:
            raise VaultBindingError("ASR and Embedding providers are required")
        self.asr = asr
        self.embedder = embedder
        self.dim = dim

        self.vault_path = vault_path
        self.keys_path = os.path.join(vault_path, "master_keys")
        self.memory_matrix_path = os.path.join(vault_path, "memory_matrix")
        self.core_slices = {
            'ucm_core': os.path.join(vault_path, "ecm_contracts"),
            'kaygee': os.path.join(vault_path, "cognitive_resonance"),
            'caleon': os.path.join(vault_path, "consciousness_states"),
            'cali_x': os.path.join(vault_path, "skg_knowledge")
        }
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Core-specific access patterns
        self.access_policies = {
            'ucm_core': ['read_contracts', 'write_judgments', 'judgments'],
            'kaygee': ['read_resonance', 'write_metrics', 'read_all_states', 'metrics'],
            'caleon': ['read_consciousness', 'write_experiences', 'read_contracts', 'consciousness', 'experiences'],
            'cali_x': ['read_skg', 'write_patterns', 'read_all_knowledge', 'knowledge']
        }
    
    def _initialize_encryption(self):
        """Master key for all vault access"""
        if not os.path.exists(self.keys_path):
            os.makedirs(self.keys_path, exist_ok=True)
            key = Fernet.generate_key()
            with open(os.path.join(self.keys_path, "master.key"), "wb") as f:
                f.write(key)
    
    def store(self, core_id: str, data_type: str, payload: Dict) -> str:
        """Unified storage with core-specific indexing. Requires real, non-empty payload."""

        if not isinstance(payload, dict) or not payload:
            raise RuntimeError("payload must be a non-empty dict")

        # Validate access policy
        if data_type not in self.access_policies.get(core_id, []):
            raise PermissionError(f"Core {core_id} cannot write to {data_type}")

        # Generate vault address
        timestamp = datetime.now().isoformat()
        vault_address = {
            'core_id': core_id,
            'data_type': data_type,
            'timestamp': timestamp,
            'slice': self.core_slices[core_id],
            'access_policy': self.access_policies[core_id]
        }

        # Encrypt payload
        with open(os.path.join(self.keys_path, "master.key"), "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(payload).encode())

        # Store in appropriate slice
        slice_path = self.core_slices[core_id]
        os.makedirs(slice_path, exist_ok=True)

        filename = f"{core_id}_{data_type}_{hash(encrypted)}.vault"
        filepath = os.path.join(slice_path, filename)

        with open(filepath, "wb") as f:
            f.write(encrypted)

        # Update memory matrix index
        self._update_memory_index(vault_address, encrypted)

        return f"vault://{core_id}/{data_type}/{hash(encrypted)}"
    
    def retrieve(self, vault_address: str, requester_core: str) -> Optional[Dict]:
        """
        Retrieve from vault with cross-core access control
        Some cores can read others' data (KayGee monitors all)
        """
        
        # Parse vault address
        parts = vault_address.replace("vault://", "").split("/")
        if len(parts) != 3:
            raise ValueError("Invalid vault address")
        
        target_core, data_type, data_hash = parts
        
        # Check cross-core read permissions
        read_policy = self.access_policies.get(requester_core, [])
        can_read_cross = "read_all_states" in read_policy or "read_all_knowledge" in read_policy
        
        if target_core != requester_core and not can_read_cross:
            # Still allow if it's consciousness data (Caleon transparency)
            if not (requester_core == "caleon" and data_type == "consciousness"):
                raise PermissionError(f"Core {requester_core} cannot read {target_core}'s vault")
        
        # Find and decrypt
        slice_path = self.core_slices[target_core]
        pattern = f"{target_core}_{data_type}_*.vault"
        
        import glob
        matches = glob.glob(os.path.join(slice_path, pattern))
        
        for filepath in matches:
            if data_hash in filepath:
                with open(filepath, "rb") as f:
                    encrypted = f.read()
                
                with open(os.path.join(self.keys_path, "master.key"), "rb") as f_key:
                    key = f_key.read()
                
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted)
                return json.loads(decrypted.decode())
        
        return None
    
    def _update_memory_index(self, vault_address: Dict, encrypted_data: bytes):
        """Maintain index for memory matrix retrieval"""
        index_path = os.path.join(self.vault_path, "memory_index.json")
        
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                index = json.load(f)
        else:
            index = []
        
        index.append({
            'timestamp': vault_address['timestamp'],
            'core_id': vault_address['core_id'],
            'data_type': vault_address['data_type'],
            'vault_hash': hash(encrypted_data),
            'access_count': 0
        })
        
        # Keep only recent 10000 entries
        if len(index) > 10000:
            index = index[-10000:]
        
        with open(index_path, "w") as f:
            json.dump(index, f)


# Shared sensory I/O manager
class UnifiedSensoryIO:
    """
    Single voice and ears for all four cores
    Cochlear processors → 4 cores → POM voice output
    Requires injected vault with real ASR/embedder (no stubs).
    """
    
    def __init__(self, orchestrator: AttentionGovernor, vault_ref: UnifiedVault):
        if not orchestrator:
            raise VaultBindingError("orchestrator is required")
        if not vault_ref:
            raise VaultBindingError("vault_ref with real providers is required")
        self.orchestrator = orchestrator
        self.vault = vault_ref
        
        # Audio pipeline (from Caleon_Genesis)
        self.audio_input = None  # Cochlear processor
        self.audio_output = None  # POM voice
        
        # Voice state shared across cores
        self.voice_profile = {
            'active_speaker': None,  # Which core is currently "speaking"
            'interruption_allowed': True,
            'barge_in_enabled': True
        }
    
    def process_audio_input(self, audio_data: bytes, sample_rate: int) -> Dict:
        """
        Single audio input processed by all four cores. Requires real transcription and embeddings.
        Raises if any dependency fails.
        """

        transcription = self._transcribe_audio(audio_data, sample_rate)

        if not transcription or not isinstance(transcription, dict):
            raise VaultBindingError("transcription must be a non-empty dict with source and content")

        source = transcription.get('source')
        content = transcription.get('content')

        if not source or not isinstance(source, str):
            raise VaultBindingError("transcription source is required")
        if not content or not isinstance(content, str):
            raise VaultBindingError("transcription content is required")

        # Create context vector for attention mechanism
        context_vector = self._embed_transcription(content)

        # Each core processes according to its nature (must return real verdicts)
        core_verdicts = {
            'ucm_core': self._process_philosophical(content, context_vector),
            'kaygee': self._process_cognitive(content, context_vector),
            'caleon': self._process_consciousness(content, context_vector),
            'cali_x': self._process_knowledge(content, context_vector)
        }

        orchestration_result = self.orchestrator.orchestrate(
            core_verdicts=core_verdicts,
            context_vector=context_vector
        )

        self.vault.store(
            core_id='caleon',
            data_type='consciousness',
            payload={
                'transcription': transcription,
                'core_interpretations': core_verdicts,
                'orchestrated_understanding': orchestration_result,
                'timestamp': datetime.now().isoformat()
            }
        )

        return orchestration_result
    
    def generate_voice_output(self, orchestration_result: Dict) -> bytes:
        """
        Single voice output representing the council's consensus
        SoftMax weights determine voice modulation parameters
        """
        
        # Extract attention weights for voice characteristics
        attention_weights = orchestration_result['attention_weights']
        confidence = orchestration_result['confidence_score']
        
        # Voice modulation based on consensus
        voice_params = {
            'pitch': self._map_attention_to_pitch(attention_weights),
            'tempo': self._map_confidence_to_tempo(confidence),
            'emphasis_core': orchestration_result['dominant_core'],
            'emotional_tone': self._infer_tone(confidence, attention_weights)
        }
        
        # Generate speech using POM (from Caleon)
        text = orchestration_result['council_recommendation']
        audio = self._synthesize_speech(text, voice_params)
        
        return audio
    
    def _transcribe_audio(self, audio_data: bytes, sample_rate: int) -> Dict:
        """Cochlear processor integration: must return {'source': ..., 'content': ...} or raise."""
        tx = self.vault.asr.transcribe(audio_data, sample_rate)
        if not isinstance(tx, dict) or not tx.get("content") or not tx.get("source"):
            raise VaultBindingError("ASR transcription invalid")
        return tx
    
    def _embed_transcription(self, text: str) -> np.ndarray:
        """Create context vector for attention. Must produce real, finite vector."""
        if not text or not isinstance(text, str):
            raise VaultBindingError("text is required for embedding")

        vec = self.vault.embedder.embed(text)
        if not isinstance(vec, np.ndarray) or vec.shape[0] != self.vault.dim:
            raise VaultBindingError("Invalid embedding shape")
        if not np.isfinite(vec).all() or np.linalg.norm(vec) == 0:
            raise VaultBindingError("Invalid embedding values")
        return vec
    
    def _process_philosophical(self, text: str, context: np.ndarray) -> Dict:
        """UCM_Core_ECM philosophical analysis: must be implemented with real model."""
        raise RuntimeError("_process_philosophical must be implemented with real UCM core output")

    def _process_cognitive(self, text: str, context: np.ndarray) -> Dict:
        """KayGee cognitive resonance analysis: must be implemented with real model."""
        raise RuntimeError("_process_cognitive must be implemented with real KayGee output")

    def _process_consciousness(self, text: str, context: np.ndarray) -> Dict:
        """Caleon consciousness integration: must be implemented with real model."""
        raise RuntimeError("_process_consciousness must be implemented with real Caleon output")

    def _process_knowledge(self, text: str, context: np.ndarray) -> Dict:
        """Cali_X SKG pattern recognition: must be implemented with real model."""
        raise RuntimeError("_process_knowledge must be implemented with real Cali_X output")
    
    def _map_attention_to_pitch(self, weights: Dict) -> float:
        """Voice pitch based on dominant core"""
        dominant = max(weights, key=weights.get)
        pitch_map = {
            'ucm_core': 1.0,    # Neutral philosophical tone
            'kaygee': 1.2,      # Slightly higher for cognitive clarity
            'caleon': 0.9,      # Deeper for consciousness authority
            'cali_x': 1.1       # Balanced for knowledge synthesis
        }
        return pitch_map.get(dominant, 1.0)
    
    def _map_confidence_to_tempo(self, confidence: float) -> float:
        """Speaking tempo based on confidence"""
        # 0.5 = slow deliberate, 1.5 = fast confident
        return 0.7 + (confidence * 0.8)
    
    def _infer_tone(self, confidence: float, weights: Dict) -> str:
        """Emotional tone based on consensus"""
        if confidence > 0.85:
            return "authoritative"
        elif confidence > 0.6:
            return "deliberative"
        else:
            return "uncertain"


# No implicit initialization: real providers must be injected by the caller.