"""Capture the current desktop screen."""

from pathlib import Path
from datetime import datetime
from typing import Any


def run(parameters: dict[str, Any]) -> str:
    from PIL import ImageGrab

    output_dir = Path(parameters.get("screenshots_dir", "screenshots")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"jarvis-screen-{datetime.now():%Y%m%d-%H%M%S}.png"
    screenshot = ImageGrab.grab()
    screenshot.save(output_path)
    return f"Screenshot saved to {output_path}."