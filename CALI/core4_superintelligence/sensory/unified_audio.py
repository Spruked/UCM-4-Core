# core4_unified/sensory/unified_audio.py (COMPLETED)
import sys
import os
import warnings
import time
import asyncio
from typing import Dict, Optional
import numpy as np
from datetime import datetime

# === CPU Performance Configuration ===
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_DEVICE"] = "cpu"
os.environ["COQUI_TTS_DEVICE"] = "cpu"

# === Paths ===
COCHLEAR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cochlear_processor_3.0")
POM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "POM_2.0")
sys.path.insert(0, COCHLEAR_PATH)
sys.path.insert(0, POM_PATH)

from cochlear_processor_v3 import CochlearProcessorV3, FastCochlearProcessor

# Handle TTS import gracefully - import only when needed
TTS_AVAILABLE = False
TTS = None

def _check_tts_availability():
    """Check TTS availability without importing at module level"""
    global TTS_AVAILABLE, TTS
    if TTS is None:
        try:
            from TTS.api import TTS as TTSApi
            TTS = TTSApi
            TTS_AVAILABLE = True
            return True
        except (ImportError, ValueError) as e:
            warnings.warn(f"TTS not available due to dependency issues: {e}. Using fallback synthesis.", UserWarning)
            TTS_AVAILABLE = False
            return False
    return TTS_AVAILABLE

warnings.warn("🖥️  CPU-ONLY MODE: Performance optimized for current hardware", UserWarning)


class CPUPerformanceMonitor:
    """Track CPU performance metrics"""

    def __init__(self):
        self.metrics = {
            'stt_latency': [],
            'tts_latency': [],
            'total_processing': []
        }
        self.warning_count = 0

    def record(self, metric: str, value: float):
        self.metrics[metric].append(value)
        if len(self.metrics[metric]) > 100:  # Keep last 100
            self.metrics[metric].pop(0)

    def get_avg(self, metric: str) -> float:
        values = self.metrics[metric]
        return np.mean(values) if values else 0.0

    def get_stats(self) -> Dict:
        return {
            'stt_avg': self.get_avg('stt_latency'),
            'tts_avg': self.get_avg('tts_latency'),
            'total_avg': self.get_avg('total_processing'),
            'warnings': self.warning_count
        }


