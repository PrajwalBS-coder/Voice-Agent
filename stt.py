"""Optional local speech-to-text adapter."""

from pathlib import Path


class SpeechToText:
    def __init__(self, model_name: str = "base.en") -> None:
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str | Path) -> str:
        segments, _ = self.model.transcribe(str(audio_path), vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
