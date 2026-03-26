from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ActionType, UserAction, UserSession
from app.schemas.actions import ActionCreate


def _validate_action_type(action_type: str) -> str:
    try:
        return ActionType(action_type).value
    except ValueError:
        allowed = [a.value for a in ActionType]
        raise ValueError(f"Invalid action_type '{action_type}'. Allowed: {allowed}")


def _upsert_session(db: Session, action: ActionCreate) -> None:
    """Create or update the UserSession record for this action."""
    session_row = (
        db.execute(
            select(UserSession).where(UserSession.session_id == action.session_id)
        )
        .scalars()
        .first()
    )

    if session_row is None:
        session_row = UserSession(
            user_id=action.user_id,
            session_id=action.session_id,
            started_at=action.timestamp,
            action_count=1,
        )
        db.add(session_row)
    else:
        session_row.action_count += 1
        if action.timestamp > (session_row.ended_at or session_row.started_at):
            session_row.ended_at = action.timestamp


def create_action(db: Session, action: ActionCreate) -> UserAction:
    _validate_action_type(action.action_type)

    row = UserAction(
        user_id=action.user_id,
        session_id=action.session_id,
        action_type=action.action_type,
        target=action.target,
        page_url=action.page_url,
        action_metadata=action.metadata,
        timestamp=action.timestamp,
    )
    db.add(row)
    _upsert_session(db, action)
    db.commit()
    db.refresh(row)
    return row


def create_actions_batch(db: Session, actions: list[ActionCreate]) -> list[UserAction]:
    rows: list[UserAction] = []
    for action in actions:
        _validate_action_type(action.action_type)
        row = UserAction(
            user_id=action.user_id,
            session_id=action.session_id,
            action_type=action.action_type,
            target=action.target,
            page_url=action.page_url,
            action_metadata=action.metadata,
            timestamp=action.timestamp,
        )
        db.add(row)
        _upsert_session(db, action)
        rows.append(row)

    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def list_actions(
    db: Session,
    *,
    user_id: str | None = None,
    session_id: str | None = None,
    action_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[UserAction], int]:
    stmt = select(UserAction)
    if user_id:
        stmt = stmt.where(UserAction.user_id == user_id)
    if session_id:
        stmt = stmt.where(UserAction.session_id == session_id)
    if action_type:
        stmt = stmt.where(UserAction.action_type == action_type)

    total = len(db.execute(stmt.with_only_columns(UserAction.id)).all())

    stmt = stmt.order_by(UserAction.timestamp.desc()).limit(limit).offset(offset)
    actions = list(db.execute(stmt).scalars().all())
    return actions, total


def list_sessions(
    db: Session,
    *,
    user_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[UserSession], int]:
    stmt = select(UserSession)
    if user_id:
        stmt = stmt.where(UserSession.user_id == user_id)

    total = len(db.execute(stmt.with_only_columns(UserSession.id)).all())

    stmt = stmt.order_by(UserSession.updated_at.desc()).limit(limit).offset(offset)
    sessions = list(db.execute(stmt).scalars().all())
    return sessions, total


def get_user_summary(db: Session, user_id: str) -> dict:
    total_actions = db.execute(
        select(func.count()).select_from(UserAction).where(UserAction.user_id == user_id)
    ).scalar() or 0

    total_sessions = db.execute(
        select(func.count()).select_from(UserSession).where(UserSession.user_id == user_id)
    ).scalar() or 0

    breakdown_rows = db.execute(
        select(UserAction.action_type, func.count())
        .where(UserAction.user_id == user_id)
        .group_by(UserAction.action_type)
    ).all()
    action_breakdown = {row[0]: row[1] for row in breakdown_rows}

    return {
        "user_id": user_id,
        "total_actions": total_actions,
        "total_sessions": total_sessions,
        "action_breakdown": action_breakdown,
    }
