"""Single registry of executable Jarvis skills."""

from collections.abc import Callable
from typing import Any

from skills import about_me, agent_control, ai_tools, create_document, greeting, open_app, open_video, search_web, self_improvement, take_picture, take_screenshot, tell_joke, tell_time, thanks, voice_help

Skill = Callable[[dict[str, Any]], str]

SKILLS: dict[str, Skill] = {
    "take_picture": take_picture.run,
    "take_screenshot": take_screenshot.run,
    "open_video": open_video.run,
    "open_app": open_app.run,
    "tell_time": tell_time.run,
    "tell_joke": tell_joke.run,
    "about_me": about_me.run,
    "greeting": greeting.run,
    "thanks": thanks.run,
    "voice_help": voice_help.run,
    "create_document": create_document.run,
    "ai_tools": ai_tools.run,
    "self_improvement": self_improvement.run,
    "start_agent": agent_control.start,
    "stop_agent": agent_control.stop,
    "search_web": search_web.run,
}

SPECIAL_ACTIONS = {"code_change", "unknown"}


def available_actions() -> set[str]:
    return set(SKILLS) | SPECIAL_ACTIONS
