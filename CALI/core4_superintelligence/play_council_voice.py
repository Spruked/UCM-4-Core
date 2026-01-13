# play_council_voice.py
"""
Play the first council voice output
"""

from pydub import AudioSegment
from pydub.playback import play

def play_council_voice():
    print("🎵 Playing Core 4 Council Voice...")

    try:
        # Load the audio file
        audio = AudioSegment.from_wav("first_council_voice.wav")

        print(f"Audio duration: {len(audio)}ms")
        print(f"Sample rate: {audio.frame_rate}Hz")
        print(f"Channels: {audio.channels}")

        # Play the audio
        print("🔊 Playing now...")
        play(audio)

        print("✅ Council voice playback completed!")

    except Exception as e:
        print(f"❌ Error playing audio: {e}")
        print("Try opening first_council_voice.wav with your media player")

if __name__ == "__main__":
    play_council_voice()