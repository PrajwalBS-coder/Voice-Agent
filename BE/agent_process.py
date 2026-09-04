"""Manage the existing Jarvis voice process."""

from __future__ import annotations

import os
import subprocess
import sys
from collections import deque
from pathlib import Path
from threading import Lock, Thread


class AgentProcess:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.process: subprocess.Popen[str] | None = None
        self.logs: deque[str] = deque(maxlen=100)
        self.lock = Lock()

    def start(self, duration: int) -> None:
        with self.lock:
            if self.is_running:
                return
            self.logs.clear()
            self.process = subprocess.Popen(
                [sys.executable, "-u", "main.py", "--voice", "--duration", str(duration)],
                cwd=self.workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )
            Thread(target=self._read_output, daemon=True).start()

    def stop(self) -> None:
        with self.lock:
            if self.process and self.is_running:
                self.process.terminate()

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    @property
    def state(self) -> str:
        if not self.is_running:
            return "stopped"
        recent = self.logs[-1].lower() if self.logs else ""
        if "listening" in recent:
            return "listening"
        if "converting" in recent:
            return "processing"
        if "preparing voice" in recent:
            return "speaking"
        return "starting"

    def snapshot(self) -> dict:
        return {
            "running": self.is_running,
            "state": self.state,
            "pid": self.process.pid if self.is_running and self.process else None,
            "logs": list(self.logs),
        }

    def _read_output(self) -> None:
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            self.logs.append(line.rstrip())
        self.logs.append("Voice agent stopped.")
