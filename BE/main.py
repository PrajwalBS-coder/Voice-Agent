"""FastAPI control server for Jarvis."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from BE.api.routes import create_router
from BE.core.settings import FRONTEND_ORIGINS, WORKSPACE
from BE.services.agent_process import AgentProcess

agent = AgentProcess(WORKSPACE)
app = FastAPI(title="Jarvis Control API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(create_router(agent))
