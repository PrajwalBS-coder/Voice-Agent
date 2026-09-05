"""Permission-gated song search and browser playback handoff."""

from __future__ import annotations

import webbrowser
from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass
class MusicSession:
    """Keep the requested song until the user chooses a playback format."""

    pending_song: str | None = None

    def request(self, song: str) -> str:
        song = song.strip(" .?!")
        if not song:
            return "Which song would you like me to search for?"
        self.pending_song = song
        return (
            f"I can search YouTube for {song}. Would you like audio results or "
            "video results? Please say audio or video to give permission to open it."
        )

    def approve(self, media_type: str) -> str:
        if not self.pending_song:
            return "There is no pending song request. Ask me to play a song first."
        if media_type not in {"audio", "video"}:
            return "Please say audio or video."
        song = self.pending_song
        self.pending_song = None
        query = f"{song} official {media_type}"
        url = f"https://www.youtube.com/results?{urlencode({'search_query': query})}"
        try:
            webbrowser.open(url)
        except Exception as error:
            return f"I could not open {media_type} results for {song}: {error}"
        return f"Opening {media_type} results for {song} on YouTube."

    def cancel(self) -> str:
        if not self.pending_song:
            return "There is no pending song request to cancel."
        self.pending_song = None
        return "Song request cancelled."
