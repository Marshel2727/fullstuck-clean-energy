"""Atomic, shared login throttling; unavailable security storage fails closed."""
import logging
from functools import lru_cache

from fastapi import HTTPException
from redis import Redis
from redis.exceptions import RedisError
from redis.backoff import NoBackoff
from redis.retry import Retry

from app.utils.config import get_settings
from app.utils.tokens import digest

logger = logging.getLogger(__name__)

# Reject without incrementing once full; requests cannot prolong a lockout.
_CONSUME = """
local count = tonumber(redis.call('GET', KEYS[1]) or '0')
if count >= tonumber(ARGV[1]) then
    return math.max(1, redis.call('TTL', KEYS[1]))
end
count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[2]) end
return 0
"""


@lru_cache
def auth_redis():
    return Redis.from_url(get_settings().auth_redis_url,
                          socket_connect_timeout=0.5, socket_timeout=0.5,
                          retry=Retry(NoBackoff(), 0), max_connections=32)


def _consume(scope, identity, limit, seconds):
    try:
        retry_after = int(auth_redis().eval(
            _CONSUME, 1, f"auth:login:v1:{scope}:{digest(identity)}", limit, seconds))
    except RedisError:
        # Never log exception URLs, credentials, identifiers or request bodies.
        logger.warning("auth_rate_limit_unavailable")
        raise HTTPException(503, "Login sementara tidak tersedia. Silakan coba lagi.",
                            headers={"Retry-After": "30"}) from None
    if retry_after:
        raise HTTPException(429, "Terlalu banyak percobaan login. Silakan tunggu lalu coba lagi.",
                            headers={"Retry-After": str(retry_after)})


def check_global_login_rate():
    # Coarse protection before DB lookup/hash work; ingress must also limit by IP.
    # Never trust arbitrary X-Forwarded-For sent through the Next.js proxy.
    _consume("global", "all", get_settings().login_global_limit, 60)


def check_upload_rate():
    # Coarse shared limit, since the frontend proxy hides the original client IP.
    try:
        retry_after = int(auth_redis().eval(_CONSUME, 1, "uploads:requests:global:v1", 20, 60))
    except RedisError:
        raise HTTPException(503, "Unggah lampiran sementara tidak tersedia. Coba lagi nanti.") from None
    if retry_after:
        raise HTTPException(429, "Terlalu banyak pengajuan lampiran. Coba lagi sebentar.",
                            headers={"Retry-After": str(retry_after)})


def check_login_rate(identifier, user_id=None):
    settings = get_settings()
    # Email, phone and collation-equivalent aliases share the existing user's key.
    identity = f"user:{user_id}" if user_id is not None else f"unknown:{identifier.strip().casefold()}"
    _consume("account", identity, settings.login_account_limit, settings.login_account_window_seconds)
