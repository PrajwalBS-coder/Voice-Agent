from datetime import datetime
from typing import Any


def run(_parameters: dict[str, Any]) -> str:
    return f"It is {datetime.now().strftime('%I:%M %p').lstrip('0')}."
