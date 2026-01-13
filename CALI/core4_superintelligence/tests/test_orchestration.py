# test_orchestration.py
import pytest
import numpy as np
from orchestration.orchestration_skg import AttentionGovernor, MemoryMatrix
from orchestration.unified_vault import UnifiedVault, UnifiedSensoryIO
from bridge.core4_bridge import Core4Bridge

class TestAttentionGovernor:
    """Test suite for attention-based orchestration"""
    
    def setup_method(self):
        self.orchestrator = AttentionGovernor(dim=512)
    
    def test_initialization(self):
        """Test proper initialization of attention matrices"""
        assert self.orchestrator.dim == 512
        assert self.orchestrator.Wq.shape == (512, 512)
        assert 'ucm_core' in self.orchestrator.Wk
        assert isinstance(self.orchestrator.memory_matrix, MemoryMatrix)
    
    def test_softmax(self):
        """Test softmax implementation"""
        x = np.array([1.0, 2.0, 3.0])
        result = self.orchestrator._softmax(x)
        assert len(result) == 3
        assert np.isclose(np.sum(result), 1.0)
        assert all(result >= 0)
    
    def test_compute_attention_weights(self):
        """Test attention weight computation"""
        context = np.random.randn(512)
        core_states = {
            'ucm_core': np.random.randn(512),
            'kaygee': np.random.randn(512),
            'caleon': np.random.randn(512),
            'cali_x': np.random.randn(512)
        }
        
        weights = self.orchestrator.compute_attention_weights(context, core_states)
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)
        assert all(weights >= 0)
    
    def test_orchestrate(self):
        """Test full orchestration pipeline"""
        core_verdicts = {
            'ucm_core': {
                'confidence': 0.85,
                'coherence': 0.9,
                'completeness': 0.8,
                'ethical_alignment': 0.95,
                'recommended_path': 'philosophical_analysis'
            },
            'kaygee': {
                'confidence': 0.75,
                'coherence': 0.95,
                'completeness': 0.7,
                'ethical_alignment': 0.9,
                'recommended_path': 'cognitive_monitoring'
            },
            'caleon': {
                'confidence': 0.9,
                'coherence': 0.85,
                'completeness': 0.95,
                'ethical_alignment': 0.85,
                'recommended_path': 'consciousness_flow'
            },
            'cali_x': {
                'confidence': 0.8,
                'coherence': 0.8,
                'completeness': 0.85,
                'ethical_alignment': 0.8,
                'recommended_path': 'knowledge_synthesis'
            }
        }
        
        context_vector = np.random.randn(512)
        result = self.orchestrator.orchestrate(core_verdicts, context_vector)
        
        # Check result structure
        assert 'unified_verdict' in result
        assert 'attention_weights' in result
        assert 'confidence_score' in result
        assert 'dominant_core' in result
        assert 'council_recommendation' in result
        assert 'memory_update' in result
        
        # Check attention weights
        assert len(result['attention_weights']) == 4
        assert result['dominant_core'] in core_verdicts
        
        # Check confidence bounds
        assert 0 <= result['confidence_score'] <= 1.0
    
    def test_extract_competency_vector(self):
        """Test competency vector extraction"""
        verdict = {
            'confidence': 0.8,
            'coherence': 0.9,
            'completeness': 0.7,
            'ethical_alignment': 0.85
        }
        
        vector = self.orchestrator._extract_competency_vector(verdict)
        assert len(vector) == 512
        assert np.isclose(np.linalg.norm(vector), 1.0)  # Normalized
    
    def test_weighted_fusion(self):
        """Test verdict fusion with attention weights"""
        verdicts = {
            'ucm_core': {'recommended_path': 'path1', 'constraints': ['a', 'b']},
            'kaygee': {'recommended_path': 'path2', 'constraints': ['c']},
            'caleon': {'recommended_path': 'path1', 'constraints': ['d']},
            'cali_x': {'recommended_path': 'path3', 'constraints': ['e']}
        }
        
        weights = np.array([0.4, 0.3, 0.2, 0.1])
        result = self.orchestrator._weighted_fusion(verdicts, weights)
        
        assert 'primary_path' in result
        assert 'ethical_constraints' in result
        assert 'confidence_trajectory' in result
        assert 'cognitive_resonance' in result
        
        # Check resonance calculation (std of weights)
        expected_resonance = np.std(weights)
        assert np.isclose(result['cognitive_resonance'], expected_resonance)
    
    def test_compute_confidence(self):
        """Test confidence scoring with scaling laws"""
        attention_weights = np.array([0.4, 0.3, 0.2, 0.1])
        core_confidences = [0.8, 0.9, 0.7, 0.85]
        
        confidence = self.orchestrator._compute_confidence(attention_weights, core_confidences)
        
        # Should be between 0 and 1
        assert 0 <= confidence <= 1.0
        
        # Higher when weights are more equal (consensus bonus)
        equal_weights = np.array([0.25, 0.25, 0.25, 0.25])
        equal_confidence = self.orchestrator._compute_confidence(equal_weights, core_confidences)
        assert equal_confidence >= confidence  # Consensus bonus
    
    def test_generate_recommendation(self):
        """Test recommendation generation based on confidence"""
        # High confidence
        rec = self.orchestrator._generate_recommendation(
            {'primary_path': 'test_path'}, 0.9
        )
        assert "High-confidence" in rec
        
        # Moderate confidence
        rec = self.orchestrator._generate_recommendation(
            {'primary_path': 'test_path'}, 0.7
        )
        assert "Moderate convergence" in rec
        
        # Low confidence
        rec = self.orchestrator._generate_recommendation(
            {'primary_path': 'test_path'}, 0.4
        )
        assert "Low consensus" in rec

