from config import load_config


def test_audio_defaults_keep_vad_opt_in():
    config = load_config("does-not-exist.yaml")

    assert config["audio"]["vad_enabled"] is False
    assert config["audio"]["vad_threshold"] == 0.5
