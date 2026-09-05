from skills.search_web import _search_subject


def test_conversational_question_prefixes_are_removed():
    assert _search_subject("I've asked about Robert Downey Jr.") == "Robert Downey Jr"
    assert _search_subject("Tell me about Ada Lovelace") == "Ada Lovelace"


def test_plain_search_query_is_preserved():
    assert _search_subject("latest space news") == "latest space news"
