import sys
import types

from stt import SpeechToText


def test_transcription_uses_accuracy_settings(monkeypatch, tmp_path):
    calls = {}

    class FakeModel:
        def transcribe(self, path, **kwargs):
            calls["path"] = path
            calls["kwargs"] = kwargs
            return iter([types.SimpleNamespace(text=" hello ")]), None

    fake_module = types.SimpleNamespace(WhisperModel=lambda *args, **kwargs: FakeModel())
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)

    transcriber = SpeechToText("small.en", language="en", beam_size=7, vad_filter=False)
    assert transcriber.transcribe(tmp_path / "command.wav") == "hello"
    assert calls["kwargs"] == {
        "language": "en",
        "beam_size": 7,
        "temperature": 0,
        "condition_on_previous_text": False,
        "vad_filter": False,
    }