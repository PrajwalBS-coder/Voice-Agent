"""Search DuckDuckGo and return concise spoken results."""

from html.parser import HTMLParser
import json
import re
from html import unescape
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

USER_AGENT = "Jarvis-lite/1.0"
QUESTION_PREFIXES = (
    "can you tell me about ",
    "could you tell me about ",
    "i want to know about ",
    "i would like to know about ",
    "i have asked about ",
    "i've asked about ",
    "i asked about ",
    "tell me about ",
    "who is ",
    "what is ",
    "what are ",
)


class _ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[str] = []
        self._in_result = False
        self._buffer = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class", "") or ""
        if tag == "a" and "result__a" in classes:
            self._in_result = True
            self._buffer = ""

    def handle_data(self, data: str) -> None:
        if self._in_result:
            self._buffer += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_result:
            title = " ".join(self._buffer.split())
            if title:
                self.results.append(title)
            self._in_result = False


def _search_subject(query: str) -> str:
    """Remove conversational wording that lowers web-search recall."""
    cleaned = query.strip(" .?!")
    lowered = cleaned.lower()
    for prefix in QUESTION_PREFIXES:
        if lowered.startswith(prefix):
            return cleaned[len(prefix):].strip(" .?!")
    return cleaned


def _wikipedia_summary(query: str) -> str | None:
    subject = _search_subject(query)
    if subject.casefold() == query.strip(" .?!").casefold():
        return None
    subjects = [subject]
    if subject.startswith("the "):
        subjects.append(subject[4:])
    if subject.removeprefix("the ") == "interstellar":
        subjects.insert(0, "interstellar (film)")
    for candidate in subjects:
        title = quote_plus(candidate.replace(" ", "_"))
        request = Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
            headers={"User-Agent": USER_AGENT},
        )
        try:
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8", errors="ignore"))
        except Exception:
            continue
        extract = data.get("extract")
        if extract:
            return str(extract)
    return None


def run(parameters: dict[str, Any]) -> str:
    query = str(parameters.get("query", "")).strip()
    if not query:
        return "What would you like me to search for?"
    search_query = _search_subject(query)
    try:
        summary = _wikipedia_summary(query)
        if summary:
            return summary
    except Exception:
        pass
    try:
        api_request = Request(
            f"https://api.duckduckgo.com/?q={quote_plus(search_query)}&format=json&no_html=1",
            headers={"User-Agent": USER_AGENT},
        )
        with urlopen(api_request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))
        answer = data.get("Answer") or data.get("AbstractText")
        if answer:
            return f"{answer}"
        related_topics = data.get("RelatedTopics", [])
        for topic in related_topics:
            if isinstance(topic, dict) and topic.get("Text"):
                return str(topic["Text"])
            if isinstance(topic, dict) and topic.get("Result"):
                text = re.sub(r"<[^>]+>", "", str(topic["Result"]))
                return unescape(" ".join(text.split()))
    except Exception:
        pass
    try:
        request = Request(
            f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}",
            headers={"User-Agent": USER_AGENT},
        )
        with urlopen(request, timeout=10) as response:
            parser = _ResultParser()
            parser.feed(response.read().decode("utf-8", errors="ignore"))
    except Exception:
        return "I could not reach the web right now."
    if not parser.results:
        return f"I found no results for {search_query}."
    results = "; ".join(parser.results[:3])
    return f"Here are the top results for {search_query}: {results}."
