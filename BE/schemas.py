"""API request and response schemas."""

from pydantic import BaseModel, Field


class AgentStatus(BaseModel):
    running: bool
    state: str
    pid: int | None = None
    logs: list[str] = Field(default_factory=list)


class StartRequest(BaseModel):
    duration: int = Field(default=15, ge=1, le=120)


class MessageResponse(BaseModel):
    message: str
