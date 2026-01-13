# analyze_council_voice.py
"""
Analyze the council voice audio content
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import scipy.signal as signal

def analyze_council_voice():
    print("🔍 Analyzing Core 4 Council Voice...")

    try:
        # Read the audio file
        sample_rate, audio_data = wavfile.read("first_council_voice.wav")

        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Duration: {len(audio_data) / sample_rate:.2f} seconds")
        print(f"Samples: {len(audio_data)}")
        print(f"Data Type: {audio_data.dtype}")
        print(f"Value Range: {audio_data.min()} to {audio_data.max()}")

        # Convert to float for analysis
        if audio_data.dtype == np.int16:
            audio_float = audio_data.astype(np.float32) / 32768.0
        else:
            audio_float = audio_data.astype(np.float32)

        # Basic analysis
        rms = np.sqrt(np.mean(audio_float**2))
        print(f"RMS Amplitude: {rms:.4f}")

        # Frequency analysis
        if len(audio_float) > 0:
            # Compute FFT
            fft = np.fft.fft(audio_float)
            freqs = np.fft.fftfreq(len(audio_float), 1/sample_rate)

            # Get magnitude spectrum (positive frequencies only)
            magnitude = np.abs(fft[:len(fft)//2])
            freqs_pos = freqs[:len(freqs)//2]

            # Find dominant frequency
            peak_idx = np.argmax(magnitude)
            dominant_freq = freqs_pos[peak_idx]
            print(f"Dominant Frequency: {dominant_freq:.1f} Hz")

            # Check if it's a pure tone (fallback synthesis)
            if 435 < dominant_freq < 445:  # Around 440Hz
                print("🎵 This is the fallback synthesis: A simple 440Hz tone")
                print("   (TTS is unavailable due to dependency conflicts)")
            else:
                print("🎤 This appears to be actual speech synthesis!")

        # Plot the waveform
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(np.arange(len(audio_float)) / sample_rate, audio_float)
        plt.title("Council Voice Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(freqs_pos, magnitude)
        plt.title("Frequency Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.xlim(0, 2000)  # Focus on speech frequencies
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("council_voice_analysis.png", dpi=150, bbox_inches='tight')
        print("📊 Analysis plot saved as: council_voice_analysis.png")

        plt.show()

    except Exception as e:
        print(f"❌ Error analyzing audio: {e}")

if __name__ == "__main__":
    analyze_council_voice()