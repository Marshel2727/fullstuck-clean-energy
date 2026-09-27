"""One cookie policy for issuing, reading and removing opaque sessions."""
from app.utils.config import get_settings
from app.utils.tokens import COOKIE


def session_token(request):
    # Production never accepts the old insecure development cookie as fallback.
    return request.cookies.get(get_settings().session_cookie_name)


def set_session_cookie(response, token):
    settings = get_settings()
    if settings.cookie_secure:
        response.delete_cookie(COOKIE, path="/api/v1", httponly=True, samesite="strict")
    response.set_cookie(settings.session_cookie_name, token, httponly=True,
                        secure=settings.cookie_secure, samesite="strict",
                        max_age=settings.session_lifetime_seconds, path=settings.session_cookie_path)


def delete_session_cookie(response):
    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name, path=settings.session_cookie_path,
                           secure=settings.cookie_secure, httponly=True, samesite="strict")
    if settings.cookie_secure:
        response.delete_cookie(COOKIE, path="/api/v1", httponly=True, samesite="strict")
