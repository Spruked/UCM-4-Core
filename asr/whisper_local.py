from faster_whisper import WhisperModel


class WhisperASR:
    def __init__(self, model_name="large-v3"):
        self.model = WhisperModel(model_name)

    def transcribe(self, audio: bytes, sample_rate: int):
        segments, _ = self.model.transcribe(audio)
        text = " ".join(seg.text for seg in segments).strip()
        if not text:
            raise RuntimeError("ASR produced empty transcription")
        return {
            "source": "whisper_local",
            "content": text
        }


def build_asr():
    return WhisperASR()
