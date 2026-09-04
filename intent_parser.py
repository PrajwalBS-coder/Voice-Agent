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
        rules = [
            (any(phrase in transcript for phrase in ("take a picture", "take a photo", "capture")), Intent("take_picture", {})),
            (any(phrase in transcript for phrase in ("take a screenshot", "screenshot", "screen capture")), Intent("take_screenshot", {})),
            (any(phrase in transcript for phrase in ("what time", "tell me the time", "current time")), Intent("tell_time", {})),
            (any(phrase in transcript for phrase in ("tell me a joke", "give me a joke", "make me laugh", "say a joke")), Intent("tell_joke", {})),
            (any(phrase in transcript for phrase in ("tell me about you", "who are you", "what are you")), Intent("about_me", {})),
            (transcript in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}, Intent("greeting", {})),
            (transcript in {"thank you", "thanks", "thank you jarvis", "thanks jarvis"}, Intent("thanks", {})),
            (any(phrase in transcript for phrase in ("change your voice", "change the voice", "how can i change your voice", "voice settings")), Intent("voice_help", {})),
            (any(word in transcript for word in ("change", "edit", "modify", "update", "add", "remove", "fix")) and "code" in transcript, Intent("code_change", {"request": transcript})),
            (any(word in transcript for word in ("document", "report", "guide", "notes")) and any(word in transcript for word in ("create", "make", "give", "write", "generate")), Intent("create_document", {"topic": transcript})),
            ("ai tools" in transcript or "artificial intelligence tools" in transcript, Intent("ai_tools", {})),
            (any(phrase in transcript for phrase in ("improve yourself", "improve jarvis", "research improvements", "research public github", "learn from github")), Intent("self_improvement", {"request": transcript})),
            (transcript in {"start", "start jarvis", "wake up", "begin listening"}, Intent("start_agent", {})),
            (any(phrase in transcript for phrase in ("stop", "stop jarvis", "stop working", "stop working now", "go to sleep", "shut down")), Intent("stop_agent", {})),
            (transcript.startswith(("open video ", "play video ")), Intent("open_video", {"name": transcript.split(" ", 2)[-1]})),
            (transcript.startswith(("open app ", "launch ", "open ")), Intent("open_app", {"name": transcript.split(" ", 1)[-1]})),
        ]
        return next((intent for matches, intent in rules if matches), Intent("search_web", {"query": transcript}))
