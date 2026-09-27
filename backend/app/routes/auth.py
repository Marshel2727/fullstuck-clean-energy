from fastapi import APIRouter, Depends, Request, Response
from app.model.schemas.auth import LoginInput
from app.routes.dependencies import current_user
from app.service import auth as service
from app.utils.database import get_db
from app.utils.cookies import session_token, set_session_cookie, delete_session_cookie

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginInput, request: Request, response: Response, db=Depends(get_db)):
    user, token = service.login(data, session_token(request), db)
    set_session_cookie(response, token)
    return user


@router.get("/me")
def me(user=Depends(current_user)):
    return service.user_data(user)


@router.post("/logout")
def logout(request: Request, response: Response, db=Depends(get_db)):
    result = service.logout(session_token(request), db)
    delete_session_cookie(response)
    return result