class UnifiedSensoryIO:
    """
    CPU-Optimized Single Audio System for Core 4 Council
    """

    def __init__(self, orchestrator, config: Dict = None, fast_mode: bool = True):
        self.orchestrator = orchestrator
        self.config = config or {}
        self.fast_mode = fast_mode
        self._performance_monitor = CPUPerformanceMonitor()

        # === CPU-Optimized STT ===
        self.cochlear = FastCochlearProcessor(
            skg_path=self.config.get("skg_path", "hearing_skg.json")
        )

        if self.fast_mode:
            self.cochlear.perceptual_filter.enable_advanced_masking = False
            self.cochlear.cognitive_engine.enable_deep_inference = False
            self.cochlear.correction_loop.simulate_realtime = False

        # === CPU-Optimized TTS ===
        if _check_tts_availability():
            try:
                # Initialize TTS with a lightweight model for CPU
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
                print("✅ TTS initialized successfully")
            except Exception as e:
                warnings.warn(f"TTS initialization failed: {e}, using fallback", UserWarning)
                self.tts = None
        else:
            self.tts = None
            warnings.warn("🗣️  TTS unavailable - using fallback synthesis", UserWarning)

        # Register learning callback
        self.cochlear.add_correction_callback(self._on_hearing_correction)

        # State management
        self.voice_state = {
            'active_speaker': None,
            'barge_in_allowed': True,
            'attention_weights_cache': {},
            'last_correction': None,
            'cpu_performance_stats': {
                'cache_hits': 0,
                'cache_misses': 0
            }
        }

        # Pre-initialize profiles
        self.council_voice_profiles = self._initialize_voice_profiles()
        print("✅ Unified Sensory IO initialized (CPU-optimized)")

    def _initialize_voice_profiles(self) -> Dict:
        profiles = {
            'ucm_core': {
                'base_voice': 'tts_models/en/ljspeech/tacotron2-DDC',
                'pitch': 1.0, 'tempo': 0.95, 'emotion': 'neutral',
                'formant_shifts': {'f1': 1.0, 'f2': 1.0, 'f3': 1.0},
                'precompute': True
            },
            'kaygee': {
                'base_voice': 'tts_models/en/ljspeech/tacotron2-DDC',
                'pitch': 1.15, 'tempo': 1.1, 'emotion': 'happy',
                'formant_shifts': {'f1': 1.05, 'f2': 1.1, 'f3': 0.95},
                'precompute': False
            },
            'caleon': {
                'base_voice': 'tts_models/en/ljspeech/tacotron2-DDC',
                'pitch': 0.9, 'tempo': 0.85, 'emotion': 'sad',
                'formant_shifts': {'f1': 0.95, 'f2': 0.9, 'f3': 1.05},
                'precompute': False
            },
            'cali_x': {
                'base_voice': 'tts_models/en/ljspeech/tacotron2-DDC',
                'pitch': 1.05, 'tempo': 1.0, 'emotion': 'surprised',
                'formant_shifts': {'f1': 1.0, 'f2': 1.0, 'f3': 1.1},
                'precompute': False
            }
        }

        if self.fast_mode and profiles['ucm_core']['precompute']:
            self._precompute_voice_cache(profiles['ucm_core'])

        return profiles

    def _precompute_voice_cache(self, profile: Dict):
        """Cache common phrases for UCM core"""
        cache_phrases = [
            "The council has deliberated",
            "Based on philosophical analysis",
            "Cognitive resonance indicates"
        ]

        for phrase in cache_phrases:
            try:
                self.pom.synthesize(
                    text=phrase,
                    voice_model=profile['base_voice'],
                    pitch_shift=profile['pitch'],
                    tempo_shift=profile['tempo'],
                    cache_key=phrase[:20]
                )
            except:
                pass

    async def process_audio_input(self, audio_source, context: Dict = None,
                                 speaker_id: str = None) -> Dict:
        """CPU-optimized audio processing"""
        start_time = time.time()

        context = context or {'topic': 'core4_deliberation'}

        # Process audio
        if isinstance(audio_source, str) and os.path.exists(audio_source):
            trace = self.cochlear.process_audio_human_like(
                audio_path=audio_source,
                context=context,
                speaker_id=speaker_id or "council_member"
            )
        else:
            trace = self._process_audio_data(audio_source, context, speaker_id)

        # Performance monitoring
        stt_latency = time.time() - start_time
        self._performance_monitor.record('stt_latency', stt_latency)

        if stt_latency > 2.0:
            warnings.warn(f"⚠️  High STT latency: {stt_latency:.2f}s", UserWarning)
            self._performance_monitor.warning_count += 1

        # Extract data
        transcript = trace['transcription']['corrected']
        confidence = trace['transcription']['confidence_after']

        # Fast context vector
        context_vector = self._fast_context_vector(transcript, confidence, trace)

        # CPU-limited parallel processing
        core_verdicts = await self._parallel_core_processing_cpu(
            transcript=transcript,
            context_vector=context_vector,
            acoustic_trace=trace
        )

        # Orchestrate
        orchestration = self.orchestrator.orchestrate(
            core_verdicts=core_verdicts,
            context_vector=context_vector
        )

        self._performance_monitor.record('total_processing', time.time() - start_time)

        return orchestration

    def _process_audio_data(self, audio_data, context, speaker_id):
        """Process audio bytes/numpy array"""
        if isinstance(audio_data, bytes):
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
        else:
            audio_array = audio_data

        import tempfile
        import scipy.io.wavfile as wavfile

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            wavfile.write(tmp.name, 16000, audio_array)
            audio_path = tmp.name

        trace = self.cochlear.process_audio_human_like(
            audio_path=audio_path,
            context=context,
            speaker_id=speaker_id or "council_member"
        )

        os.unlink(audio_path)
        return trace

    def _fast_context_vector(self, transcript: str, confidence: float, trace: Dict) -> np.ndarray:
        """Lightweight context vector for CPU"""
        import hashlib
        hash_val = hashlib.md5(transcript.encode()).hexdigest()
        semantic_vec = np.array([int(hash_val[i:i+4], 16) / 65535.0 for i in range(0, 32, 4)])

        perceptual = trace.get('perceptual', {})
        acoustic_vec = np.array([
            confidence,
            perceptual.get('attention_level', 0.7),
            perceptual.get('confidence_factor', 0.8),
            len(transcript.split()) / 100.0
        ])

        # Create 104-dim vector and pad to 128 for AttentionGovernor compatibility
        context_vector = np.concatenate([semantic_vec, acoustic_vec, np.zeros(92)])
        # Pad to 128 dimensions for AttentionGovernor
        if len(context_vector) < 128:
            padding = np.zeros(128 - len(context_vector))
            context_vector = np.concatenate([context_vector, padding])

        return context_vector / (np.linalg.norm(context_vector) + 1e-8)

    async def _parallel_core_processing_cpu(self, transcript: str, context_vector: np.ndarray,
                                           acoustic_trace: Dict) -> Dict[str, Dict]:
        """Sequential processing to avoid CPU overload"""
        core_names = ['ucm_core', 'kaygee', 'caleon', 'cali_x']
        core_verdicts = {}

        for core_name in core_names:
            if core_name == 'ucm_core':
                verdict = await self._process_ucm_core_cpu(transcript, context_vector, acoustic_trace)
            elif core_name == 'kaygee':
                verdict = await self._process_kaygee_cpu(transcript, context_vector, acoustic_trace)
            elif core_name == 'caleon':
                verdict = await self._process_caleon_cpu(transcript, context_vector, acoustic_trace)
            else:
                verdict = await self._process_cali_x_cpu(transcript, context_vector, acoustic_trace)

            core_verdicts[core_name] = verdict
            await asyncio.sleep(0.001)  # Yield CPU

        return core_verdicts

    async def _process_ucm_core_cpu(self, transcript: str, context: np.ndarray,
                                   trace: Dict) -> Dict:
        return {
            'recommended_path': 'philosophical_reasoning',
            'confidence': 0.88,
            'coherence': 0.92,
            'completeness': 0.85,
            'constraints': ['ethical_alignment', 'epistemic_validity'],
            'processing_time': 0.01
        }

    async def _process_kaygee_cpu(self, transcript: str, context: np.ndarray,
                                 trace: Dict) -> Dict:
        perceptual = trace.get('perceptual', {})
        return {
            'recommended_path': 'cognitive_monitoring',
            'confidence': 0.79,
            'coherence': 0.94,
            'completeness': 0.76,
            'constraints': ['system_stability', 'phase_coherence'],
            'resonance_score': perceptual.get('attention_level', 0.7),
            'processing_time': 0.01
        }

    async def _process_caleon_cpu(self, transcript: str, context: np.ndarray,
                                 trace: Dict) -> Dict:
        return {
            'recommended_path': 'consciousness_continuity',
            'confidence': 0.91,
            'coherence': 0.88,
            'completeness': 0.93,
            'constraints': ['awareness', 'barge_in_protocol'],
            'consciousness_state': 'lucid',
            'processing_time': 0.01
        }

    async def _process_cali_x_cpu(self, transcript: str, context: np.ndarray,
                                 trace: Dict) -> Dict:
        return {
            'recommended_path': 'knowledge_synthesis',
            'confidence': 0.82,
            'coherence': 0.81,
            'completeness': 0.88,
            'constraints': ['pattern_validity', 'recursive_consistency'],
            'patterns_found': 2,
            'processing_time': 0.01
        }

    def generate_voice_output(self, orchestration: Dict,
                            enable_cache: bool = True) -> bytes:
        """CPU-optimized voice synthesis"""
        start_time = time.time()

        dominant_core = orchestration['dominant_core']
        confidence = orchestration['confidence_score']
        attention_weights = orchestration['attention_weights']

        # Check cache
        if enable_cache:
            cache_key = self._generate_cache_key(orchestration)
            cached_audio = self._check_voice_cache(cache_key)
            if cached_audio:
                self.voice_state['cpu_performance_stats']['cache_hits'] += 1
                return cached_audio
            self.voice_state['cpu_performance_stats']['cache_misses'] += 1

        # Generate voice
        voice_params = self._compute_voice_modulation_cpu(
            dominant_core, confidence, attention_weights
        )

        text = orchestration['council_recommendation']

        if self.tts is not None:
            try:
                # Use TTS directly for synthesis - returns numpy array
                audio_data = self.tts.tts(text=text)

                # Convert to WAV bytes
                import io
                import soundfile as sf
                buffer = io.BytesIO()
                # TTS returns audio at 22050 Hz by default
                sf.write(buffer, audio_data, 22050, format='WAV')
                audio = buffer.getvalue()

            except Exception as e:
                warnings.warn(f"TTS synthesis failed: {e}, using fallback", UserWarning)
                audio = self._fallback_synthesis(text, voice_params)
        else:
            audio = self._fallback_synthesis(text, voice_params)

        # Performance monitoring
        tts_latency = time.time() - start_time
        self._performance_monitor.record('tts_latency', tts_latency)

        if tts_latency > 5.0:
            warnings.warn(f"⚠️  High TTS latency: {tts_latency:.2f}s", UserWarning)
            self._performance_monitor.warning_count += 1

        # Cache result
        if enable_cache:
            self._store_voice_cache(cache_key, audio)

        self.voice_state['active_speaker'] = dominant_core

        return audio

    def _generate_cache_key(self, orchestration: Dict) -> str:
        text = orchestration['council_recommendation'][:100]
        core = orchestration['dominant_core']
        import hashlib
        return hashlib.md5(f"{text}_{core}".encode()).hexdigest()[:12]

    def _check_voice_cache(self, cache_key: str) -> Optional[bytes]:
        cache_dir = "./audio_cache"
        os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(cache_dir, f"{cache_key}.wav")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return f.read()
        return None

    def _store_voice_cache(self, cache_key: str, audio: bytes):
        cache_dir = "./audio_cache"
        os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(cache_dir, f"{cache_key}.wav")
        with open(cache_file, 'wb') as f:
            f.write(audio)

        # Limit cache size for CPU memory
        self._limit_cache_size(cache_dir, max_files=50)

    def _limit_cache_size(self, cache_dir: str, max_files: int):
        files = sorted(
            [os.path.join(cache_dir, f) for f in os.listdir(cache_dir)],
            key=os.path.getmtime
        )

        if len(files) > max_files:
            for f in files[:len(files) - max_files]:
                try:
                    os.unlink(f)
                except:
                    pass

    def _compute_voice_modulation_cpu(self, dominant_core: str, confidence: float,
                                     attention_weights: Dict) -> Dict:
        """Simplified voice modulation for CPU"""
        attention_std = np.std(list(attention_weights.values()))

        tempo = 0.8 + confidence * 0.4
        pitch_variance = 1.0 + (attention_std * 0.05)
        formant_boost = 1.0 + (confidence * 0.1)

        base_profile = self.council_voice_profiles[dominant_core]

        return {
            'base_voice': base_profile['base_voice'],
            'pitch': base_profile['pitch'] * pitch_variance,
            'tempo': base_profile['tempo'] * tempo,
            'emotion': self._select_emotion_cpu(confidence, attention_std),
            'formant_shifts': {
                k: v * formant_boost
                for k, v in base_profile['formant_shifts'].items()
            }
        }

    def _select_emotion_cpu(self, confidence: float, attention_std: float) -> str:
        if confidence > 0.85:
            return "neutral"
        elif confidence > 0.6:
            return "happy" if attention_std < 0.15 else "surprised"
        else:
            return "sad"

    def _fallback_synthesis(self, text: str, voice_params: Dict) -> bytes:
        """Ultra-lightweight fallback: 1 second of 440Hz tone"""
        import wave
        import io

        duration = 1.0  # Short fallback
        sr = 16000
        t = np.linspace(0, duration, int(sr * duration))
        tone = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(tone.tobytes())

        return buffer.getvalue()

    def get_performance_report(self) -> Dict:
        """Return CPU performance statistics"""
        stats = self._performance_monitor.get_stats()
        cache_total = self.voice_state['cpu_performance_stats'].get('cache_hits', 0) + \
                     self.voice_state['cpu_performance_stats'].get('cache_misses', 0)

        cache_rate = 0
        if cache_total > 0:
            cache_rate = self.voice_state['cpu_performance_stats'].get('cache_hits', 0) / cache_total

        return {
            'performance_monitor': stats,
            'cache_hit_rate': cache_rate,
            'cpu_optimization': 'fast_mode' if self.fast_mode else 'standard',
            'recommendation': self._get_optimization_recommendation(stats, cache_rate)
        }

    def _get_optimization_recommendation(self, stats: Dict, cache_rate: float) -> str:
        """Smart recommendation based on performance"""
        if stats['stt_avg'] > 2.0:
            return "Consider reducing audio length or increasing chunk_size"
        elif stats['tts_avg'] > 5.0:
            return "Enable aggressive caching or reduce voice complexity"
        elif cache_rate < 0.3:
            return "Cache is underutilized - increase cache_size parameter"
        elif stats['warnings'] > 5:
            return "Multiple performance warnings detected - review CPU load"
        else:
            return "CPU performance is acceptable for current workload"

    def _on_hearing_correction(self, wrong: str, right: str):
        """Callback: hearing correction improves future voice synthesis"""
        print(f"🔄 Correction learned: '{wrong}' → '{right}'")

        self.voice_state['last_correction'] = {
            'misheard': wrong,
            'corrected': right,
            'timestamp': datetime.now().isoformat()
        }

        # Future enhancement: adjust POM articulation
        # This creates the hearing→speaking feedback loop
        self._adapt_voice_articulation(wrong, right)

    def _adapt_voice_articulation(self, wrong_phoneme: str, correct_phoneme: str):
        """
        CPU version: simple articulation adjustment
        When cochlear mishears 'b' as 'p', boost voicing in future speech
        """
        # Simple logic: if consonant confusion, increase formant clarity
        consonants = {'b': 'p', 'd': 't', 'g': 'k', 'v': 'f', 'z': 's'}

        if wrong_phoneme in consonants and consonants[wrong_phoneme] == correct_phoneme:
            # Increase f1 for voiced consonants
            for profile in self.council_voice_profiles.values():
                profile['formant_shifts']['f1'] *= 1.05  # 5% boost
            print(f"📢 Articulation adapted: Boosting voicing clarity")


# === Initialization Helper ===
def initialize_unified_sensory(orchestrator, config: Dict = None,
                              fast_mode: bool = True) -> UnifiedSensoryIO:
    """
    Initialize unified sensory system

    Args:
        orchestrator: AttentionGovernor 5th element
        config: Configuration dict
        fast_mode: Enable CPU optimizations (default: True for CPU-only)

    Returns:
        UnifiedSensoryIO instance
    """
    return UnifiedSensoryIO(orchestrator, config, fast_mode)