import numpy as np

from audio import _RmsSpeechDetector


def test_rms_detector_rejects_silence_and_accepts_speech():
    detector = _RmsSpeechDetector(threshold=0.015)

    assert not detector.is_speech(np.zeros((1600, 1), dtype="float32"), 16_000)
    assert detector.is_speech(np.full((1600, 1), 0.02, dtype="float32"), 16_000)