class TestMemoryMatrix:
    """Test memory matrix functionality"""
    
    def setup_method(self):
        self.memory = MemoryMatrix(dim=512, max_entries=100)
    
    def test_initialization(self):
        """Test memory matrix setup"""
        assert self.memory.dim == 512
        assert self.memory.max_entries == 100
        assert self.memory.entries == []
    
    def test_update(self):
        """Test memory storage"""
        context = np.random.randn(512)
        verdict = {'test': 'data'}
        
        result = self.memory.update(context, verdict)
        
        assert 'memory_id' in result
        assert 'retention_probability' in result
        assert 'eviction_risk' in result
        assert len(self.memory.entries) == 1
        
        # Check entry structure
        entry = self.memory.entries[0]
        assert 'timestamp' in entry
        assert 'context' in entry
        assert 'verdict_hash' in entry
        assert 'attention_score' in entry
    
    def test_retrieve(self):
        """Test memory retrieval"""
        # Add some entries
        for i in range(5):
            context = np.random.randn(512)
            verdict = {'id': i}
            self.memory.update(context, verdict)
        
        # Retrieve with similar query
        query = np.random.randn(512)
        results = self.memory.retrieve(query, top_k=3)
        
        assert len(results) == 3
        # Results should be sorted by similarity
    
    def test_eviction(self):
        """Test memory eviction"""
        self.memory.max_entries = 3
        
        # Add more than max entries
        for i in range(5):
            context = np.random.randn(512)
            verdict = {'id': i}
            self.memory.update(context, verdict)
        
        # Should only keep last 3
        assert len(self.memory.entries) == 3
        assert self.memory.entries[0]['timestamp'] == 2  # First two evicted

class TestUnifiedVault:
    """Test vault functionality"""
    
    def setup_method(self):
        self.vault = UnifiedVault(vault_path="./test_vault")
    
    def test_store_and_retrieve(self):
        """Test basic store/retrieve"""
        payload = {'test': 'data', 'value': 42}
        vault_addr = self.vault.store('ucm_core', 'judgments', payload)
        
        retrieved = self.vault.retrieve(vault_addr, 'ucm_core')
        assert retrieved == payload
    
    def test_access_control(self):
        """Test permission system"""
        payload = {'secret': 'data'}
        vault_addr = self.vault.store('caleon', 'consciousness', payload)
        
        # Caleon can read its own
        assert self.vault.retrieve(vault_addr, 'caleon') == payload
        
        # KayGee can read all states
        assert self.vault.retrieve(vault_addr, 'kaygee') == payload
        
        # UCM cannot read Caleon's consciousness
        with pytest.raises(PermissionError):
            self.vault.retrieve(vault_addr, 'ucm_core')
    
    def test_invalid_permissions(self):
        """Test permission enforcement"""
        payload = {'data': 'test'}
        
        # KayGee cannot write to Cali_X's data type
        with pytest.raises(PermissionError):
            self.vault.store('kaygee', 'skg', payload)

class TestUnifiedSensoryIO:
    """Test sensory I/O system"""
    
    def setup_method(self):
        orchestrator = AttentionGovernor()
        self.sensory = UnifiedSensoryIO(orchestrator)
    
    def test_process_audio_input(self):
        """Test audio processing pipeline"""
        audio_data = b"fake audio data"
        result = self.sensory.process_audio_input(audio_data)
        
        assert 'unified_verdict' in result
        assert 'attention_weights' in result
        assert 'confidence_score' in result
        assert 'dominant_core' in result
    
    def test_voice_modulation(self):
        """Test voice parameter mapping"""
        weights = {'ucm_core': 0.4, 'kaygee': 0.3, 'caleon': 0.2, 'cali_x': 0.1}
        
        pitch = self.sensory._map_attention_to_pitch(weights)
        assert pitch == 1.0  # UCM dominant
        
        tempo = self.sensory._map_confidence_to_tempo(0.8)
        assert 0.7 <= tempo <= 1.5
        
        tone = self.sensory._infer_tone(0.9, weights)
        assert tone == "authoritative"

class TestCore4Bridge:
    """Test integration bridge"""
    
    def setup_method(self):
        self.bridge = Core4Bridge()
    
    def test_initialization(self):
        """Test bridge setup"""
        assert not any(self.bridge.active_cores.values())  # None active initially
        assert hasattr(self.bridge, 'orchestrator')
        assert hasattr(self.bridge, 'vault')
        assert hasattr(self.bridge, 'sensory')
    
    @pytest.mark.asyncio
    async def test_unified_query(self):
        """Test unified query processing"""
        query = "What is the meaning of life?"
        result = await self.bridge.unified_query(query)
        
        assert 'unified_verdict' in result
        assert 'attention_weights' in result
        assert 'confidence_score' in result
        assert 'council_recommendation' in result
    
    @pytest.mark.asyncio
    async def test_core_queries(self):
        """Test individual core queries"""
        query = "Test query"
        context = np.random.randn(512)
        
        ucm_result = await self.bridge._query_ucm_core(query, context)
        assert 'recommended_path' in ucm_result
        assert 'confidence' in ucm_result
        
        kaygee_result = await self.bridge._query_kaygee(query, context)
        assert 'resonance_score' in kaygee_result
        
        caleon_result = await self.bridge._query_caleon(query, context)
        assert 'consciousness_state' in caleon_result
        
        cali_result = await self.bridge._query_cali_x(query, context)
        assert 'patterns_found' in cali_result

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])