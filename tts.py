"""Optional offline text-to-speech adapter."""

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
) -> None:
    if not enabled:
        return
    try:
        import pyttsx3
    except ModuleNotFoundError:
        print("TTS is unavailable; install requirements.txt to enable spoken replies.")
        return

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
    engine.say(text)
    engine.runAndWait()
