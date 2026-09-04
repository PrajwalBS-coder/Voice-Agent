"""Research public repositories and write a reviewed improvement proposal."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

USER_AGENT = "Jarvis-lite/1.0"
SEARCH_TERMS = {
    "voice": "python voice activity detection speech assistant",
    "wake word": "python wake word detection open source",
    "tts": "python local text to speech voice assistant",
    "stt": "python faster whisper speech to text",
    "ui": "svelte fastapi voice assistant dashboard",
    "memory": "python postgres conversation memory assistant",
}


def _get_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT})
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8", errors="ignore"))


def _search_repositories(term: str) -> list[dict[str, Any]]:
    data = _get_json(f"https://api.github.com/search/repositories?q={quote_plus(term)}&sort=stars&order=desc&per_page=5")
    results = []
    for item in data.get("items", []):
        license_info = item.get("license") or {}
        results.append({
            "name": item.get("full_name", "unknown"),
            "url": item.get("html_url", ""),
            "description": item.get("description") or "No description provided.",
            "stars": item.get("stargazers_count", 0),
            "license": license_info.get("spdx_id") or license_info.get("name") or "License not detected",
            "updated": item.get("updated_at", "unknown"),
        })
    return results


def _topic_for_request(request: str) -> tuple[str, str]:
    lowered = request.lower()
    for topic, term in SEARCH_TERMS.items():
        if topic in lowered:
            return topic, term
    return "voice agent", "python voice assistant open source"


def run(parameters: dict[str, Any]) -> str:
    request = str(parameters.get("request", "")).strip() or "research improvements for yourself"
    topic, search_term = _topic_for_request(request)
    try:
        repositories = _search_repositories(search_term)
    except Exception as error:
        return f"I could not research public repositories right now: {error}"
    if not repositories:
        return f"I found no public repositories for {topic}."

    output_dir = Path(parameters.get("reports_dir", "documents/research")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"jarvis-improvement-{datetime.now():%Y%m%d-%H%M%S}.md"
    lines = [
        "# Jarvis Improvement Proposal",
        "",
        f"Request: {request}",
        f"Research topic: {topic}",
        "",
        "This report contains repository metadata and links only. No source code was copied or executed.",
        "",
        "## Candidate repositories",
        "",
    ]
    for index, repository in enumerate(repositories, 1):
        lines.extend([
            f"### {index}. {repository['name']}",
            f"- URL: {repository['url']}",
            f"- Description: {repository['description']}",
            f"- Stars: {repository['stars']}",
            f"- License: {repository['license']}",
            f"- Last updated: {repository['updated']}",
            "",
        ])
    lines.extend([
        "## Review checklist",
        "",
        "- Confirm the repository license is compatible before using any code.",
        "- Review dependencies and security history before installing anything.",
        "- Prefer adapting ideas over copying implementation code.",
        "- Create a patch and run tests only after explicit confirmation.",
        "",
        "## Next step",
        "",
        "Say `review this proposal` after reading the report. Jarvis will not modify files from research alone.",
    ])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f"I researched public GitHub repositories for {topic} and created a review report at {output_path}."
