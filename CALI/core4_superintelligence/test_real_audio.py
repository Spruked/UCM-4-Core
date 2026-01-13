# test_real_audio.py
import asyncio
import sys
import os
import pytest
sys.path.insert(0, '.')

from orchestration.orchestration_skg import AttentionGovernor
from sensory.unified_audio import initialize_unified_sensory

@pytest.mark.asyncio
async def test_real_hearing():
    """Test the full pipeline with a real audio file"""

    print("🎤 TESTING REAL AUDIO INPUT")
    print("=" * 50)

    # Initialize
    orchestrator = AttentionGovernor(dim=128)
    sensory = initialize_unified_sensory(orchestrator, fast_mode=True)

    # === STEP 1: Provide a real audio file ===
    # Option A: Record yourself saying: "Is artificial intelligence truly conscious?"
    # Save as: query.wav in the same directory

    # Option B: Use this Python script to record 5 seconds of audio
    # (Requires: pip install sounddevice scipy)

    """
    import sounddevice as sd
    import scipy.io.wavfile as wavfile

    print("\n🎙️  Recording in 3 seconds... speak now!")
    await asyncio.sleep(3)

    duration = 5  # seconds
    sr = 16000
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    wavfile.write('query.wav', sr, audio)
    print("✅ Recording saved: query.wav")
    """

    # For now, assume you have query.wav:
    audio_path = "./query.wav"

    if not os.path.exists(audio_path):
        print("❌ No query.wav found. Please record audio first.")
        print("💡 Tip: Use your phone's voice recorder, save as WAV, transfer to this folder")
        print("\n🔧 Quick recording option:")
        print("pip install sounddevice scipy")
        print("Then run this in terminal:")
        print('python -c "import sounddevice as sd; import scipy.io.wavfile as wf; print(\'Recording in 2s...\'); import time; time.sleep(2); audio=sd.rec(int(5*16000), samplerate=16000, channels=1, dtype=\'int16\'); sd.wait(); wf.write(\'query.wav\', 16000, audio); print(\'Saved: query.wav\')"')
        return

    print(f"\n📢 Processing: {audio_path}")

    # === STEP 2: Process through unified system ===
    orchestration = await sensory.process_audio_input(
        audio_source=audio_path,
        context={
            "topic": "consciousness",
            "environment": "direct_query",
            "urgency": "moderate"
        },
        speaker_id="user_test"
    )

    # === STEP 3: Review results ===
    print("\n" + "=" * 50)
    print("🏛️ COUNCIL DELIBERATION RESULT")
    print("=" * 50)

    print(f"\n📝 Transcript: '{orchestration['unified_verdict']}'")
    print(f"🎯 Dominant Core: {orchestration['dominant_core'].upper()}")
    print(f"📊 Confidence: {orchestration['confidence_score']:.3f}")

    print("\n⚖️ Attention Weights:")
    for core, weight in orchestration['attention_weights'].items():
        print(f"   {core:12s}: {weight:.3f} {'█' * int(weight * 20)}")

    print(f"\n💬 Council says: {orchestration['council_recommendation']}")

    # === STEP 4: Generate voice response ===
    print("\n🎙️ Generating council voice response...")
    audio_response = sensory.generate_voice_output(orchestration)

    with open("./council_response.wav", "wb") as f:
        f.write(audio_response)

    print(f"✅ Response saved: council_response.wav ({len(audio_response)} bytes)")

    # === STEP 5: Performance check ===
    report = sensory.get_performance_report()
    print(f"\n⚡ Performance: {report['performance_monitor']['total_avg']:.3f}s avg")
    print(f"   Cache hit rate: {report['cache_hit_rate']:.1%}")

    print("\n" + "=" * 50)
    print("✅ REAL AUDIO TEST COMPLETE")
    print("=" * 50)
    print("\n🎯 What to listen for:")
    print("   1. Play query.wav - is your speech clear?")
    print("   2. Play council_response.wav - does it sound like a council speaking?")
    print("   3. Check if transcript matches what you said (accuracy)")
    print("   4. Check if council recommendation makes sense (orchestration)")

    return orchestration

if __name__ == "__main__":
    asyncio.run(test_real_hearing())