"""Search DuckDuckGo and return concise spoken results."""

from html.parser import HTMLParser
import json
import re
from html import unescape
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

USER_AGENT = "Jarvis-lite/1.0"


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


def _wikipedia_summary(query: str) -> str | None:
    prefixes = ("tell me about ", "who is ", "what is ", "what are ")
    subject = query.lower()
    for prefix in prefixes:
        if subject.startswith(prefix):
            subject = query[len(prefix):].strip(" .?!")
            break
    if subject == query.lower():
        return None
    title = quote_plus(subject.replace(" ", "_"))
    request = Request(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
        headers={"User-Agent": USER_AGENT},
    )
    with urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8", errors="ignore"))
    extract = data.get("extract")
    return str(extract) if extract else None


def run(parameters: dict[str, Any]) -> str:
    query = str(parameters.get("query", "")).strip()
    if not query:
        return "What would you like me to search for?"
    try:
        summary = _wikipedia_summary(query)
        if summary:
            return summary
    except Exception:
        pass
    try:
        api_request = Request(
            f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1",
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
            f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
            headers={"User-Agent": USER_AGENT},
        )
        with urlopen(request, timeout=10) as response:
            parser = _ResultParser()
            parser.feed(response.read().decode("utf-8", errors="ignore"))
    except Exception:
        return "I could not reach the web right now."
    if not parser.results:
        return f"I found no results for {query}."
    results = "; ".join(parser.results[:3])
    return f"Here are the top results for {query}: {results}."