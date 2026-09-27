"""Session authentication and account authorization; no HTTP cookie handling."""
import secrets
import re
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select, or_, update, func
from pwdlib.exceptions import UnknownHashError
from argon2.exceptions import InvalidHashError, VerificationError
from app.model.user import User, AuthSession
from app.model.schemas.auth import LoginInput
from app.utils.tokens import digest
from app.utils.rate_limit import check_login_rate, check_global_login_rate
from app.utils.config import get_settings
from app.utils.passwords import passwords, DUMMY_HASH

logger = logging.getLogger(__name__)


def valid_token(token):
    return isinstance(token, str) and re.fullmatch(r"[A-Za-z0-9_-]{64}", token) is not None

def user_data(user):
    return dict(id=str(user.id), name=user.name, email=user.email or "",
                phone=user.phone or "", role=user.role)


def current_user(token, db):
    if not valid_token(token):
        raise HTTPException(401, "Authentication required")
    now = datetime.utcnow()
    idle_cutoff = now - timedelta(seconds=get_settings().session_idle_seconds)
    session = db.scalar(select(AuthSession).where(
        AuthSession.refresh_token_hash == digest(token),
        AuthSession.revoked_at.is_(None), AuthSession.expires_at > now,
        func.coalesce(AuthSession.last_used_at, AuthSession.created_at) > idle_cutoff))
    user = db.get(User, session.user_id) if session else None
    if not user or not user.is_active:
        raise HTTPException(401, "Session expired")
    last_used = session.last_used_at or session.created_at
    if last_used <= now - timedelta(seconds=60):
        # Never resurrect a session that was concurrently logged out.
        result = db.execute(update(AuthSession).where(
            AuthSession.id == session.id, AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now).values(last_used_at=now))
        db.commit()
        if result.rowcount != 1:
            raise HTTPException(401, "Session expired")
    return user


def admin_user(user):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


def login(data: LoginInput, previous, db):
    check_global_login_rate()
    user = db.scalar(select(User).where(or_(User.email == data.identifier.strip(),
                                           User.phone == data.identifier.strip())))
    check_login_rate(data.identifier, user.id if user else None)
    stored_hash = user.password_hash if user else DUMMY_HASH
    try:
        valid, updated_hash = passwords.verify_and_update(data.password.get_secret_value(), stored_hash)
    except (UnknownHashError, InvalidHashError, VerificationError):
        logger.warning("auth_password_hash_invalid")
        passwords.verify(data.password.get_secret_value(), DUMMY_HASH)
        valid, updated_hash = False, None
    if not valid or not user or not user.is_active:
        raise HTTPException(401, "Email/nomor HP atau password salah")
    # Refresh under a lock after hashing to catch concurrent disable/password change.
    user = db.scalar(select(User).where(User.id == user.id).with_for_update()
                     .execution_options(populate_existing=True))
    if not user or not user.is_active or user.password_hash != stored_hash:
        raise HTTPException(401, "Email/nomor HP atau password salah")
    if updated_hash:
        user.password_hash = updated_hash
    now = datetime.utcnow()
    if valid_token(previous):
        db.execute(update(AuthSession).where(
            AuthSession.refresh_token_hash == digest(previous),
            AuthSession.revoked_at.is_(None)).values(revoked_at=now))
    token = secrets.token_urlsafe(48)
    db.add(AuthSession(user_id=user.id, refresh_token_hash=digest(token),
                       last_used_at=now,
                       expires_at=now + timedelta(seconds=get_settings().session_lifetime_seconds)))
    user.last_login_at = now
    db.commit()
    return user_data(user), token


def logout(token, db):
    if valid_token(token):
        db.execute(update(AuthSession).where(
            AuthSession.refresh_token_hash == digest(token),
            AuthSession.revoked_at.is_(None)).values(revoked_at=datetime.utcnow()))
        db.commit()
    return {"ok": True}
