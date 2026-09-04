"""Optional offline text-to-speech adapter."""

from pathlib import Path

EMOTION_PROFILES = {
    "calm": {"rate": 145, "volume": 0.95},
    "happy": {"rate": 175, "volume": 1.0},
    "urgent": {"rate": 190, "volume": 1.0},
    "empathetic": {"rate": 135, "volume": 0.9},
}


def speak(
    text: str,
    enabled: bool = False,
    voice_name: str = "David",
    rate: int = 155,
    volume: float = 1.0,
    emotion: str = "calm",
    output_path: str | Path = "audio/output/jarvis-response.wav",
) -> Path | None:
    if not enabled:
        return None
    try:
        import pyttsx3
    except ModuleNotFoundError:
        print("TTS is unavailable; install requirements.txt to enable spoken replies.")
        return None

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
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine.say(text)
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    engine = None
    return output_path
