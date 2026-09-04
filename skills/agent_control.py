from typing import Any


def start(_parameters: dict[str, Any]) -> str:
    return "I am already running and listening."


def stop(_parameters: dict[str, Any]) -> str:
    return "Stopping now. Goodbye."