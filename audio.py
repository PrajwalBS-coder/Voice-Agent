"""Microphone recording with optional local voice-activity detection."""

from collections import deque
from pathlib import Path


class NoSpeechDetected(RuntimeError):
    """Raised when the selected microphone captured no usable speech."""


class _RmsSpeechDetector:
    """Compatibility detector used when neural VAD is disabled."""

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def is_speech(self, block, sample_rate: int) -> bool:
        import numpy as np

        del sample_rate
        return float(np.sqrt(np.mean(block**2))) >= self.threshold


class _SileroSpeechDetector:
    """Small wrapper that keeps the optional Silero dependency isolated."""

    def __init__(self, threshold: float) -> None:
        try:
            from silero_vad import load_silero_vad
            import torch
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Silero VAD is enabled but unavailable. Install requirements.txt "
                "or set audio.vad_enabled to false."
            ) from error
        self._model = load_silero_vad()
        self._torch = torch
        self.threshold = threshold

    def is_speech(self, block, sample_rate: int) -> bool:
        samples = self._torch.from_numpy(block.reshape(-1)).to(self._torch.float32)
        probability = float(self._model(samples, sample_rate).item())
        return probability >= self.threshold


def record_audio_until_silence(
    output_path: str | Path,
    max_duration: int = 15,
    sample_rate: int = 16_000,
    silence_seconds: float = 1.2,
    threshold: float = 0.015,
    vad_enabled: bool = False,
    vad_threshold: float = 0.5,
    pre_roll_seconds: float = 0.3,
    min_speech_seconds: float = 0.25,
) -> Path:
    """Record one utterance, ending after sustained silence.

    The legacy RMS detector remains the default. When ``vad_enabled`` is true,
    Silero VAD classifies 32 ms frames instead; this is more reliable for quiet
    speech and varied background noise.
    """
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Silero's 16 kHz model expects 512 samples per inference frame.
    block_size = 512 if vad_enabled else 1600
    blocks = []
    pre_roll = deque(maxlen=max(1, round(pre_roll_seconds * sample_rate / block_size)))
    speech_started = False
    silent_blocks = 0
    required_silent_blocks = max(1, int(silence_seconds * sample_rate / block_size))
    maximum_blocks = int(max_duration * sample_rate / block_size)
    detector = _SileroSpeechDetector(vad_threshold) if vad_enabled else _RmsSpeechDetector(threshold)
    try:
        device_index = sd.default.device[0]
        device = sd.query_devices(device_index, "input")
        device_name = device.get("name", "default microphone")
    except Exception:
        device_index = "default"
        device_name = "system default microphone"
    print(f"Listening on input {device_index}: {device_name}. Speak now; recording stops after silence.")
    speech_blocks = 0
    required_speech_blocks = max(1, int(min_speech_seconds * sample_rate / block_size))
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32", blocksize=block_size) as stream:
        for _ in range(maximum_blocks):
            block, _ = stream.read(block_size)
            block = np.asarray(block).copy()
            is_speech = detector.is_speech(block, sample_rate)
            if not speech_started:
                pre_roll.append(block)
                if is_speech:
                    blocks.extend(pre_roll)
                    speech_started = True
                    silent_blocks = 0
                    speech_blocks = 1
            else:
                blocks.append(block)
                if is_speech:
                    silent_blocks = 0
                    speech_blocks += 1
                else:
                    silent_blocks += 1
                    if silent_blocks >= required_silent_blocks:
                        break
    if not speech_started or speech_blocks < required_speech_blocks:
        raise NoSpeechDetected(
            f"No speech detected from {device_name}. Check the selected input device, microphone permission, and input level."
        )
    recording = np.concatenate(blocks, axis=0)
    sf.write(path, recording, sample_rate)
    print(f"Captured {len(recording) / sample_rate:.1f}s from input {device_index} to {path}.")
    return path
