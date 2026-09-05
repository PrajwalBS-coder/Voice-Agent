from unittest.mock import patch

from skills.music import MusicSession


def test_song_requires_format_permission_before_opening_browser():
    session = MusicSession()

    response = session.request("Blinding Lights")
    assert "audio results or video results" in response
    assert session.pending_song == "Blinding Lights"

    with patch("skills.music.webbrowser.open") as open_browser:
        response = session.approve("audio")

    assert "Opening audio results" in response
    assert "Blinding+Lights+official+audio" in open_browser.call_args.args[0]
    assert session.pending_song is None


def test_song_permission_without_request_does_not_open_browser():
    session = MusicSession()

    with patch("skills.music.webbrowser.open") as open_browser:
        response = session.approve("video")

    assert "no pending song request" in response
    open_browser.assert_not_called()
