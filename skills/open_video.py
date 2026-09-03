import os
import subprocess
from pathlib import Path
from typing import Any


def run(parameters: dict[str, Any]) -> str:
    videos = parameters.get("videos", {})
    name = str(parameters.get("name", "")).strip().lower()
    path = videos.get(name)
    if not path:
        return f"I could not find a video named {name or 'that'}."
    video_path = Path(path).expanduser()
    if not video_path.exists():
        return f"The video path does not exist: {video_path}"
    if os.name == "nt":
        os.startfile(video_path)  # type: ignore[attr-defined]
    elif os.name == "posix":
        subprocess.Popen(["open" if os.uname().sysname == "Darwin" else "xdg-open", str(video_path)])
    return f"Opening {name}."
