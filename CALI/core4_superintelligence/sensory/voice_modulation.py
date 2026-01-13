# voice_modulation.py
class VoiceModulator:
    """
    Attention-weighted voice synthesis for unified council output
    """
    
    def __init__(self):
        self.base_pitch = 1.0
        self.base_tempo = 1.0
        
    def modulate_voice(self, text: str, attention_weights: Dict, confidence: float) -> Dict:
        """
        Modulate voice parameters based on council consensus
        """
        
        # Extract dominant core for pitch
        dominant_core = max(attention_weights, key=attention_weights.get)
        
        # Pitch modulation
        pitch_modifier = self._get_pitch_modifier(dominant_core)
        
        # Tempo based on confidence
        tempo_modifier = self._get_tempo_modifier(confidence)
        
        # Emotional tone
        tone = self._infer_emotional_tone(confidence, attention_weights)
        
        return {
            'text': text,
            'voice_params': {
                'pitch': self.base_pitch * pitch_modifier,
                'tempo': self.base_tempo * tempo_modifier,
                'tone': tone,
                'dominant_core': dominant_core,
                'confidence_level': confidence
            }
        }
    
    def _get_pitch_modifier(self, dominant_core: str) -> float:
        """Pitch adjustment based on core specialization"""
        pitch_map = {
            'ucm_core': 1.0,    # Neutral philosophical tone
            'kaygee': 1.2,      # Slightly higher for cognitive clarity
            'caleon': 0.9,      # Deeper for consciousness authority
            'cali_x': 1.1       # Balanced for knowledge synthesis
        }
        return pitch_map.get(dominant_core, 1.0)
    
    def _get_tempo_modifier(self, confidence: float) -> float:
        """Speaking tempo based on confidence level"""
        # 0.5 = slow deliberate, 1.5 = fast confident
        return 0.7 + (confidence * 0.8)
    
    def _infer_emotional_tone(self, confidence: float, weights: Dict) -> str:
        """Determine emotional tone from consensus quality"""
        # Calculate consensus (inverse of attention variance)
        import numpy as np
        weights_array = np.array(list(weights.values()))
        consensus = 1.0 - np.std(weights_array)
        
        if confidence > 0.85 and consensus > 0.8:
            return "authoritative"
        elif confidence > 0.6:
            return "deliberative"
        elif consensus < 0.5:
            return "conflicted"
        else:
            return "uncertain"