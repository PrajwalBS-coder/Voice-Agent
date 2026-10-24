"""Gemini TTS with a local Windows speech fallback."""

from __future__ import annotations

import base64
import os
from pathlib import Path

EMOTION_STYLES = {
    "calm": "calm, clear, natural, conversational",
    "happy": "friendly and upbeat",
    "urgent": "clear, focused, and urgent",
    "empathetic": "warm, gentle, and reassuring",
}

EMOTION_PROFILES = {
    "calm": {"rate": 145, "volume": 0.95},
    "happy": {"rate": 175, "volume": 1.0},
    "urgent": {"rate": 190, "volume": 1.0},
    "empathetic": {"rate": 135, "volume": 0.9},
}


def _play_wav(path: Path) -> None:
    """Play a generated WAV file on the default output device."""
    if os.name == "nt":
        try:
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME)
            return
        except Exception:
            pass

    import sounddevice
    import soundfile

    audio, sample_rate = soundfile.read(str(path), dtype="float32")
    sounddevice.play(audio, sample_rate)
    sounddevice.wait()


def _speak_with_gemini(
    text: str,
    voice_name: str,
    emotion: str,
    output_path: Path,
) -> Path:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    model = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-lite-tts")
    voice = os.getenv("GEMINI_TTS_VOICE", voice_name or "Charon")
    client = genai.Client(api_key=api_key)
    interaction = client.interactions.create(
        model=model,
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": EMOTION_STYLES.get(emotion, EMOTION_STYLES["calm"]),
                }],
            }],
        }],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": voice}]},
    )
    audio_data = interaction.output_audio.data
    if isinstance(audio_data, str):
        audio_data = base64.b64decode(audio_data)
    if not audio_data:
        raise RuntimeError("Gemini returned an empty audio response")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_data)
    _play_wav(output_path)
    return output_path


def _speak_locally(
    text: str,
    voice_name: str,
    rate: int,
    volume: float,
    emotion: str,
    output_path: Path,
) -> Path:
    import pyttsx3

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    matching_voice = next(
        (voice for voice in voices if voice_name.lower() in voice.name.lower()),
        None,
    )
    if matching_voice:
        engine.setProperty("voice", matching_voice.id)
    profile = EMOTION_PROFILES.get(emotion, EMOTION_PROFILES["calm"])
    engine.setProperty("rate", profile.get("rate", rate))
    engine.setProperty("volume", min(1.0, volume * profile.get("volume", 1.0)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine.say(text)
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    engine = None
    return output_path


def speak(
    text: str,
    enabled: bool = False,
    voice_name: str = "Charon",
    rate: int = 155,
    volume: float = 1.0,
    emotion: str = "calm",
    output_path: str | Path = "audio/output/jarvis-response.wav",
) -> Path | None:
    if not enabled:
        return None

    output_path = Path(output_path)
    if os.getenv("GEMINI_API_KEY"):
        try:
            return _speak_with_gemini(text, voice_name, emotion, output_path)
        except Exception as error:
            print(f"Gemini TTS unavailable; using local speech instead: {error}")

    try:
        return _speak_locally(text, voice_name, rate, volume, emotion, output_path)
    except ModuleNotFoundError:
        print("TTS is unavailable; install requirements.txt to enable spoken replies.")
        return None
