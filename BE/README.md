# Jarvis Backend

The `BE` folder contains the FastAPI control API for the Jarvis voice agent. It starts and stops the existing root-level `main.py --voice` process and exposes its current state and recent logs.

## Structure

```text
BE/
├── api/              # HTTP route modules
│   ├── __init__.py
│   └── routes.py      # Health, status, start, and stop endpoints
├── core/             # Shared configuration and utilities
│   ├── __init__.py
│   └── settings.py    # Workspace and CORS settings
├── models/           # Database and persistent data models
│   ├── __init__.py
│   └── schemas.py     # API request and response models
├── services/         # Business logic and integrations
│   ├── __init__.py
│   └── agent_process.py # Voice process lifecycle and logs
├── tests/            # Backend tests
│   ├── __init__.py
│   └── README.md
├── __init__.py       # Python package marker
├── main.py           # FastAPI application and API routes
├── schemas.py        # Legacy compatibility module
└── agent_process.py  # Legacy compatibility module
```

## API

| Method | Endpoint      | Purpose                                           |
| ------ | ------------- | ------------------------------------------------- |
| `GET`  | `/api/health` | Check that the API is available                   |
| `GET`  | `/api/status` | Return running state, process ID, and recent logs |
| `POST` | `/api/start`  | Start voice mode                                  |
| `POST` | `/api/stop`   | Stop voice mode                                   |

Start request body:

```json
{
  "duration": 15
}
```

`duration` is the maximum listening time per command and must be between 1 and 120 seconds.

## Run locally

Run these commands from the workspace root:

```powershell
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
uv run --python .venv/Scripts/python.exe uvicorn BE.main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Runtime behavior

- The API launches the existing voice agent with the same Python interpreter used by Uvicorn.
- Output is captured and exposed through `/api/status`.
- The frontend polls status approximately once per second.
- Only one voice-agent process can run at a time.
- Stopping the API-managed process does not delete recorded audio or database data.

The backend requires the root project dependencies, a working microphone, and the configured PostgreSQL connection for interaction logging. Jarvis continues operating if database logging is unavailable.
