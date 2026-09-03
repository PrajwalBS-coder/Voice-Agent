"""Microphone recording adapter."""

from pathlib import Path


def record_audio_until_silence(
    output_path: str | Path,
    max_duration: int = 15,
    sample_rate: int = 16_000,
    silence_seconds: float = 1.2,
    threshold: float = 0.015,
) -> Path:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    block_size = 1600
    blocks = []
    speech_started = False
    silent_blocks = 0
    required_silent_blocks = max(1, int(silence_seconds * sample_rate / block_size))
    maximum_blocks = int(max_duration * sample_rate / block_size)
    print("Listening...")
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32", blocksize=block_size) as stream:
        for _ in range(maximum_blocks):
            block, _ = stream.read(block_size)
            block = np.asarray(block).copy()
            blocks.append(block)
            is_loud = float(np.sqrt(np.mean(block**2))) >= threshold
            if is_loud:
                speech_started = True
                silent_blocks = 0
            elif speech_started:
                silent_blocks += 1
                if silent_blocks >= required_silent_blocks:
                    break
    recording = np.concatenate(blocks, axis=0) if blocks else np.zeros((1, 1), dtype="float32")
    sf.write(path, recording, sample_rate)
    return path