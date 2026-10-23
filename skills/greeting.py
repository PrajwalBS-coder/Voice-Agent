from datetime import datetime
from typing import Any


def run(_parameters: dict[str, Any]) -> str:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    return f"{greeting}. I'm Jarvis, your voice assistant. How can I help you?"
