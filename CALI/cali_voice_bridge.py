# cali_voice_bridge.py - Connect CALI SKG to POM Phonatory Output
from cali_skg import CALISKGEngine
from pom_engine import POMEngine
from pathlib import Path
from typing import Dict, Any

class CALIVoiceBridge:
    """
    Bridge between CALI SKG intelligence and POM phonatory output
    Ensures elegant female voice synthesis
    """

    def __init__(self, cali_skg: CALISKGEngine, pom_engine: POMEngine):
        self.cali = cali_skg
        self.pom = pom_engine

        # CALI-specific voice configuration
        self.cali_voice_profile = {
            "base_model": "tts_models/en/vctk/vits",
            "speaker_id": "p240",  # P240: Elegant female voice
            "language": "en",
            "phoneme_language": "en-us",
            "base_pitch": 220,  # A3 - elegant female pitch
            "base_speed": 0.95,  # Slightly slower for clarity
            "audio_format": "mp3",
            "bitrate": "192k"
        }

    def generate_cali_speech(self, cali_response: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate elegant female voice from CALI response

        Args:
            cali_response: Full response dict from CALI SKG
            output_path: Where to save audio file

        Returns:
            Path to generated audio file
        """

        voice_params = cali_response["voice_parameters"]
        text = cali_response["text"]

        # Apply CALI voice characteristics
        pitch_adjust = voice_params["pitch_base_hz"] / self.cali_voice_profile["base_pitch"]
        speed_adjust = voice_params["speech_rate_wpm"] / 150  # Normalize to 150 WPM baseline

        # Modulate based on emotional state
        if voice_params["emotional_tone"] == "contemplative_humble":
            pitch_adjust *= 0.98  # Slightly lower
            speed_adjust *= 0.90  # Slightly slower
        elif voice_params["emotional_tone"] == "authoritative_warm":
            pitch_adjust *= 1.02  # Slightly higher
            speed_adjust *= 1.05  # Slightly more confident pace

        # Generate with POM
        audio_file = self.pom.generate_speech(
            text=text,
            voice_profile=self.cali_voice_profile["speaker_id"],
            language=self.cali_voice_profile["language"],
            output_path=output_path,
            pitch_adjust=pitch_adjust,
            speed_adjust=speed_adjust
        )

        self.cali.logger.info(f"CALI Voice Generated: {output_path.name}")

        return audio_file

    def generate_announcement(self, event_type: str, event_data: Dict, output_path: Path) -> Path:
        """
        Generate CALI system announcements with appropriate gravitas

        Args:
            event_type: Type of system event
            event_data: Event details
            output_path: Where to save audio

        Returns:
            Path to announcement audio
        """

        # Get announcement text from CALI
        announcement_text = self.cali.generate_verbal_announcement(event_type, event_data)

        # Use more formal voice parameters for announcements
        announcement_profile = self.cali_voice_profile.copy()
        announcement_profile["speed_adjust"] = 0.90  # Slower for importance
        announcement_profile["pitch_adjust"] = 1.05   # Slightly elevated for clarity

        audio_file = self.pom.generate_speech(
            text=announcement_text,
            voice_profile=announcement_profile["speaker_id"],
            output_path=output_path,
            pitch_adjust=announcement_profile["pitch_adjust"],
            speed_adjust=announcement_profile["speed_adjust"]
        )

        return audio_file