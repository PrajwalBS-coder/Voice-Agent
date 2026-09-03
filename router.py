"""Route validated intents to skills."""

from intent_parser import Intent
from skill_registry import SKILLS


def run_intent(intent: Intent) -> str:
    skill = SKILLS.get(intent.action)
    if skill is None:
        return "I did not understand that command."
    try:
        return skill(intent.parameters)
    except Exception as error:
        return f"The command failed: {error}"
