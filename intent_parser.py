"""Convert natural-language transcripts into validated Jarvis intents."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from skill_registry import available_actions


@dataclass(frozen=True)
class Intent:
    action: str
    parameters: dict[str, Any]


def validate_intent(value: dict[str, Any]) -> Intent:
    action = value.get("action", "unknown")
    if action not in available_actions():
        action = "unknown"
    parameters = value.get("parameters", {})
    if not isinstance(parameters, dict):
        parameters = {}
    return Intent(action, parameters)


class IntentParser:
    """Use OpenAI when configured, with a deterministic local fallback."""

    def __init__(self, model: str = "gpt-4o-mini", api_key_env: str = "OPENAI_API_KEY") -> None:
        self.model = model
        self.api_key = os.getenv(api_key_env)

    def parse(self, transcript: str) -> Intent:
        transcript = transcript.strip()
        if not transcript:
            return Intent("unknown", {})
        if self.api_key:
            return self._parse_with_openai(transcript)
        return self._parse_locally(transcript.lower())

    def _parse_with_openai(self, transcript: str) -> Intent:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only JSON with action and parameters. Valid actions are: "
                        f"{', '.join(sorted(available_actions()))}. "
                        "Use name for open_video/open_app and no parameters for other actions."
                    ),
                },
                {"role": "user", "content": transcript},
            ],
        )
        content = response.choices[0].message.content or "{}"
        try:
            return validate_intent(json.loads(content))
        except (json.JSONDecodeError, TypeError):
            return Intent("unknown", {})

    @staticmethod
    def _parse_locally(transcript: str) -> Intent:
        if any(phrase in transcript for phrase in ("take a picture", "take a photo", "capture")):
            return Intent("take_picture", {})
        if any(phrase in transcript for phrase in ("take a screenshot", "screenshot", "screen capture")):
            return Intent("take_screenshot", {})
        if any(phrase in transcript for phrase in ("what time", "tell me the time", "current time")):
            return Intent("tell_time", {})
        if any(phrase in transcript for phrase in ("tell me a joke", "give me a joke", "make me laugh", "say a joke")):
            return Intent("tell_joke", {})
        if any(phrase in transcript for phrase in ("tell me about you", "who are you", "what are you")):
            return Intent("about_me", {})
        if transcript in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
            return Intent("greeting", {})
        if transcript in {"thank you", "thanks", "thank you jarvis", "thanks jarvis"}:
            return Intent("thanks", {})
        if any(phrase in transcript for phrase in ("change your voice", "change the voice", "how can i change your voice", "voice settings")):
            return Intent("voice_help", {})
        edit_words = ("change", "edit", "modify", "update", "add", "remove", "fix")
        if any(word in transcript for word in edit_words) and "code" in transcript:
            return Intent("code_change", {"request": transcript})
        document_words = ("document", "report", "guide", "notes")
        if any(word in transcript for word in document_words) and any(word in transcript for word in ("create", "make", "give", "write", "generate")):
            return Intent("create_document", {"topic": transcript})
        if "ai tools" in transcript or "artificial intelligence tools" in transcript:
            return Intent("ai_tools", {})
        if transcript.startswith(("open video ", "play video ")):
            return Intent("open_video", {"name": transcript.split(" ", 2)[-1]})
        if transcript.startswith(("open app ", "launch ", "open ")):
            return Intent("open_app", {"name": transcript.split(" ", 1)[-1]})
        return Intent("search_web", {"query": transcript})
