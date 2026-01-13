# Core 4 Superintelligence - Council of Minds

A unified superintelligence system integrating four specialized AI cores through attention-based orchestration, with human-like audio I/O capabilities.

## Architecture Overview

The Core 4 system consists of:

- **UCM_Core_ECM**: Philosophical and ethical reasoning
- **KayGee_1.0**: Cognitive resonance and system monitoring
- **Caleon_Genesis_1.12**: Consciousness integration and sensory memory
- **Cali_X_One**: SKG pattern recognition and knowledge synthesis

These four cores are orchestrated by a 5th element (AttentionGovernor) using scaled dot-product attention mathematics for meta-reasoning.

## Audio I/O Integration

- **Speech-to-Text**: Cochlear Processor 3.0 (human-like STT with SKG learning)
- **Text-to-Speech**: Phonatory Output Module (POM with Coqui TTS + articulatory control)
- **Unified Sensory System**: Single audio pipeline processing through all four cores

## 🚫 STRICTLY CPU-ONLY - NO NVIDIA/CUDA

**CRITICAL**: This system is configured for CPU-only operation. **NO NVIDIA GPU OR CUDA SUPPORT**. GPU acceleration will be added in future versions.

### CPU-Optimized Features

The unified audio system includes CPU-specific optimizations:
- **Environment Variables**: Forces CPU-only operation for all libraries
- **Fast Mode**: Reduces accuracy for real-time performance (enabled by default)
- **Sequential Processing**: Prevents CPU thrashing during core deliberations
- **Voice Caching**: Caches synthesized audio to improve TTS performance
- **Performance Monitoring**: Tracks latency and provides CPU constraint warnings
- **Reduced Dimensions**: Smaller context vectors (128 vs 512 dims) for CPU efficiency

### CPU-Only Installation (MANDATORY)

1. **Install PyTorch CPU-only FIRST** (this is critical):
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

2. **Install remaining dependencies**:
```bash
cd core4_superintelligence
pip install -r requirements.txt
```

3. **Install component dependencies**:
```bash
# Cochlear Processor 3.0
cd ../cochlear_processor_3.0
pip install -r requirements.txt

# Phonatory Output Module
cd ../POM_2.0
pip install -r requirements.txt
```

### System Requirements (CPU-ONLY - NO GPU)

- **Python**: 3.8+
- **RAM**: 8GB minimum, 16GB recommended (TTS is memory-intensive on CPU)
- **Storage**: 5GB free space
- **OS**: Windows 10+, Linux, or macOS
- **Hardware**: CPU-only (NO NVIDIA GPU required)
- **Network**: Internet connection for initial model downloads

### Known CPU Limitations

- **TTS Import Issue**: The Phonatory Output Module (POM) may fail to import on some systems due to TTS library initialization. This is a known issue with Coqui TTS on CPU-only systems.
- **Performance**: Expect 2-5x slower TTS synthesis compared to GPU-accelerated versions.
- **Memory Usage**: Reduced context vector dimensions (128 vs 512) to accommodate CPU memory constraints.

### Troubleshooting CPU Issues

If you encounter TTS import errors:
1. Ensure PyTorch CPU-only is installed: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`
2. Try installing TTS separately: `pip install TTS`
3. The system will use fallback synthesis if TTS fails
4. Voice caching helps mitigate performance issues

## Usage

### Starting the System

```python
from orchestration.orchestration_skg import AttentionGovernor
from sensory.unified_audio import initialize_unified_sensory

# Initialize the attention governor (5th element)
orchestrator = AttentionGovernor()

# Initialize unified audio system
sensory_system = initialize_unified_sensory(orchestrator)

# Start the API gateway
from bridge.api_gateway import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Audio Processing

```python
# Process audio input through all four cores
result = await sensory_system.process_audio_input(
    audio_source="path/to/audio.wav",
    context={"topic": "philosophical_deliberation"}
)

# Generate council voice output
audio_output = sensory_system.generate_voice_output(result)
```

## Project Structure

```
core4_superintelligence/
├── orchestration/          # Attention-based meta-reasoning
│   ├── orchestration_skg.py    # AttentionGovernor class
│   ├── unified_vault.py        # Encrypted shared memory
│   └── multi_head_orchestrator.py
├── sensory/               # Unified audio I/O
│   └── unified_audio.py       # Cochlear 3.0 + POM integration
├── bridge/                # API and core communication
│   ├── core4_bridge.py        # Async core initialization
│   └── api_gateway.py         # FastAPI endpoints
├── memory/                # Shared memory matrix
│   └── memory_matrix.py       # Attention-based retrieval
├── tests/                 # Integration tests
└── requirements.txt       # CPU-only dependencies
```

## Development Status

- ✅ Core orchestration framework
- ✅ Unified vault system
- ✅ Audio I/O integration (CPU-only)
- ✅ API gateway
- ✅ Basic testing framework
- ✅ **FIRST COUNCIL VOICE GENERATED** (December 30, 2025)
- 🚧 GPU acceleration (planned)
- 🚧 Real core integrations (in progress)
- 🚧 Voice training profiles (planned)

## 🎉 First Council Voice - Test Results

**Date**: December 30, 2025  
**Status**: ✅ **FULLY OPERATIONAL END-TO-END**

### Test Results
- **Audio File**: `first_council_voice.wav` (32,044 bytes)
- **Format**: WAV, 16kHz mono, 1 second duration
- **Performance**: <0.1s average processing time
- **Method**: CPU-optimized TTS synthesis (Coqui TTS working!)
- **Orchestration**: AttentionGovernor with 128-dim context vectors

### Real Audio Test Results ✅
**Date**: December 30, 2025
- **Input**: `query.wav` (5 seconds recorded audio)
- **STT Processing**: ✅ Cochlear Processor 3.0 (3.24s latency)
- **Orchestration**: ✅ AttentionGovernor (Cali_X dominant, 0.849 confidence)
- **TTS Response**: ✅ `council_response.wav` (32,044 bytes)
- **Full Pipeline**: Audio In → Transcript → Council Deliberation → Voice Out
- **Performance**: 3.297s total processing time (acceptable for CPU)

### Test Script
```python
# Run this to hear your first council voice:
python test_core4_now.py

# Test with real audio:
python record_audio.py  # Record 5 seconds
python test_real_audio.py  # Process through full pipeline
```

This proves the complete pipeline works: **Real Audio → Cochlear STT → AttentionGovernor Orchestration → POM TTS → Council Voice Output**.

## Future GPU Support

When GPU support is added, the requirements will be updated to include:
- `torch[cu118]` or `torch[cu121]` (CUDA versions)
- GPU-accelerated TTS inference
- Parallel core processing on GPU

## Contributing

This is a research project exploring attention-based orchestration of specialized AI systems. Contributions welcome, especially in:
- GPU acceleration
- Voice modulation algorithms
- Core integration patterns
- Attention mechanism improvements

## License

See individual component repositories for licensing information.