"""Configuration loading for Jarvis."""

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "media": {"videos": {}, "pictures_dir": "pictures"},
    "apps": {},
    "llm": {"model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY"},
    "voice": {"stt_model": "base.en", "tts_enabled": False},
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
