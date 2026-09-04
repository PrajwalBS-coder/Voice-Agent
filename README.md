# Jarvis-lite

A local-first voice-agent foundation following `jarvis-voice-agent-plan.md`.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --text "what time is it"
```

Without `OPENAI_API_KEY`, the intent parser uses a small deterministic fallback so the pipeline can be tested offline. Add your configured video and app mappings to `config.yaml`; use `config.example.yaml` as a guide.

Secrets belong in `.env`. Add your key as `OPENAI_API_KEY=...`; `.env` is excluded from version control. See `.env.example` for the template.

## Adding capabilities

Add a skill module with a `run(parameters)` function, then register it once in `skill_registry.py`. The intent validator, router, and LLM prompt read the same registry automatically; there is no separate `VALID_ACTIONS` list to update.

## Voice mode

With a microphone connected, start push-to-talk voice mode:

```powershell
python main.py --voice --duration 5
```

Speak when Jarvis says “Listening.” It detects when you stop speaking, then transcribes the command, runs it, and speaks the response. The first use of Whisper downloads the configured model. Press Ctrl+C to exit.

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

The default TTS voice is Microsoft David with a slower, formal AI-style delivery. Change `tts_voice` to `Hazel` or `Zira`, or adjust `tts_rate` in `config.yaml`. Jarvis also uses calm, happy, and empathetic delivery profiles by changing rate and volume. The exact movie JARVIS voice is not included with Windows.

## Code changes by voice

Install Ollama, start it with `ollama serve`, and download the configured coding model with `ollama pull qwen2.5-coder:7b`. Then say a request such as “change the greeting in the code.” Jarvis will show the proposed files and apply them only when you type `CONFIRM`.

The camera, microphone, Whisper, OpenAI, and TTS dependencies are imported only when those features are used. `take_picture` therefore needs a working webcam, while `take_screenshot` uses Windows screen capture. Unknown commands fall back to a DuckDuckGo web search, so web access is needed for search answers. The LLM path needs `OPENAI_API_KEY`.

## Tests

```powershell
python -m pytest -q
```
