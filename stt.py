"""Optional local speech-to-text adapter."""

from pathlib import Path
from collections import Counter


class SpeechToText:
    def __init__(
        self,
        model_name: str = "base.en",
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = False,
    ) -> None:
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter

    def transcribe(self, audio_path: str | Path) -> str:
        segments, _ = self.model.transcribe(
            str(audio_path),
            language=self.language or None,
            beam_size=self.beam_size,
            temperature=0,
            condition_on_previous_text=False,
            vad_filter=self.vad_filter,
        )
        accepted_segments = []
        rejected_segments = 0
        for segment in segments:
            text = segment.text.strip()
            if not text:
                continue
            if getattr(segment, "no_speech_prob", 0.0) >= 0.65:
                rejected_segments += 1
                continue
            if getattr(segment, "avg_logprob", 0.0) <= -1.0:
                rejected_segments += 1
                continue
            if getattr(segment, "compression_ratio", 0.0) > 2.4:
                rejected_segments += 1
                continue
            accepted_segments.append(text)

        transcript = " ".join(accepted_segments).strip()
        if not transcript and rejected_segments:
            print("Speech was too unclear to trust. Move closer to the active microphone and try again.")
        words = [word.strip(".,!?;:").casefold() for word in transcript.split()]
        if len(words) >= 6:
            repeated_word, repeated_count = Counter(words).most_common(1)[0]
            if repeated_count / len(words) >= 0.7:
                print(f"Ignored likely silence hallucination from speech recognition: repeated '{repeated_word}'.")
                return ""
        return transcript
