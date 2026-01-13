# record_audio.py
"""
Quick audio recording script for testing Core 4
"""

import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import time

def record_audio():
    print("🎙️ AUDIO RECORDER FOR CORE 4 TESTING")
    print("=" * 40)

    try:
        # Check available devices
        devices = sd.query_devices()
        print(f"Available audio devices: {len(devices)}")

        # Recording parameters
        duration = 5  # seconds
        sample_rate = 16000  # 16kHz for speech
        channels = 1  # mono

        print(f"\nRecording parameters:")
        print(f"  Duration: {duration} seconds")
        print(f"  Sample Rate: {sample_rate} Hz")
        print(f"  Channels: {channels} (mono)")

        print(f"\n🎤 Starting recording in 3 seconds...")
        print("💬 Speak clearly: 'Test: Can the council hear and understand my voice?'")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        print("\n🔴 RECORDING NOW - SPEAK!")
        time.sleep(0.5)  # Brief pause

        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='int16'
        )

        # Show recording progress
        for i in range(duration):
            print(f"   Recording... {i+1}/{duration}s")
            time.sleep(1)

        print("⏹️ Recording complete!")
        sd.wait()  # Wait until recording is finished

        # Save to file
        output_file = "query.wav"
        wavfile.write(output_file, sample_rate, audio)

        print(f"\n✅ Audio saved: {output_file}")
        print(f"   File size: {len(audio)} samples")
        print(f"   Duration: {len(audio)/sample_rate:.1f} seconds")

        # Basic audio check
        rms = np.sqrt(np.mean(audio.astype(np.float32)**2))
        print(f"   RMS level: {rms:.1f} (should be > 1000 for good recording)")

        if rms < 500:
            print("⚠️  Warning: Audio level seems low. Speak louder or closer to microphone.")
        elif rms > 15000:
            print("⚠️  Warning: Audio may be clipped (too loud).")

        print(f"\n🎯 Ready to test! Run: python test_real_audio.py")

    except Exception as e:
        print(f"❌ Recording failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure you have a microphone connected")
        print("   2. Check microphone permissions")
        print("   3. Try using your phone to record instead")

if __name__ == "__main__":
    record_audio()