"""Route validated intents to skills."""

import logging

from intent_parser import Intent
from skill_registry import SKILLS

logger = logging.getLogger(__name__)


def run_intent(intent: Intent) -> str:
    skill = SKILLS.get(intent.action)
    if skill is None:
        return "I did not understand that command."
    try:
        return skill(intent.parameters)
    except Exception as error:
        logger.exception("Skill %s failed", intent.action)
        return "The command failed. Please try again."
