from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.actions import (
    ActionBatchCreate,
    ActionCreate,
    ActionListResponse,
    ActionResponse,
    SessionListResponse,
    SessionResponse,
    UserSummaryResponse,
)
from app.services.actions import (
    create_action,
    create_actions_batch,
    get_user_summary,
    list_actions,
    list_sessions,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/actions", response_model=ActionResponse, status_code=201)
def post_action(
    body: ActionCreate,
    db: Session = Depends(get_db),
) -> ActionResponse:
    """Record a single user action (click, page view, scroll, etc.)."""
    try:
        action = create_action(db, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ActionResponse.model_validate(action)


@router.post("/actions/batch", response_model=list[ActionResponse], status_code=201)
def post_actions_batch(
    body: ActionBatchCreate,
    db: Session = Depends(get_db),
) -> list[ActionResponse]:
    """Record a batch of user actions in a single request.

    Use this when the frontend buffers events and flushes them periodically.
    """
    try:
        actions = create_actions_batch(db, body.actions)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return [ActionResponse.model_validate(a) for a in actions]


@router.get("/actions", response_model=ActionListResponse)
def get_actions(
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    session_id: str | None = Query(default=None, description="Filter by session ID"),
    action_type: str | None = Query(default=None, description="Filter by action type"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ActionListResponse:
    """Retrieve recorded user actions with optional filters and pagination."""
    actions, total = list_actions(
        db,
        user_id=user_id,
        session_id=session_id,
        action_type=action_type,
        limit=limit,
        offset=offset,
    )
    return ActionListResponse(
        actions=[ActionResponse.model_validate(a) for a in actions],
        total=total,
    )


@router.get("/sessions", response_model=SessionListResponse)
def get_sessions(
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SessionListResponse:
    """List tracked user sessions."""
    sessions, total = list_sessions(db, user_id=user_id, limit=limit, offset=offset)
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.get("/{user_id}/summary", response_model=UserSummaryResponse)
def get_user_summary_endpoint(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserSummaryResponse:
    """Get a summary of a user's behavior: total actions, sessions, and action breakdown."""
    summary = get_user_summary(db, user_id)
    return UserSummaryResponse(**summary)
