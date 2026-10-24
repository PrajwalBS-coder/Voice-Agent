# Jarvis-lite

A local-first voice-agent foundation following `jarvis-voice-agent-plan.md`.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --text "what time is it"
```

Add `GEMINI_API_KEY=...` to `.env` to use Gemini for intent routing and context-aware follow-up commands. The key stays in the local backend environment. Gemini is selected automatically when that key is present; `OPENAI_API_KEY` remains supported. Without either key, the intent parser uses a deterministic local fallback. Add your configured video and app mappings to `config.yaml`; use `config.example.yaml` as a guide.

Secrets belong in `.env`; `.env` is excluded from version control. See `.env.example` for the template. Install the Gemini client with `pip install -r requirements.txt`.

The default `llm.provider: auto` setting uses `GEMINI_API_KEY` when available and otherwise supports `OPENAI_API_KEY`. Gemini uses constrained JSON output to route commands and Google Search grounding to answer general questions with current sources. Set `llm.provider` to `gemini`, `openai`, or `local` to choose explicitly. The Gemini model is configured by `llm.model`.

## Adding capabilities

Add a skill module with a `run(parameters)` function, then register it once in `skill_registry.py`. The intent validator, router, and LLM prompt read the same registry automatically; there is no separate `VALID_ACTIONS` list to update.

## Self-improvement research

Say `research improvements for yourself` or `learn from public GitHub repositories`. Jarvis uses the public GitHub API to collect repository metadata, links, and detected licenses, then writes a review report under `documents/research/`. It does not copy source code, execute repository code, or modify the project without a separate confirmed code-change request.

## Conversation memory

Jarvis stores each interaction locally in `data/jarvis-memory.db` by default and
uses the latest six turns as context for the configured LLM. This lets it resolve
follow-up references such as “when was she born?” after an earlier question.
To disable memory, set `memory.enabled: false` in `config.yaml`. When a Gemini or OpenAI
key is configured, the selected recent turns are sent with the current request;
without one, interactions are still stored locally but the offline parser does
not use them to answer free-form follow-up questions.

## Voice mode

With a microphone connected, start push-to-talk voice mode:

```powershell
python main.py --voice --duration 5
```

Speak when Jarvis prints the active input device and says “Speak now.” It records only after detecting speech, stops after silence, then transcribes and handles the command. Empty or very short captures are discarded instead of being sent to Whisper, which reduces silence hallucinations. Captured recordings are saved under `audio/input/`; the console and UI activity log show the input device and saved path. The first use of Whisper downloads the configured model. Press Ctrl+C to exit.

After the microphone and speech model are initialized, Jarvis greets you aloud with a time-of-day greeting and confirms that it is listening. This also happens when you start it from the control UI. Set `voice.startup_greeting: false` to disable it; spoken greetings require `voice.tts_enabled: true` and either `GEMINI_API_KEY` or a working local speech voice.

For more reliable listening, the default recorder now accepts quieter speech, keeps a longer pre-roll, and waits slightly longer before ending an utterance. Whisper uses beam search and does not apply a second VAD pass by default, which helps preserve short words. For better recognition on a faster computer, set `voice.stt_model` to `small.en`. For noisy rooms, set `audio.vad_enabled: true` after installing the updated requirements.

Voice controls:

- Say `stop`, `stop working now`, or `go to sleep` to hear a final response and stop the voice loop.
- Say `start` while the loop is running to confirm that Jarvis is already listening.
- To start a fully stopped process again, use the Svelte UI Start button or the backend `POST /api/start` endpoint. A stopped process cannot hear a spoken start command.

## Music search and playback

Say `play song <title>` (or `listen to <title>`). Jarvis asks whether you want
audio or video results before it opens a YouTube search in your browser. Reply
`audio` or `video` to grant permission, or say `cancel song` to discard the
request. It does not download music or start playback without that confirmation.

## Start the control UI

See [BE/README.md](BE/README.md) for the API details and [FE/README.md](FE/README.md) for the Svelte application details.

Install backend dependencies and start the API from the workspace root:

```powershell
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
uv run --python .venv/Scripts/python.exe uvicorn BE.main:app --reload --port 8000
```

In a second terminal, start the Svelte frontend:

```powershell
cd FE
npm install
npm run dev
```

Open `http://localhost:5173`. Use the UI to start or stop the voice agent and monitor its live status and logs.

When `GEMINI_API_KEY` is set, spoken replies use Gemini TTS with `GEMINI_TTS_MODEL` (default `gemini-3.8-flash-lite-tts`) and `GEMINI_TTS_VOICE` (default `Charon`). Gemini audio is saved under `audio/output` and played through the default speakers. If Gemini TTS is unavailable, Jarvis falls back to the configured local Windows voice. The `.env.example` file shows the TTS settings.

## Code changes by voice

Install Ollama, start it with `ollama serve`, and download the configured coding model with `ollama pull qwen2.5-coder:7b`. Then say a request such as “change the greeting in the code.” Jarvis will show the proposed files and apply them only when you type `CONFIRM`.

The camera, microphone, Whisper, Gemini, OpenAI, and TTS dependencies are imported only when those features are used. `take_picture` therefore needs a working webcam, while `take_screenshot` uses Windows screen capture. Unknown commands fall back to a DuckDuckGo web search, so web access is needed for search answers. Gemini and OpenAI improve intent classification and contextual command routing; speech recognition remains local Whisper.

## Tests

```powershell
python -m pytest -q
```
