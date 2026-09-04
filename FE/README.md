# Jarvis Frontend

The `FE` folder contains the Svelte/Vite control panel for starting and stopping Jarvis and monitoring its runtime state.

## Structure

```text
FE/
├── index.html       # Browser entry document
├── package.json     # Node scripts and dependencies
├── vite.config.js   # Vite and Svelte configuration
└── src/
    ├── components/  # Reusable Svelte UI components
    │   ├── README.md
    │   └── StatusCard.svelte
    ├── lib/         # Shared frontend utilities
    ├── services/    # API clients and backend communication
    │   ├── README.md
    │   └── api.js
    ├── stores/      # Shared Svelte state
    ├── assets/      # Static assets
    ├── App.svelte   # Control screen and API calls
    ├── app.css      # Visual styles and responsive layout
    └── main.js      # Svelte application entry point
```

## Features

- Start and stop the voice agent
- Set the maximum listening duration
- Show `stopped`, `starting`, `listening`, `processing`, or `speaking` state
- Display process ID and recent backend logs
- Poll the backend status automatically

## Run in development

Start the backend first from the workspace root:

```powershell
uv run --python .venv/Scripts/python.exe uvicorn BE.main:app --reload --port 8000
```

Then open a second terminal in this folder:

```powershell
cd FE
npm install
npm run dev
```

Open `http://localhost:5173` in a browser. The frontend expects the backend at `http://127.0.0.1:8000`.

## Build for production

```powershell
cd FE
npm run build
npm run preview
```

The production output is generated in `FE/dist/`. It is ignored by `FE/.gitignore`.

## API contract

The UI sends:

```http
POST /api/start
Content-Type: application/json

{"duration": 15}
```

It also calls `GET /api/status` every second and sends `POST /api/stop` when the Stop button is used. CORS is configured in the backend for ports `5173` on localhost.
