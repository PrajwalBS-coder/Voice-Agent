"""Route validated intents to skills."""

from collections.abc import Callable
from typing import Any

from intent_parser import Intent
from skills import about_me, greeting, open_app, open_video, search_web, take_picture, take_screenshot, tell_time, thanks, voice_help

Skill = Callable[[dict[str, Any]], str]
SKILLS: dict[str, Skill] = {
    "take_picture": take_picture.run,
    "take_screenshot": take_screenshot.run,
    "about_me": about_me.run,
    "greeting": greeting.run,
    "thanks": thanks.run,
    "voice_help": voice_help.run,
    "search_web": search_web.run,
    "open_video": open_video.run,
    "open_app": open_app.run,
    "tell_time": tell_time.run,
}


def run_intent(intent: Intent) -> str:
    skill = SKILLS.get(intent.action)
    if skill is None:
        return "I did not understand that command."
    try:
        return skill(intent.parameters)
    except Exception as error:
        return f"The command failed: {error}"
