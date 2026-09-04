"""Backend application settings."""

from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
