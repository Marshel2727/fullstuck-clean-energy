"""Versioned cache-aside. MySQL epochs prevent stale resurrection after Redis outages."""
import json
import logging
import time
from functools import lru_cache
from uuid import uuid4

from redis import Redis
from redis.exceptions import RedisError
from redis.retry import Retry
from redis.backoff import NoBackoff
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from fastapi.encoders import jsonable_encoder

from app.utils.config import get_settings
from app.model.cache import CacheEpoch

log = logging.getLogger("solarsync.cache")


@lru_cache
def redis_client():
    return Redis.from_url(
        get_settings().redis_url, decode_responses=True,
        socket_connect_timeout=0.5, socket_timeout=0.5,
        retry=Retry(NoBackoff(), 0),
    )


def bump_epoch(db, namespace):
    # Called inside the SAME transaction as the domain mutation.
    # Readers see the new epoch only after commit. Never reuse old namespaces.
    statement = insert(CacheEpoch).values(namespace=namespace, revision=uuid4().hex)
    db.execute(statement.on_duplicate_key_update(revision=statement.inserted.revision))


def read_cached(db, namespace, suffix, ttl, loader):
    start = time.perf_counter()
    epoch = db.scalar(select(CacheEpoch.revision).where(CacheEpoch.namespace == namespace)) or "initial"
    key = f"solarsync:v1:{namespace}:{epoch}:{suffix}"
    client = redis_client()
    available = get_settings().cache_enabled
    if available:
        try:
            value = client.get(key)
            if value is not None:
                result = json.loads(value)
                log.info("cache_read outcome=hit duration_ms=%.2f", (time.perf_counter()-start)*1000)
                return result
        except (RedisError, ValueError, TypeError):
            # Do not log exceptions, keys, identifiers, URLs, passwords or values.
            log.warning("cache_read outcome=unavailable")
            available = False
    result = jsonable_encoder(loader())
    if available:
        try:
            client.set(key, json.dumps(result), ex=ttl)
        except RedisError:
            log.warning("cache_write outcome=unavailable")
    log.info("cache_read outcome=miss duration_ms=%.2f", (time.perf_counter()-start)*1000)
    return result
