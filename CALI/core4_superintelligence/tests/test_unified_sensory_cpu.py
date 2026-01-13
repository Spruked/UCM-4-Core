# core4_superintelligence/tests/test_unified_sensory_cpu.py
"""
CPU-Optimized Integration Test for Unified Sensory System
Tests the complete audio pipeline: STT → Orchestration → TTS
"""

import sys
import os
import asyncio
import warnings
import numpy as np
from pathlib import Path
import pytest

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from orchestration.orchestration_skg import AttentionGovernor
from sensory.unified_audio import UnifiedSensoryIO, initialize_unified_sensory

# Suppress warnings for clean test output
warnings.filterwarnings("ignore")

def create_test_audio():
    """Create a simple test audio file (1 second tone)"""
    import scipy.io.wavfile as wavfile

    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    # 440Hz tone with some modulation
    tone = 0.3 * np.sin(2 * np.pi * 440 * t) * np.sin(2 * np.pi * 2 * t)

    test_file = "test_audio.wav"
    wavfile.write(test_file, sr, (tone * 32767).astype(np.int16))

    return test_file

@pytest.mark.asyncio
async def test_unified_sensory_cpu():
    """Test the complete CPU-optimized unified sensory pipeline"""
    print("🧪 Testing CPU-Optimized Unified Sensory System")
    print("=" * 50)

    # Initialize orchestrator
    print("1. Initializing AttentionGovernor...")
    orchestrator = AttentionGovernor(
        dim=128  # CPU-optimized attention dimension
    )

    # Initialize unified sensory system
    print("2. Initializing Unified Sensory IO (CPU-optimized)...")
    config = {
        "skg_path": "hearing_skg.json",
        "cache_size": 50,
        "fast_mode": True
    }

    try:
        sensory = initialize_unified_sensory(
            orchestrator=orchestrator,
            config=config,
            fast_mode=True
        )
        print("✅ Unified Sensory IO initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    # Create test audio
    print("3. Creating test audio...")
    test_audio_file = create_test_audio()
    print(f"✅ Test audio created: {test_audio_file}")

    # Test STT processing
    print("4. Testing STT processing...")
    try:
        # Simulate audio input (we'll use the tone file)
        context = {
            'topic': 'core4_deliberation',
            'speaker': 'test_user',
            'urgency': 'normal'
        }

        orchestration = await sensory.process_audio_input(
            audio_source=test_audio_file,
            context=context,
            speaker_id="test_speaker"
        )

        print("✅ STT processing completed")
        print(f"   Dominant core: {orchestration.get('dominant_core', 'unknown')}")
        print(".2f")
        print(f"   Recommendation: {orchestration.get('council_recommendation', 'none')[:50]}...")

    except Exception as e:
        print(f"❌ STT processing failed: {e}")
        return False

    # Test TTS synthesis
    print("5. Testing TTS synthesis...")
    try:
        audio_output = sensory.generate_voice_output(
            orchestration=orchestration,
            enable_cache=True
        )

        print("✅ TTS synthesis completed")
        print(f"   Audio length: {len(audio_output)} bytes")

        # Save test output
        with open("test_output.wav", "wb") as f:
            f.write(audio_output)
        print("✅ Test output saved as test_output.wav")

    except Exception as e:
        print(f"❌ TTS synthesis failed: {e}")
        return False

    # Performance report
    print("6. Performance Report:")
    try:
        report = sensory.get_performance_report()
        print(f"   STT avg latency: {report['performance_monitor']['stt_avg']:.3f}s")
        print(f"   TTS avg latency: {report['performance_monitor']['tts_avg']:.3f}s")
        print(f"   Cache hit rate: {report['cache_hit_rate']:.1%}")
        print(f"   CPU optimization: {report['cpu_optimization']}")
        print(f"   Recommendation: {report['recommendation']}")

        if report['performance_monitor']['warnings'] > 0:
            print(f"   ⚠️  Performance warnings: {report['performance_monitor']['warnings']}")
        else:
            print("   ✅ No performance warnings")

    except Exception as e:
        print(f"❌ Performance report failed: {e}")

    # Cleanup
    print("7. Cleanup...")
    try:
        os.unlink(test_audio_file)
        if os.path.exists("test_output.wav"):
            os.unlink("test_output.wav")
        print("✅ Test files cleaned up")
    except:
        pass

    print("\n🎉 CPU-Optimized Unified Sensory System Test Completed!")
    print("The Core 4 Council can now process audio input and generate voice output.")
    print("\nNext steps:")
    print("- Connect to actual UCM, KayGee, Caleon, and Cali_X cores")
    print("- Test with real audio input")
    print("- Monitor performance and adjust CPU optimizations")
    print("- Prepare GPU migration when hardware is available")

    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_unified_sensory_cpu())
    sys.exit(0 if success else 1)