"""Configuration loading for Jarvis."""

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "media": {"videos": {}, "pictures_dir": "pictures"},
    "apps": {},
    "llm": {"provider": "auto", "model": "gemini-3.8-flash", "api_key_env": ""},
    "voice": {
        "stt_model": "base.en",
        "stt_language": "en",
        "stt_beam_size": 5,
        "stt_vad_filter": False,
        "tts_enabled": False,
        "tts_voice": "Charon",
    },
    "database": {"url": "sqlite:///data/jarvis-memory.db"},
    "memory": {"enabled": True, "recent_turns": 6},
    "audio": {
        "input_dir": "audio/input",
        "output_dir": "audio/output",
        "vad_enabled": False,
        "vad_threshold": 0.5,
        "silence_seconds": 1.5,
        "threshold": 0.008,
        "pre_roll_seconds": 0.5,
        "min_speech_seconds": 0.25,
    },
}


def load_config(path: str = "config.yaml") -> dict[str, Any]:
    config = DEFAULT_CONFIG.copy()
    config_path = Path(path)
    if config_path.exists():
        with config_path.open(encoding="utf-8") as file:
            loaded = yaml.safe_load(file) or {}
        for section, values in loaded.items():
            if isinstance(values, dict) and isinstance(config.get(section), dict):
                config[section] = {**config[section], **values}
            else:
                config[section] = values
    return config
