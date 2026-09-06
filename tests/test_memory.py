from database import InteractionDatabase


def test_sqlite_memory_returns_recent_turns_in_chronological_order(tmp_path):
    database = InteractionDatabase(f"sqlite:///{tmp_path / 'jarvis.db'}")
    database.record("Who is Ada Lovelace?", "Ada Lovelace was a mathematician.", "search_web", "calm")
    database.record("When was she born?", "She was born in 1815.", "search_web", "calm")

    turns = database.recent_interactions(limit=1)

    assert turns == [{
        "input_text": "When was she born?",
        "output_text": "She was born in 1815.",
        "action": "search_web",
        "emotion": "calm",
    }]
