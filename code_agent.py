"""Workspace-scoped code editing through a local Ollama model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


class CodeAgent:
    def __init__(self, workspace: str = ".", model: str = "qwen2.5-coder:7b") -> None:
        self.workspace = Path(workspace).resolve()
        self.model = model

    def propose(self, request: str) -> dict[str, Any]:
        files = []
        for path in self.workspace.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".md"} and ".venv" not in path.parts:
                files.append(f"\n--- {path.relative_to(self.workspace)} ---\n{path.read_text(encoding='utf-8')}")
        prompt = (
            "You are a careful coding assistant. Modify only files inside the supplied workspace. "
            "Return JSON only: {\"summary\": string, \"edits\": [{\"path\": string, \"content\": string}]}. "
            "Include complete replacement content for each changed file. Do not invent files unless needed.\n\n"
            f"USER REQUEST:\n{request}\n\nWORKSPACE FILES:{''.join(files)}"
        )
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        response = urlopen(
            Request("http://127.0.0.1:11434/api/generate", data=body, headers={"Content-Type": "application/json"}),
            timeout=120,
        )
        result = json.loads(response.read().decode("utf-8"))
        answer = result.get("response", "").strip().strip("`")
        if answer.startswith("json"):
            answer = answer[4:].strip()
        proposal = json.loads(answer)
        if not isinstance(proposal.get("edits"), list):
            raise ValueError("The coding model returned no edits.")
        return proposal

    def apply(self, proposal: dict[str, Any]) -> None:
        for edit in proposal["edits"]:
            target = (self.workspace / edit["path"]).resolve()
            if self.workspace not in target.parents:
                raise ValueError(f"Refusing to edit outside workspace: {edit['path']}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(edit["content"], encoding="utf-8")