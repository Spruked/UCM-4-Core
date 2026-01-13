# test_core4_now.py
import asyncio
import sys
import os
import time

# Add paths
sys.path.insert(0, '.')

from orchestration.orchestration_skg import AttentionGovernor
from sensory.unified_audio import initialize_unified_sensory

async def main():
    print("🧠 Starting Core 4 Council (CPU Mode)...")

    # Initialize
    orchestrator = AttentionGovernor(dim=128)
    sensory = initialize_unified_sensory(orchestrator, fast_mode=True)

    # Test with dummy audio
    print("\n📢 Testing council voice...")

    # Create a mock orchestration (simulating 4 cores deliberating)
    mock_orchestration = {
        'unified_verdict': 'This is a test of the Core 4 council voice system.',
        'dominant_core': 'ucm_core',
        'confidence_score': 0.85,
        'attention_weights': {'ucm_core': 0.4, 'kaygee': 0.3, 'caleon': 0.2, 'cali_x': 0.1},
        'council_recommendation': 'The council recommends proceeding with testing.'
    }

    # Generate audio
    audio = sensory.generate_voice_output(mock_orchestration)

    # Save it (handle file conflicts)
    output_file = "first_council_voice.wav"
    try:
        # Remove existing file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, "wb") as f:
            f.write(audio)
        print(f"✅ SUCCESS! Audio saved to: {output_file}")
    except PermissionError:
        # Try with a different filename
        output_file = f"council_voice_{int(time.time())}.wav"
        with open(output_file, "wb") as f:
            f.write(audio)
        print(f"✅ SUCCESS! Audio saved to: {output_file} (used timestamp to avoid conflicts)")
    
    report = sensory.get_performance_report()
    print(f"\n📊 Performance: {report['performance_monitor']['total_avg']:.3f}s avg")

if __name__ == "__main__":
    asyncio.run(main())