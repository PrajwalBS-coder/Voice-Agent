from intent_parser import IntentParser, validate_intent


def test_local_commands_are_classified():
    parser = IntentParser()
    assert parser.parse("take a photo").action == "take_picture"
    assert parser.parse("tell me the time").action == "tell_time"
    assert parser.parse("open video inception").parameters == {"name": "inception"}
    assert parser.parse("play song Blinding Lights").parameters == {"query": "Blinding Lights"}
    assert parser.parse("audio").action == "song_permission"
    assert parser.parse("nonsense please").action == "unknown"


def test_invalid_llm_action_is_safe():
    assert validate_intent({"action": "delete_everything"}).action == "unknown"
    assert validate_intent({"action": "tell_time", "parameters": "bad"}).parameters == {}
