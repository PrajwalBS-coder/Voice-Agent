"""Workspace-scoped code editing through a local Ollama model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

EDITABLE_SUFFIXES = {".py", ".yaml", ".yml", ".md"}
MAX_FILE_BYTES = 256 * 1024


class CodeAgent:
    def __init__(self, workspace: str = ".", model: str = "qwen2.5-coder:7b") -> None:
        self.workspace = Path(workspace).resolve()
        self.model = model

    def propose(self, request: str) -> dict[str, Any]:
        files = []
        for path in self.workspace.rglob("*"):
            if (
                path.is_file()
                and not path.is_symlink()
                and path.suffix in EDITABLE_SUFFIXES
                and not {".venv", ".git", "node_modules"}.intersection(path.parts)
                and path.stat().st_size <= MAX_FILE_BYTES
            ):
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
        edits = proposal.get("edits")
        if not isinstance(edits, list):
            raise ValueError("The coding model returned no edits.")

        validated_edits: list[tuple[Path, str]] = []
        for edit in edits:
            if not isinstance(edit, dict) or not isinstance(edit.get("path"), str) or not isinstance(edit.get("content"), str):
                raise ValueError("Each code edit must contain a path and string content.")
            relative_path = Path(edit["path"])
            if relative_path.is_absolute() or relative_path.suffix not in EDITABLE_SUFFIXES:
                raise ValueError(f"Refusing to edit unsupported path: {edit['path']}")
            target = (self.workspace / relative_path).resolve()
            try:
                target.relative_to(self.workspace)
            except ValueError as error:
                raise ValueError(f"Refusing to edit outside workspace: {edit['path']}") from error
            validated_edits.append((target, edit["content"]))

        originals = {target: target.read_bytes() for target, _ in validated_edits if target.exists()}
        try:
            for target, content in validated_edits:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
        except Exception:
            for target, content in originals.items():
                target.write_bytes(content)
            for target, _ in validated_edits:
                if target not in originals and target.exists():
                    target.unlink()
            raise