"""Optional offline text-to-speech adapter."""


def speak(
    text: str,
    enabled: bool = False,
    voice_name: str = "David",
    rate: int = 155,
    volume: float = 1.0,
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
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.say(text)
    engine.runAndWait()
