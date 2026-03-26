from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ActionCreate(BaseModel):
    user_id: str
    session_id: str
    action_type: str
    target: str | None = None
    page_url: str | None = None
    metadata: dict[str, Any] | None = None
    timestamp: datetime


class ActionBatchCreate(BaseModel):
    actions: list[ActionCreate]


class ActionResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    action_type: str
    target: str | None = None
    page_url: str | None = None
    metadata: dict[str, Any] | None = None
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ActionListResponse(BaseModel):
    actions: list[ActionResponse]
    total: int


class SessionResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    user_agent: str | None = None
    ip_address: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    action_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class UserSummaryResponse(BaseModel):
    user_id: str
    total_actions: int
    total_sessions: int
    action_breakdown: dict[str, int]
