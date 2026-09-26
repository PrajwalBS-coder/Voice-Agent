import os
import shlex
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
    else:
        arguments = command if isinstance(command, list) else shlex.split(str(command), posix=os.name != "nt")
        if not arguments:
            return f"I do not have an app named {name or 'that'} configured."
        subprocess.Popen([str(argument) for argument in arguments], shell=False)
    return f"Opening {name}."
