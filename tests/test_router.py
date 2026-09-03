from intent_parser import Intent
from router import run_intent


def test_unknown_command_returns_safe_message():
    assert run_intent(Intent("unknown", {})) == "I did not understand that command."


def test_time_skill_returns_confirmation():
    assert run_intent(Intent("tell_time", {})).startswith("It is ")
