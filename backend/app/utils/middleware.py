"""HTTP cache policy, origin checks and request metrics."""
from time import perf_counter
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.utils.config import get_settings
from app.utils.metrics import request_metrics

settings = get_settings()
logger = logging.getLogger(__name__)


async def api_cache_policy(request: Request, call_next):
    # Cookie-authenticated writes require an explicit allowed browser origin.
    # This also protects login against login-CSRF. CLI clients supply Origin.
    if request.url.path.startswith("/api/v1") and request.method not in ("GET", "HEAD", "OPTIONS"):
        if request.headers.get("origin") not in settings.cors_origins:
            return JSONResponse({"detail": "Origin not allowed"}, status_code=403,
                                headers={"Cache-Control": "no-store"})
    stats = {"sql": 0}
    token = request_metrics.set(stats)
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        if not request.url.path.startswith("/api/v1/auth/"):
            raise
        # Authentication failures must not expose SQL parameters/cookie values in
        # tracebacks or leave a cacheable error response. Log only an event code.
        logger.error("auth_request_failed")
        response = JSONResponse({"detail": "Layanan autentikasi bermasalah. Silakan coba lagi."}, status_code=500)
    finally:
        request_metrics.reset(token)
    if settings.metrics_enabled:
        response.headers["X-DB-Queries"] = str(stats["sql"])
        response.headers["X-Response-Time-Ms"] = str(round((perf_counter() - started) * 1000, 2))
    response.headers["Cache-Control"] = "no-store"
    return response
