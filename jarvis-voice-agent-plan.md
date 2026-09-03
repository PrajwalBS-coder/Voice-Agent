# Voice Agent Build Plan — "Jarvis-lite"

A phased plan for building a local voice assistant that can listen, understand commands, and trigger actions (take a picture, open a specific video, open an app, etc). Written so it can be handed directly to a coding agent (e.g. Claude Code) task by task.

---

## 1. Goal & Scope

**MVP goal:** Say a wake word → speak a command → agent transcribes it → agent figures out which action to run → agent runs it → agent speaks back a confirmation.

**MVP actions to support first:**
- Take a picture (webcam)
- Open a specific video file / folder
- Open a specific app or website
- Tell the time / basic Q&A (sanity check that the pipeline works)

**Later actions (Phase 4+):** volume/brightness control, reminders, weather, smart-home, search the web, custom scripts.

Keep scope narrow for v1 — 4 working commands end-to-end beats 20 half-working ones.

---

## 2. High-Level Architecture

```
 Mic input
   │
   ▼
[1. Wake Word Detector]  ──(idle, always listening)
   │ triggers on "Hey Jarvis"
   ▼
[2. Speech-to-Text (STT)]  → raw transcript
   │
   ▼
[3. Intent Parser (LLM)]  → structured JSON: {action, parameters}
   │
   ▼
[4. Action Router / Skills]  → runs the matching Python function
   │
   ▼
[5. Text-to-Speech (TTS)]  → spoken confirmation
   │
   ▼
 Speaker output
```

Each numbered block is an independent module with a clear input/output contract — build and test them separately before wiring them together.

---

## 3. Recommended Tech Stack

| Component | Simple/offline option | More capable option |
|---|---|---|
| Wake word | `openWakeWord` (free, local) | Picovoice Porcupine (free tier, very accurate) |
| STT | `faster-whisper` (local, runs on CPU) | OpenAI Whisper API / Deepgram |
| Intent parsing | Claude/GPT API call with structured output (function calling / JSON schema) | Same, just the core brain |
| Action execution | Plain Python (`opencv-python`, `subprocess`, `os`, `webbrowser`) | Same |
| TTS | `pyttsx3` (offline, robotic but free) | ElevenLabs API / OpenAI TTS (natural voice) |
| Orchestration | Simple Python loop | asyncio event loop if you want it fully non-blocking |

Recommendation for v1: local wake word + local STT (keeps latency low and works offline) + one LLM API call for intent parsing (this is the part that actually needs "intelligence") + offline TTS to start, upgrade later.

---

## 4. Project Structure

```
jarvis-agent/
├── main.py                 # orchestrator loop
├── config.yaml              # wake word, paths, API keys (keys via env vars, not hardcoded)
├── wake_word.py              # module 1
├── stt.py                    # module 2
├── intent_parser.py          # module 3 (calls the LLM)
├── skills/
│   ├── __init__.py
│   ├── take_picture.py
│   ├── open_video.py
│   ├── open_app.py
│   └── tell_time.py
├── tts.py                    # module 5
└── requirements.txt
```

---

## 5. The Intent Parser (the actual "brain")

This is the piece that makes it feel like Jarvis instead of a fixed if/else command list.

- Send the transcript to an LLM with a system prompt that defines the available "tools"/skills and asks for a strict JSON response, e.g.:
  ```json
  {"action": "open_video", "parameters": {"name": "inception"}}
  ```
- Use the model provider's native structured-output / tool-calling feature rather than hand-parsing text — far more reliable.
- Keep a fixed enum of valid `action` values; if the model returns something outside it, fall back to "I didn't understand that."
- This design means adding a new capability later is just: (a) add a new skill function, (b) add it to the tool list in the prompt. No new parsing logic needed.

---

## 6. Skills (Action Modules)

Each skill is a plain Python function with a predictable signature, e.g. `def run(parameters: dict) -> str` returning a string to speak back.

- `take_picture.py` — use `opencv-python` to grab a frame from the webcam and save it with a timestamped filename.
- `open_video.py` — keep a small local mapping of video "nicknames" → file paths (or search a media folder), then open with the OS default player (`subprocess`/`os.startfile` on Windows, `open` on Mac, `xdg-open` on Linux).
- `open_app.py` — mapping of app names → launch commands.
- `tell_time.py` — trivial, good for testing the pipeline before building real skills.

Build and unit-test each skill standalone (call it directly with hardcoded parameters) before connecting it to the pipeline.

---

## 7. Build Order (phases for the coding agent)

**Phase 0 — Environment**
1. Set up project structure, virtualenv, `requirements.txt`.
2. Get mic input working at all (record N seconds, save to .wav, play it back).

**Phase 1 — STT pipeline**
3. Integrate `faster-whisper`, transcribe a test recording, print text.

**Phase 2 — Skills (no voice yet)**
4. Build `take_picture.py`, `open_video.py`, `open_app.py`, `tell_time.py`. Test each by calling directly from a script.

**Phase 3 — Intent parsing**
5. Write the system prompt + tool schema for the LLM.
6. Feed it sample transcripts ("take a picture", "open the inception video") and confirm it returns correct JSON.

**Phase 4 — Wire the loop**
7. Connect: record → STT → intent parser → skill router → print result (no TTS yet).
8. Test end-to-end with real speech.

**Phase 5 — Wake word + TTS**
9. Add wake word detection so it's not always actively recording.
10. Add TTS so it speaks confirmations back.

**Phase 6 — Polish**
11. Error handling (unclear command, skill failure, no mic input).
12. Config file for paths/nicknames instead of hardcoding.
13. Logging for debugging.

**Phase 7 — Expand**
14. Add more skills one at a time, following the same pattern.

---

## 8. Testing Checklist

- [ ] Mic records and plays back correctly
- [ ] STT transcribes clearly with reasonable accuracy
- [ ] Intent parser returns valid JSON for all 4 MVP commands
- [ ] Intent parser gracefully handles nonsense input
- [ ] Each skill runs correctly when called directly
- [ ] Full pipeline works end-to-end for each MVP command
- [ ] Wake word doesn't false-trigger constantly
- [ ] TTS response is understandable

---

## 9. How to Hand This to a Coding Agent

Give the agent one phase at a time rather than the whole plan at once — e.g. "Build Phase 0 and Phase 1 from this plan, in Python, in this folder." Review and test each phase before moving to the next. This keeps each step small enough to verify and avoids the agent guessing at architecture decisions you haven't made yet.
