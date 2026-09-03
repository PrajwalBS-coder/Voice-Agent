from datetime import datetime
from pathlib import Path
from typing import Any


def run(parameters: dict[str, Any]) -> str:
    import cv2

    output_dir = Path(parameters.get("pictures_dir", "pictures")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"jarvis-{datetime.now():%Y%m%d-%H%M%S}.jpg"
    camera = cv2.VideoCapture(int(parameters.get("camera_index", 0)))
    try:
        if not camera.isOpened():
            return "I could not access the webcam."
        success, frame = camera.read()
        if not success or not cv2.imwrite(str(output_path), frame):
            return "I could not save the picture."
    finally:
        camera.release()
    return f"Picture saved to {output_path}."
