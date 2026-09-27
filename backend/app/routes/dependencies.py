"""HTTP authentication dependencies shared by all routers."""
from fastapi import Depends, Request
from app.service import auth as service
from app.utils.database import get_db
from app.utils.cookies import session_token


def current_user(request: Request, db=Depends(get_db)):
    return service.current_user(session_token(request), db)


def admin_user(user=Depends(current_user)):
    return service.admin_user(user)


def optional_user(request: Request, db=Depends(get_db)):
    return current_user(request, db) if session_token(request) else None
