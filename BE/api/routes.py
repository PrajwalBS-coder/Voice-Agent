"""Jarvis control API routes."""

from fastapi import APIRouter

from BE.models.schemas import AgentStatus, MessageResponse, StartRequest
from BE.services.agent_process import AgentProcess


def create_router(agent: AgentProcess) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health")
    def health() -> MessageResponse:
        return MessageResponse(message="ok")

    @router.get("/status")
    def status() -> AgentStatus:
        return AgentStatus(**agent.snapshot())

    @router.post("/start")
    def start(request: StartRequest) -> MessageResponse:
        if agent.is_running:
            return MessageResponse(message="Jarvis is already running.")
        agent.start(request.duration)
        return MessageResponse(message="Jarvis started.")

    @router.post("/stop")
    def stop() -> MessageResponse:
        agent.stop()
        return MessageResponse(message="Jarvis stopped.")

    return router
