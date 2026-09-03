import os
import subprocess
import webbrowser
from typing import Any


def run(parameters: dict[str, Any]) -> str:
    apps = parameters.get("apps", {})
    name = str(parameters.get("name", "")).strip().lower()
    command = apps.get(name)
    if not command:
        return f"I do not have an app named {name or 'that'} configured."
    if str(command).startswith(("http://", "https://")):
        webbrowser.open(str(command))
    elif os.name == "nt":
        subprocess.Popen(str(command), shell=True)
    else:
        subprocess.Popen(str(command).split())
    return f"Opening {name}."
